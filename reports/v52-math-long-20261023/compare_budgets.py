import json
from pathlib import Path
root = Path(__file__).parent
old = root.parent/'v52-math-20261023'
summary = {}
for task in ('aime25', 'math500_v52'):
    for model in ('base', 'checkpoint-30'):
        paths = [list((p/'results'/task/model).rglob('samples_*.jsonl')) for p in (old, root)]
        if not all(paths): continue
        a, b = [{r['doc_id']: r for r in map(json.loads, files[0].read_text().splitlines())} for files in paths]
        assert a.keys() == b.keys()
        for k in a:
            assert a[k]['doc'] == b[k]['doc']
            x, y = a[k]['arguments']['gen_args_0'], b[k]['arguments']['gen_args_0']
            assert x['arg_0'] == y['arg_0']
            assert {k:v for k,v in x['arg_1'].items() if k != 'max_gen_toks'} == {k:v for k,v in y['arg_1'].items() if k != 'max_gen_toks'}
        summary[f'{task}/{model}'] = {'n':len(a), '4k_correct':sum(r['exact_match'] for r in a.values()), 'long_correct':sum(r['exact_match'] for r in b.values()), 'gained':[k for k in a if not a[k]['exact_match'] and b[k]['exact_match']], 'lost':[k for k in a if a[k]['exact_match'] and not b[k]['exact_match']]}
(root/'budget-comparison.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary, indent=2))
