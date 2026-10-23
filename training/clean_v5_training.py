"""Apply an exhaustive, source-bound review without rewriting frozen v5 splits."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from training.formula_grouping import prepare_grouping_records
from training.prepare_dataset import _group_keys, dedupe_records, load_jsonl, summarize
from training.review_dataset import normalized_text

VERSION = 'v5.1-reviewed-training'
SPLITS = {'train': 'latex_formula_train.jsonl', 'eval': 'latex_formula_eval_clean.jsonl',
          'test': 'latex_formula_test.jsonl'}


def sha_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def sha_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n', encoding='utf-8')


def write_rows(path, rows):
    path.write_text(''.join(json.dumps(r, ensure_ascii=False, sort_keys=True)+'\n' for r in rows), encoding='utf-8')


def review_training(rows, decisions, heldout):
    """Require exactly one bound decision per row; failed checks quarantine, never accept."""
    if len(rows) != len(decisions):
        raise ValueError('Review must cover every training record exactly once')
    by_id = {}
    for d in decisions:
        if d['source_id'] in by_id:
            raise ValueError('Duplicate review source_id')
        by_id[d['source_id']] = d
    if set(by_id) != {r['metadata']['source_id'] for r in rows}:
        raise ValueError('Review source IDs do not match the training set')
    accepted, quarantine, audit = [], [], []
    for number, original in enumerate(rows, 1):
        sid = original['metadata']['source_id']; d = by_id[sid]
        if d['row'] != number or any(d[k+'_sha256'] != sha_text(original[k]) for k in ('input', 'output')):
            raise ValueError(f'Stale or misaligned review: {sid}')
        if d['decision'] not in {'keep', 'repair', 'quarantine'} or not str(d.get('reason', '')).strip():
            raise ValueError(f'Missing review decision/evidence: {sid}')
        if d['decision'] == 'repair' and (not d.get('output') or d['output'] == original['output']):
            raise ValueError(f'Repair must provide a different complete target: {sid}')
        if d['decision'] != 'repair' and d.get('output') not in (None, original['output']):
            raise ValueError(f'Only a repair may change the target: {sid}')
        row = deepcopy(original); meta = row['metadata']
        entry = deepcopy(d); entry['final_action'] = d['decision']; entry['validation_reasons'] = []
        meta.update(data_version=VERSION, parent_data_version='v5',
                    reviewed_v5_output=original['output'], review_status=d['decision'],
                    review_reason=d['reason'], review_rule_version=VERSION)
        if d['decision'] == 'repair':
            row['output'] = d['output']; row['canonical_output'] = d['output']
        if d['decision'] != 'quarantine':
            # Recompute repaired identities while retaining every historical edge.
            ready, held, diagnostic = prepare_grouping_records([row])
            if held or diagnostic:
                entry['final_action'] = 'quarantine'
                entry['validation_reasons'].append('revised_structure_unverified')
                entry['structure_diagnostics'] = held[0]['metadata'].get('grouping_reasons', []) if held else ['diagnostic_only']
            else:
                fresh = ready[0]['metadata']
                for key in ('structural_signatures', 'template_signatures'):
                    meta[key] = sorted(set(meta.get(key, [])) | set(fresh[key]))
                for key in ('structural_signature', 'template_signature', 'signature_evidence'):
                    meta[key] = fresh[key]
        meta['review_status'] = entry['final_action']
        meta['review_validation_reasons'] = entry['validation_reasons']
        if entry['final_action'] == 'quarantine':
            meta['evaluation_role'] = 'quarantine'; quarantine.append(row)
        else:
            accepted.append(row)
        audit.append(entry)

    audit_by_id = {d['source_id']: d for d in audit}
    targets = defaultdict(set)
    for row in accepted:
        targets[normalized_text(row['input'])].add(normalized_text(row['output']))
    conflicts = {x for x, outputs in targets.items() if len(outputs) > 1}
    heldout_keys = {k for split in heldout for row in split for k in _group_keys(row)}
    unsafe_groups = {r['metadata']['formula_group_id'] for r in accepted if _group_keys(r) & heldout_keys}
    # Conservatively remove a whole original training component if a repair
    # adds a relationship to a frozen development/test component.
    kept = []
    for row in accepted:
        reasons = []
        if normalized_text(row['input']) in conflicts: reasons.append('conflicting_targets_after_review')
        if row['metadata']['formula_group_id'] in unsafe_groups: reasons.append('component_connects_to_frozen_holdout')
        if reasons:
            entry = audit_by_id[row['metadata']['source_id']]
            entry['final_action'] = 'quarantine'; entry['validation_reasons'].extend(reasons)
            row['metadata'].update(review_status='quarantine', evaluation_role='quarantine', review_validation_reasons=reasons)
            quarantine.append(row)
        else:
            kept.append(row)
    kept, duplicates = dedupe_records(kept)
    for row in kept:
        for sid in row['metadata'].get('duplicate_source_ids', []):
            if sid in audit_by_id and sid != row['metadata']['source_id']:
                audit_by_id[sid]['exported_as_duplicate_of'] = row['metadata']['source_id']
    return kept, sorted(quarantine, key=lambda r:r['metadata']['source_id']), audit, duplicates


def leakage_report(splits):
    keys = [{k for row in split for k in _group_keys(row)} |
            {('group', row['metadata']['formula_group_id']) for row in split} for split in splits]
    labels = ('input', 'equation', 'source', 'family', 'lineage', 'structure', 'template', 'near_family', 'group')
    result = {label+'_overlap': sum(len({v for k,v in keys[a] & keys[b] if k == label})
              for a,b in ((0,1),(0,2),(1,2))) for label in labels}
    if any(result.values()): raise ValueError(f'Cross-split leakage: {result}')
    return result


def build(source_dir, review_file, out_dir):
    source_dir, review_file, out_dir = map(Path, (source_dir, review_file, out_dir))
    if out_dir.exists(): raise ValueError('Refusing to overwrite an existing export directory')
    if source_dir.resolve() in out_dir.resolve().parents: raise ValueError('Export must be separate from frozen sources')
    splits = {s:load_jsonl(source_dir/name) for s,name in SPLITS.items()}
    train, held, audit, duplicates = review_training(splits['train'], load_jsonl(review_file), [splits['eval'], splits['test']])
    leakage = leakage_report([train, splits['eval'], splits['test']])
    if not train: raise ValueError('No verified training records remain')
    out_dir.mkdir(parents=True)
    write_rows(out_dir/SPLITS['train'], train)
    write_rows(out_dir/'latex_formula_quarantine.jsonl', held)
    write_rows(out_dir/'review_manifest.jsonl', audit)
    # These retain their v5 labels/version; only the training set was reviewed.
    for split in ('eval', 'test'):
        (out_dir/SPLITS[split]).write_bytes((source_dir/SPLITS[split]).read_bytes())
    (out_dir/'dataset_info.json').write_bytes((source_dir/'dataset_info.json').read_bytes())
    if (source_dir/'latex_formula_eval.jsonl').exists():
        (out_dir/'latex_formula_eval.jsonl').write_bytes((source_dir/'latex_formula_eval.jsonl').read_bytes())
    groups = defaultdict(list)
    for row in train: groups[row['metadata']['formula_group_id']].append(row)
    write_rows(out_dir/'group_manifest.jsonl', [{'formula_group_id':key,'split':'train','records':len(rows),
               'formula_names':sorted({r['metadata']['formula_name'] for r in rows})} for key,rows in sorted(groups.items())])
    summary = {'data_version':VERSION,'parent_data_version':'v5','review_scope':'All training records; frozen development/test copied unchanged, not certified clean',
               'input_records':len(splits['train']), 'review_decisions':dict(Counter(d['decision'] for d in audit)),
               'final_actions':dict(Counter(d['final_action'] for d in audit)), 'duplicates_merged':duplicates,
               'train':summarize(train),'quarantine':summarize(held),'group_count':len(groups),'leakage':leakage,
               'source_files_sha256':{name:sha_file(source_dir/name) for name in SPLITS.values()},
               'review_sha256':sha_file(review_file),
               'review_code_sha256':{name:sha_file(Path(__file__).with_name(name)) for name in
                   ('clean_v5_training.py','formula_grouping.py','formula_structure.py','latex_semantics.py')},
               'export_files_sha256':{p.name:sha_file(p) for p in sorted(out_dir.iterdir()) if p.is_file()}}
    write_json(out_dir/'dataset_summary.json', summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, default=Path('training/data/v5'))
    parser.add_argument('--review', type=Path, default=Path('training/reviews/v5_train_review.jsonl'))
    parser.add_argument('--out-dir', type=Path, default=Path('training/data/v5.1'))
    args = parser.parse_args(); print(json.dumps(build(args.source_dir,args.review,args.out_dir),ensure_ascii=False,indent=2))


if __name__ == '__main__': main()
