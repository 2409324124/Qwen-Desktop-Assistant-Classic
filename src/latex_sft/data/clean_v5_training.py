"""Apply an exhaustive, source-bound review without rewriting frozen v5 splits."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from .io import load_jsonl, sha_text, sha_file, write_json, write_rows
from .provenance import EXECUTION_PROTOCOL_VERSION, current_source_path, current_code_hashes
from .records import summarize
from .review_decisions import review_decisions, leakage_report
from .schema import SPLITS

VERSION = 'v5.1-reviewed-training'
# Compatibility for existing callers and tests.
review_training = review_decisions


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
    summary = {'execution_protocol_version':EXECUTION_PROTOCOL_VERSION, 'current_code_sha256':current_code_hashes(), 'data_version':VERSION,'parent_data_version':'v5','review_scope':'All training records; frozen development/test copied unchanged, not certified clean',
               'input_records':len(splits['train']), 'review_decisions':dict(Counter(d['decision'] for d in audit)),
               'final_actions':dict(Counter(d['final_action'] for d in audit)), 'duplicates_merged':duplicates,
               'train':summarize(train),'quarantine':summarize(held),'group_count':len(groups),'leakage':leakage,
               'source_files_sha256':{name:sha_file(source_dir/name) for name in SPLITS.values()},
               'review_sha256':sha_file(review_file),
               'review_code_sha256':{name:sha_file(current_source_path(name)) for name in
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
