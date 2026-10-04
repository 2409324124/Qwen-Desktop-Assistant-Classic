import argparse
import json
import hashlib
from copy import deepcopy
import random
from collections import defaultdict, Counter
from pathlib import Path
from typing import Any

from training.dataset_quality import load_quality_overrides
from training.latex_postprocess import postprocess_latex
from training.latex_semantics import canonicalize_latex_faithful
from training.prompts import SYSTEM_PROMPT
from training.review_dataset import review_records, normalized_text
from training.formula_grouping import prepare_grouping_records, GROUPING_VERSION

DATA_VERSION = "v5"


DEFAULT_SOURCES: tuple[tuple[str, str], ...] = (
    ("clean", "data/frozen/phase1/train_clean_v1_500.jsonl"),
    ("noisy", "data/frozen/phase1/train_noisy_v4_900.jsonl"),
    ("hard", "data/frozen/phase1/train_hard_v5_600.jsonl"),
)

TRAIN_ONLY_SOURCES: tuple[tuple[str, str], ...] = (
    ("targeted", "training/targeted_v3_train.jsonl"),
)


class DatasetValidationError(ValueError):
    pass


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise DatasetValidationError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(payload, dict):
                raise DatasetValidationError(f"{path}:{line_number}: record must be a JSON object")
            records.append(payload)
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def validate_records(records: list[dict[str, Any]], source_name: str) -> None:
    seen_pairs: set[tuple[str, str]] = set()
    for index, record in enumerate(records, 1):
        for key in ("instruction", "input", "output"):
            value = record.get(key)
            if not isinstance(value, str) or not value.strip():
                raise DatasetValidationError(f"{source_name}:{index}: missing non-empty '{key}'")

        metadata = record.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            raise DatasetValidationError(f"{source_name}:{index}: metadata must be an object when present")

        pair = (record["input"].strip(), record["output"].strip())
        seen_pairs.add(pair)


