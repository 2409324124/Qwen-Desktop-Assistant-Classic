"""Review every frozen split from input/gold evidence, with no prediction access."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
from pathlib import Path

from training.clean_v5_training import (SPLITS, leakage_report, load_jsonl, review_training,
                                       sha_file, summarize, write_json, write_rows)
from training.prepare_dataset import _group_keys
from training.evaluate_latex import is_output_protocol_compliant

VERSION = 'v5.2-reviewed-all-splits'


def isolate_components(splits):
    """Keep frozen split ownership; quarantine every side of a cross-split component."""
    entries = sorted(((split, row) for split, rows in splits.items() for row in rows),
                     key=lambda item:(item[0], item[1]['metadata']['source_id']))
    parent = list(range(len(entries)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i

    owners, edges = {}, []
    for i, (split, row) in enumerate(entries):
        meta = row['metadata']
        keys = _group_keys(row) | {('original_group', meta['formula_group_id'])}
        for kind, value in sorted(keys):
            key = (kind, value)
            if key in owners:
                j = owners[key]; parent[find(i)] = find(j)
                edges.append({'left_source_id':entries[j][1]['metadata']['source_id'],
                              'right_source_id':meta['source_id'],'basis':kind,'value':value})
            else:
                owners[key] = i
    components = defaultdict(list)
    for i, item in enumerate(entries): components[find(i)].append(item)
    kept = {split:[] for split in splits}; held = []; manifest = []
    for members in sorted(components.values(), key=lambda group:min(r['metadata']['source_id'] for _,r in group)):
        original_groups = sorted({r['metadata']['formula_group_id'] for _,r in members})
        split_names = sorted({split for split,_ in members})
        group_id = original_groups[0] if len(original_groups)==1 else 'formula:'+hashlib.sha256('\n'.join(original_groups).encode()).hexdigest()[:20]
        crossing = len(split_names)>1
        for split,row in members:
            meta = row['metadata']
            meta['original_formula_group_id'] = meta['formula_group_id']
            meta['formula_group_id'] = group_id
            if crossing:
                meta.update(evaluation_role='quarantine',review_status='quarantine')
                meta.setdefault('review_validation_reasons',[]).append('cross_split_connected_component')
                held.append(row)
            else:
                kept[split].append(row)
        manifest.append({'formula_group_id':group_id,'original_formula_group_ids':original_groups,
                         'original_splits':split_names,'status':'quarantine' if crossing else 'retained',
                         'records':len(members),'source_ids':sorted(r['metadata']['source_id'] for _,r in members),
                         'formula_names':sorted({r['metadata']['formula_name'] for _,r in members})})
    return kept, held, manifest, edges


def build(source_dir, reviews_dir, out_dir):
    source_dir, reviews_dir, out_dir = map(Path,(source_dir,reviews_dir,out_dir))
    if out_dir.exists(): raise ValueError('Refusing to overwrite an existing dataset')
    if source_dir.resolve() in out_dir.resolve().parents or reviews_dir.resolve() in out_dir.resolve().parents:
        raise ValueError('Export must be separate from frozen inputs/reviews')
    originals = {split:load_jsonl(source_dir/name) for split,name in SPLITS.items()}
    accepted, held, audits, duplicate_counts = {}, [], [], {}
    for split, rows in originals.items():
        if not rows: raise ValueError(f'Empty source split: {split}')
        if any(r['metadata'].get('split') != split for r in rows):
            raise ValueError(f'Frozen membership mismatch: {split}')
        review_path = reviews_dir/f'v5_{split}_review.jsonl'
        decisions = load_jsonl(review_path)
        if split!='train' and any(d.get('review_basis')!='input_and_original_label_only' for d in decisions):
            raise ValueError('Holdout review must declare input/gold-only evidence')
        ready, quarantine, audit, duplicates = review_training(rows,decisions,[])
        accepted[split] = ready; held.extend(quarantine); duplicate_counts[split]=duplicates
        for d in audit: d['split']=split
        audits.extend(audit)
    accepted, crossing, components, edges = isolate_components(accepted)
    held.extend(crossing)
    audit_by_id = {(d['split'],d['source_id']):d for d in audits}
    for row in crossing:
        m=row['metadata']; d=audit_by_id[(m['split'],m['source_id'])]
        d['final_action']='quarantine'; d['validation_reasons']=m['review_validation_reasons']
        for sid in m.get('duplicate_source_ids',[]):
            if (m['split'],sid) in audit_by_id:
                duplicate=audit_by_id[(m['split'],sid)];duplicate['final_action']='quarantine'
                duplicate['validation_reasons']=m['review_validation_reasons']
    for rows in [*accepted.values(),held]:
        for r in rows:
            r['metadata'].update(data_version=VERSION,review_rule_version=VERSION,
                                 review_basis='input_and_original_label_only')
    for split in accepted:
        accepted[split].sort(key=lambda r:r['metadata']['source_id'])
    held.sort(key=lambda r:(r['metadata']['split'],r['metadata']['source_id']))
    leakage=leakage_report([accepted[s] for s in SPLITS])
    # An empty split is a failed usable dataset, not a reason to move examples.
    if any(not rows for rows in accepted.values()):
        raise ValueError('Isolation left an empty split; manual review required, no automatic reassignment')
    for split, rows in accepted.items():
        invalid = [r['metadata']['source_id'] for r in rows if not is_output_protocol_compliant(r['output'])]
        if invalid: raise ValueError(f'Gold output protocol violations in {split}: {invalid}')
    out_dir.mkdir(parents=True)
    for split, filename in SPLITS.items(): write_rows(out_dir/filename,accepted[split])
    (out_dir/'latex_formula_eval.jsonl').write_bytes((out_dir/SPLITS['eval']).read_bytes())
    (out_dir/'dataset_info.json').write_bytes((source_dir/'dataset_info.json').read_bytes())
    write_rows(out_dir/'latex_formula_quarantine.jsonl',held)
    write_rows(out_dir/'review_manifest.jsonl',audits)
    write_rows(out_dir/'group_manifest.jsonl',components)
    write_rows(out_dir/'group_connections.jsonl',edges)
    summary = {'data_version':VERSION,'parent_data_version':'v5',
               'review_scope':'All frozen source rows; labels reviewed from input/gold evidence, no prediction files read by this pipeline',
               'label_protocol_check':{s:{'checked':len(rows),'violations':0} for s,rows in accepted.items()},
               'selection_policy':'Retain original split ownership; quarantine all sides of cross-split connected components; never reallocate',
               'splits':{s:{'input_records':len(originals[s]),'accepted':summarize(accepted[s]),
                            'final_actions':dict(Counter(d['final_action'] for d in audits if d['split']==s)),
                            'group_count':len({r['metadata']['formula_group_id'] for r in accepted[s]}),
                            'duplicates_merged':duplicate_counts[s]} for s in SPLITS},
               'quarantine':summarize(held),'cross_split_components_quarantined':sum(c['status']=='quarantine' for c in components),
               'leakage':leakage,'source_files_sha256':{n:sha_file(source_dir/n) for n in (*SPLITS.values(),'dataset_info.json')},
               'review_files_sha256':{f'v5_{s}_review.jsonl':sha_file(reviews_dir/f'v5_{s}_review.jsonl') for s in SPLITS},
               'code_sha256':{n:sha_file(Path(__file__).with_name(n)) for n in ('clean_v5_holdouts.py','clean_v5_training.py','formula_grouping.py','formula_structure.py','latex_semantics.py','evaluate_latex.py')},
               'export_files_sha256':{p.name:sha_file(p) for p in sorted(out_dir.iterdir()) if p.is_file()}}
    write_json(out_dir/'dataset_summary.json',summary)
    return summary


if __name__=='__main__':
    import json
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir',type=Path,default=Path('training/reviews/v5_source'))
    parser.add_argument('--reviews-dir',type=Path,default=Path('training/reviews'))
    parser.add_argument('--out-dir',type=Path,default=Path('training/data/v5.2'))
    args=parser.parse_args();print(json.dumps(build(args.source_dir,args.reviews_dir,args.out_dir),ensure_ascii=False,indent=2))
