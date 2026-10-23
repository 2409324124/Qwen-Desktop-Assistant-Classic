import json
from pathlib import Path
from transformers import AutoTokenizer
from answer_audit import reliable_last_boxed_content, last_boxed_content, looks_truncated, response_text
from lm_eval.tasks.hendrycks_math.utils import is_equiv
root = Path(__file__).parent
base = '/home/miku/.cache/huggingface/hub/models--Qwen--Qwen3-4B-Instruct-2507/snapshots/cdbee75f17c01a7cc42f958dc650907174af0554'
tokenizer = AutoTokenizer.from_pretrained(base, local_files_only=True)
report = {}
for task in ('gsm8k_cot_zeroshot', 'math500_v52', 'aime25'):
    runs = {}
    for model in ('base', 'checkpoint-30'):
        paths = list((root/'results'/task/model).rglob('samples_*.jsonl'))
        if not paths: break
        rows = [json.loads(line) for line in paths[0].read_text().splitlines()]
        rows = [r for r in rows if r.get('filter') == ('flexible-extract' if task.startswith('gsm') else 'none')]
        runs[model] = {r['doc_id']: r for r in rows}
    if len(runs) != 2: continue
    a, b = runs['base'], runs['checkpoint-30']
    assert a.keys() == b.keys() and all(a[k]['doc'] == b[k]['doc'] and a[k]['arguments'] == b[k]['arguments'] for k in a)
    entry = {'n': len(a), 'base_only_correct': [k for k in a if a[k]['exact_match'] and not b[k]['exact_match']], 'sft_only_correct': [k for k in a if b[k]['exact_match'] and not a[k]['exact_match']]}
    for model, rows in runs.items():
        texts = [response_text(r) for r in rows.values()]
        lengths = [len(ids) for ids in tokenizer(texts, add_special_tokens=False)['input_ids']]
        entry[model] = {'correct': sum(r['exact_match'] for r in rows.values()), 'no_reliable_final_box': sum(reliable_last_boxed_content(s) is None for s in texts), 'suspected_truncation': sum(looks_truncated(s) for s in texts), 'output_at_4096_tokens': sum(n >= 4096 for n in lengths), 'max_output_tokens': max(lengths), 'invalid_filter': sum('[invalid]' in str(r.get('filtered_resps')) for r in rows.values())}
        if task == 'math500_v52':
            entry[model]['last_box_match_diagnostic'] = sum(is_equiv(last_boxed_content(response_text(r)), str(r['doc']['answer'])) for r in rows.values())
            entry[model]['no_complete_box'] = sum(last_boxed_content(s) is None for s in texts)
    report[task] = entry
(root/'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