def load_sources(repo_root: Path, sources: tuple[tuple[str, str], ...] = DEFAULT_SOURCES) -> list[dict[str, Any]]:
    combined: list[dict[str, Any]] = []
    for layer, relative_path in sources:
        path = repo_root / relative_path
        records = load_jsonl(path)
        validate_records(records, relative_path)
        physical_lines = [i for i,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1) if line.strip()]
        for index, record in zip(physical_lines, records):
            # Cached historical canonical outputs may have lost fonts or types.
            # Rebuild from the source label; preserve the cache only as provenance.
            canonical_output = canonicalize_latex_faithful(postprocess_latex(record['output']))
            cloned = dict(record)
            cloned["instruction"] = SYSTEM_PROMPT
            cloned["output"] = canonical_output
            cloned["canonical_output"] = canonical_output
            metadata = dict(cloned.get("metadata") or {})
            metadata["original_output"] = record["output"]
            metadata["original_canonical_output"] = record.get("canonical_output")
            metadata["source_id"] = f"{relative_path}:{index}"
            metadata["source_line"] = index
            metadata["source_sha256"] = hashlib.sha256(json.dumps(record, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            metadata["dataset_layer"] = layer
            metadata["source_file"] = Path(relative_path).name
            metadata["source_path"] = relative_path
            cloned["metadata"] = metadata
            combined.append(cloned)
    return combined


def _lineage_rows(row: dict[str, Any]) -> list[dict[str, Any]]:
    """All pre-deduplication source records, including their original grouping edges."""
    return [row, *row.get('metadata', {}).get('source_records', [])]


def _group_keys(row: dict[str, Any]) -> set[tuple[str, str]]:
    keys = set()
    for source in _lineage_rows(row):
        meta = source.get('metadata', {})
        # Ancestor inputs and descendants' source_input share an identity.
        for value in (source.get('input'), meta.get('source_input')):
            if value: keys.add(('input', normalized_text(value)))
        # A repair cannot sever the connection to the source's original equation.
        for value in (source.get('output'), meta.get('original_output')):
            if value: keys.add(('equation', normalized_text(value)))
        for signature in meta.get('structural_signatures', []): keys.add(('structure', signature))
        for signature in meta.get('template_signatures', []): keys.add(('template', signature))
        if meta.get('near_family_id'): keys.add(('near_family',meta['near_family_id']))
        for label, field in (('family', 'formula_name'), ('lineage', 'formula_id')):
            if meta.get(field): keys.add((label, str(meta[field])))
        for source_id in [meta.get('source_id'), *meta.get('duplicate_source_ids', [])]:
            if source_id: keys.add(('source', source_id))
    return keys


def dedupe_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    seen: dict[tuple[str, str], dict[str, Any]] = {}
    deduped: list[dict[str, Any]] = []
    duplicates = 0
    for record in records:
        key = (normalized_text(record["input"]), normalized_text(record["output"]))
        if key in seen:
            duplicates += 1
            meta = seen[key].setdefault('metadata', {})
            for source in _lineage_rows(record):
                snapshot = deepcopy(source)
                snapshot.setdefault('metadata', {}).pop('source_records', None)
                meta.setdefault('source_records', []).append(snapshot)
                source_id = snapshot['metadata'].get('source_id')
                if source_id and source_id != meta.get('source_id'):
                    ids = meta.setdefault('duplicate_source_ids', [])
                    if source_id not in ids: ids.append(source_id)
            continue
        clone = deepcopy(record)
        seen[key] = clone
        deduped.append(clone)
    return deduped, duplicates


def split_grouped_records(records, *, eval_ratio=0.1, test_ratio=0.1, seed=42, connections=None):
    if not (0 < eval_ratio < 1 and 0 <= test_ratio < 1 and eval_ratio + test_ratio < 1):
        raise ValueError('eval/test ratios must leave a positive train fraction')
    parent = list(range(len(records)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    def union(a,b):
        parent[find(b)] = find(a)
    seen = {}
    for i in sorted(range(len(records)),key=lambda i:records[i]['metadata']['source_id']):
        row=records[i]
        for key in sorted(_group_keys(row)):
            if key in seen:
                anchor=seen[key]
                union(i,anchor)
                if connections is not None:
                    connections.append({'left_source_id':records[anchor]['metadata']['source_id'],
                                        'right_source_id':row['metadata']['source_id'],
                                        'basis':key[0],'identity':key[1]})
            else: seen[key] = i
        if connections is not None:
            for source in row['metadata'].get('source_records',[]):
                connections.append({'left_source_id':row['metadata']['source_id'],
                                    'right_source_id':source['metadata'].get('source_id'),
                                    'basis':'duplicate_input_output',
                                    'identity':hashlib.sha256((normalized_text(row['input'])+'\0'+normalized_text(row['output'])).encode()).hexdigest()})
    groups = defaultdict(list)
    for i, row in enumerate(records): groups[find(i)].append(row)
    grouped=[]
    for group in groups.values():
        identities=sorted({f'{kind}:{value}' for row in group for kind,value in _group_keys(row)
                           if kind in {'family','near_family'}})
        if not identities:
            identities=sorted({f'{kind}:{value}' for row in group for kind,value in _group_keys(row)})
        group_id='formula:'+hashlib.sha256('\n'.join(identities).encode()).hexdigest()[:20]
        for row in group:
            for source in _lineage_rows(row):source['metadata']['formula_group_id']=group_id
        grouped.append(sorted(group,key=lambda r:r['metadata']['source_id']))
    rng=random.Random(seed)
    grouped.sort(key=lambda g:g[0]['metadata']['formula_group_id']); rng.shuffle(grouped)
    n=len(grouped); dev=round(n*eval_ratio); test=round(n*test_ratio)
    if n>=3:
        dev=max(1,dev); test=max(1,test) if test_ratio else 0
    while dev+test>=n and dev+test:
        if test>=dev:test-=1
        else:dev-=1
    splits=[[],[],[]]; group_counts=[0,0,0]
    for index,group in enumerate(grouped):
        split=1 if index<dev else 2 if index<dev+test else 0
        for row in group:row['metadata']['split']=('train','eval','test')[split]
        splits[split].extend(group);group_counts[split]+=1
    for split in splits:rng.shuffle(split)
    leakage={}
    for label in ('input','equation','source','family','lineage','structure','template','near_family'):
        sets=[{value for row in split for kind,value in _group_keys(row) if kind==label} for split in splits]
        leakage[label+'_overlap']=sum(len(sets[a]&sets[b]) for a,b in ((0,1),(0,2),(1,2)))
    for label,getter in {
        'target':lambda r:[normalized_text(r['output'])],
        'original_target':lambda r:[normalized_text(s['metadata'].get('original_output',s['output'])) for s in _lineage_rows(r)],
        'group':lambda r:[r['metadata']['formula_group_id']],
        'source_input':lambda r:[normalized_text(s['metadata']['source_input']) for s in _lineage_rows(r) if s['metadata'].get('source_input')],
    }.items():
        sets=[{v for row in split for v in getter(row) if v} for split in splits]
        leakage[label+'_overlap']=sum(len(sets[a]&sets[b]) for a,b in ((0,1),(0,2),(1,2)))
    if any(leakage.values()):raise DatasetValidationError(f'cross-split leakage: {leakage}')
    return (*splits,leakage,dict(zip(('train','eval','test'),group_counts)))



def dataset_info() -> dict[str, Any]:
    columns = {"prompt": "input", "response": "output", "system": "instruction"}
    return {
        "latex_formula_train": {
            "file_name": "latex_formula_train.jsonl",
            "formatting": "alpaca",
            "columns": columns,
        },
        "latex_formula_eval": {
            "file_name": "latex_formula_eval.jsonl",
            "formatting": "alpaca",
            "columns": columns,
        },
        "latex_formula_eval_clean": {
            "file_name": "latex_formula_eval_clean.jsonl",
            "formatting": "alpaca",
            "columns": columns,
        },
    }

def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {"total": len(records), "layers": {}, "categories": {}}
    for record in records:
        metadata = record.get("metadata") or {}
        layer = str(metadata.get("dataset_layer") or "unknown")
        category = str(metadata.get("category") or "unknown")
        summary["layers"][layer] = summary["layers"].get(layer, 0) + 1
        summary["categories"][category] = summary["categories"].get(category, 0) + 1
    return summary


def build_datasets(
    repo_root: Path,
    out_dir: Path,
    eval_ratio: float,
    seed: int,
    *,
    sources: tuple[tuple[str, str], ...] = DEFAULT_SOURCES,
    train_only_sources: tuple[tuple[str, str], ...] = TRAIN_ONLY_SOURCES,
    quality_overrides: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    existing_summary=out_dir/'dataset_summary.json'
    if existing_summary.exists():
        existing=json.loads(existing_summary.read_text(encoding='utf-8'))
        if existing.get('data_version')!=DATA_VERSION:
            raise DatasetValidationError('Refusing to overwrite a historical dataset version; select a new output directory')
    elif out_dir.exists() and any(out_dir.glob('latex_formula_*.jsonl')):
        raise DatasetValidationError('Refusing to overwrite unversioned historical dataset files')
    source_records = load_sources(repo_root, sources)
    targeted_records = load_sources(repo_root, train_only_sources) if train_only_sources else []
    all_records = source_records + targeted_records
    overrides_path = repo_root / "training/dataset_quality_overrides.json"
    overrides = load_quality_overrides(overrides_path) if quality_overrides is None else quality_overrides
    # Historical overrides are evidence, not permission to guess missing symbols.
    # Retain reviewed exclusions. Only explicitly written product-rule symbols
    # have an unambiguous replacement independent of the formula name.
    by_selector = {(o['source_file'],o['input'],o['formula_name']):o for o in overrides}
    for row in all_records:
        m = row['metadata']
        o = by_selector.get((m['source_file'],row['input'],m.get('formula_name','')))
        if o and o['action'] == 'exclude':
            m['quality_override_action'] = 'exclude'
            m['quality_override_reason'] = o.get('reason','')
        elif o and o['action'] == 'replace_output' and row['input'] == "Prod rule: (fg)' = f'g + fg'":
            m['reviewed_explicit_replacement'] = o['output']
    source_artifacts_sha256 = {
        path: hashlib.sha256((repo_root / path).read_bytes()).hexdigest()
        for _, path in (*sources, *train_only_sources)
    }
    if quality_overrides is None and overrides_path.exists():
        source_artifacts_sha256['training/dataset_quality_overrides.json'] = hashlib.sha256(overrides_path.read_bytes()).hexdigest()
    code_root = Path(__file__).resolve().parents[1]
    code_paths = ('training/prepare_dataset.py', 'training/review_dataset.py',
                  'training/latex_postprocess.py', 'training/latex_semantics.py', 'training/evaluate_latex.py', 'training/prompts.py',
                  'training/dataset_quality.py', 'training/canonicalize_dataset.py',
                  'training/formula_grouping.py','training/formula_structure.py','training/formula_families.json',
                  'tools/data_generation/data_builder.py', 'tools/data_generation/noisy_builder.py',
                  'tools/data_generation/hard_builder.py', 'tools/data_generation/mine_sympy.py')
    source_code_sha256 = {path: hashlib.sha256((code_root / path).read_bytes()).hexdigest()
                          for path in code_paths if (code_root / path).is_file()}
    overrides_sha256 = hashlib.sha256(json.dumps(overrides, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    review_rule_sha256 = hashlib.sha256(json.dumps(
        {'source_code_sha256': source_code_sha256, 'quality_overrides_sha256': overrides_sha256},
        sort_keys=True).encode()).hexdigest()
    quality_records, quarantined_records, manifest = review_records(all_records)
    ready_records, grouping_held, diagnostic_records = prepare_grouping_records(quality_records)
    quarantined_records.extend(grouping_held)
    for row in quarantined_records:
        row['metadata'].update(data_version=DATA_VERSION,evaluation_role='quarantine',grouping_rule_version=GROUPING_VERSION)
        row['metadata'].setdefault('grouping_status','skipped_quality_quarantine')
    grouped_by_source={r['metadata']['source_id']:r for r in ready_records+grouping_held+diagnostic_records}
    for decision in manifest:
        decision['data_version']=DATA_VERSION
        decision['grouping_rule_version']=GROUPING_VERSION
        decision['evaluation_role']='quarantine'
        decision['grouping_status']='skipped_quality_quarantine'
        row=grouped_by_source.get(decision['source_id'])
        if row:
            meta=row['metadata']
            decision['quality_action']=decision['action']
            decision['grouping_status']=meta['grouping_status']
            if meta['grouping_status']=='quarantined':decision['action']='quarantine'
            if meta['grouping_status']=='diagnostic':decision['action']='diagnostic'
            decision['grouping_reasons']=meta['grouping_reasons']
            decision['reasons']=list(dict.fromkeys(decision['reasons']+meta['grouping_reasons']))
            decision['reason']='; '.join(decision['reasons'])
            for field in ('near_family_id','structural_signature','template_signature','grouping_rule_version','family_registry_version','evaluation_role'):
                decision[field]=meta.get(field)
    records, duplicate_count = dedupe_records(ready_records)
    connections=[]
    train, eval_records, test_records, leakage, group_counts = split_grouped_records(
        records, eval_ratio=eval_ratio, test_ratio=0.1, seed=seed,connections=connections)
    grouped=defaultdict(list)
    for row in records:grouped[row['metadata']['formula_group_id']].append(row)
    group_manifest=[]
    for group_id,members in sorted(grouped.items()):
        keys={key for row in members for key in _group_keys(row)}
        group_manifest.append({'formula_group_id':group_id,'split':members[0]['metadata']['split'],
                               'records':len(members),'source_records':sum(len(_lineage_rows(r)) for r in members),
                               'formula_names':sorted(value for kind,value in keys if kind=='family'),
                               'near_family_ids':sorted(value for kind,value in keys if kind=='near_family'),
                               'source_ids':sorted(value for kind,value in keys if kind=='source'),
                               'structural_signatures':sorted(value for kind,value in keys if kind=='structure'),
                               'template_signatures':sorted(value for kind,value in keys if kind=='template')})
    write_jsonl(out_dir/'group_manifest.jsonl',group_manifest)
    write_jsonl(out_dir/'group_connections.jsonl',connections)
    paths = {}
    for name, split in [('train',train),('eval',eval_records),('eval_clean',eval_records),
                        ('test',test_records),('quarantine',quarantined_records),('diagnostic',diagnostic_records)]:
        validate_records(split, name + ' split')
        path = out_dir / f'latex_formula_{name}.jsonl'
        write_jsonl(path,split); paths[name+'_path'] = str(path)
    assignment = {row['metadata']['source_id']:row['metadata']['formula_group_id'] for row in records}
    for row in records:
        for source_id in row['metadata'].get('duplicate_source_ids',[]):
            assignment[source_id] = row['metadata']['formula_group_id']
    source_metadata = {row['metadata']['source_id']: row['metadata'] for row in all_records}
    for decision in manifest:
        decision['formula_group_id'] = assignment.get(decision['source_id'])
        original_meta = source_metadata[decision['source_id']]
        decision['source_record_sha256'] = original_meta.get('source_sha256')
        decision['source_artifact_sha256'] = source_artifacts_sha256.get(original_meta.get('source_path'))
        decision['review_rule_sha256'] = review_rule_sha256
    write_jsonl(out_dir/'review_manifest.jsonl', manifest)
    quality_counts = Counter(d['action'] for d in manifest)
    reason_counts = Counter(reason for d in manifest if d['action']=='quarantine' for reason in d['reasons'])
    summary = {
        'data_version': DATA_VERSION, 'seed': seed,
        'source_artifacts_sha256': source_artifacts_sha256,
        'source_code_sha256': source_code_sha256,
        'quality_overrides_sha256': overrides_sha256,
        'review_rule_sha256': review_rule_sha256,
        'split_policy':'global connected source/structure/template/near-family groups; no category stratification',
        'grouping_rule_version':GROUPING_VERSION,
        'group_manifest':group_manifest,
        'connection_counts':dict(Counter(edge['basis'] for edge in connections)),
        'evaluation_metrics':{'status':'not_run','micro_math_accuracy':None,'macro_math_accuracy':None},
        'evaluation_note':'No new inference: per-sample and equal-per-group metrics require new held-out predictions; v3 exposure is historical.',
        'holdout_limitation':'Few held-out groups do not establish broad generalization; sizes differ and groups are never split to balance records.',
        'requested_group_ratios': {'train':0.9-eval_ratio,'eval':eval_ratio,'test':0.1},
        'historical_model_note': 'v3 trained on old data: these re-splits are not unseen tests for v3',
        'review_limitation': 'Conservative rule checks are not proof of all natural-language/input equivalence; quarantine needs manual review.',
        'source':summarize(source_records), 'targeted_source':summarize(targeted_records),
        'quality_review':dict(quality_counts), 'quarantine_reasons':dict(reason_counts),
        'quality_accepted':summarize(quality_records), 'grouping_accepted':summarize(ready_records),
        'grouping_quarantine':summarize(grouping_held),'diagnostic':summarize(diagnostic_records),
        'quarantine':summarize(quarantined_records),
        'deduped_source':summarize(records), 'duplicate_input_output_pairs_removed':duplicate_count,
        'train':summarize(train), 'eval':summarize(eval_records), 'eval_clean':summarize(eval_records),
        'test':summarize(test_records), 'groups':group_counts, 'leakage':leakage, **paths,
    }
    info = dataset_info()
    info['latex_formula_test'] = {**info['latex_formula_eval'], 'file_name':'latex_formula_test.jsonl'}
    (out_dir/'dataset_info.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report=["# v5 结构与近亲分组审计", "",
            "这里的零重叠仅针对已登记的来源、完整结构签名、参数模板签名和近亲关系，不是对任意数学相似性的证明。", "",
            f"主数据去重后 {len(records)} 条，{len(group_manifest)} 个完整组；独立诊断 {len(diagnostic_records)} 条；隔离待复核 {len(quarantined_records)} 条。",
            f"结构阶段新增隔离 {len(grouping_held)} 条。近亲关系与共享结构采用传递闭包，整组分配，不按类别强行补齐。", "",
            "| 集合 | 组数 | 样本数 |", "| --- | ---: | ---: |"]
    for name,split in [('train',train),('eval',eval_records),('test',test_records)]:
        report.append(f"| {name} | {group_counts[name]} | {len(split)} |")
    report += ["", "## 逐组名单", "", "| 集合 | 组 ID | 样本数 | 近亲组 | 公式家族 |", "| --- | --- | ---: | --- | --- |"]
    for group in group_manifest:
        report.append(f"| {group['split']} | {group['formula_group_id']} | {group['records']} | {', '.join(group['near_family_ids'])} | {', '.join(group['formula_names'])} |")
    report += ["", "## 跨集合检查", "", "| 检查项 | 重叠数 |", "| --- | ---: |"]
    report += [f"| {name} | {count} |" for name,count in sorted(leakage.items())]
    report += ["", "## 结构隔离原因", "", "| 原因 | 记录数（可重叠） |", "| --- | ---: |"]
    report += [f"| {reason} | {count} |" for reason,count in sorted(Counter(reason for row in grouping_held for reason in row['metadata']['grouping_reasons']).items())]
    report += ["", "## 评测与限制", "",
               "本轮未训练、未推理，不生成新的模型分数。未来预测记录必须保留 metadata.formula_group_id；评分同时输出样本平均 micro_math_accuracy、组等权 macro_math_accuracy 和逐组明细。缺少组 ID 的记录不伪造宏平均。",
               "metadata.evaluation_role=diagnostic 的 Symbol Boundary 记录独立统计，不进入主分数。",
               "测试组很少，样本数不均衡；报告两种平均方式也不能消除代表性限制。历史 v3 接触过旧数据，本切分不能成为它的未见测试集。",
               "group_connections.jsonl 记录每次连接的两个来源、连接种类和匹配身份；group_manifest.jsonl 与 review_manifest.jsonl 可追溯最终分配。", ""]
    (out_dir/'group_audit.md').write_text('\n'.join(report),encoding='utf-8')
    export_paths = [Path(path) for path in paths.values()] + [out_dir/'review_manifest.jsonl', out_dir/'dataset_info.json',out_dir/'group_manifest.jsonl',out_dir/'group_connections.jsonl',out_dir/'group_audit.md']
    # The summary carries the hashes and is excluded from its own self-reference.
    summary['export_files_sha256'] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in export_paths}
    (out_dir/'dataset_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare frozen LaTeX correction datasets for LLaMA-Factory.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, default=Path("training/data/v5"))
    parser.add_argument("--eval-ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = args.out_dir if args.out_dir.is_absolute() else args.repo_root / args.out_dir
    summary = build_datasets(args.repo_root, out_dir, args.eval_ratio, args.seed)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
