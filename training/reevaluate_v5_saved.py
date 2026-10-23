"""CPU-only paired reassessment of frozen v5 generations; never runs inference."""
import argparse
import hashlib
import json
from pathlib import Path

from training.clean_v5_training import load_jsonl, sha_file, write_json, write_rows
from training.evaluate_latex import evaluate_pairs
from training.latex_semantics import compare_latex_math_only


def metric_pair(rows):
    result = evaluate_pairs(rows)
    return {key:result[key] for key in ('raw_metrics', 'postprocessed_metrics')}


def reassess(fixtures, output):
    fixtures, output = Path(fixtures), Path(output)
    if output.exists(): raise ValueError('Refusing to overwrite an existing assessment')
    manifest = json.loads((fixtures/'manifest.json').read_text())
    for name, expected in manifest['files_sha256'].items():
        path = (fixtures/name).resolve()
        if not path.is_relative_to(fixtures.resolve()) or sha_file(path) != expected:
            raise ValueError(f'Frozen fixture mismatch: {name}')
    prior = json.loads((fixtures/'previous-scoring.json').read_text())
    exclusions = load_jsonl(fixtures/'development-exclusions.jsonl')
    excluded = {r['source_id']:r for r in exclusions}
    if len(excluded) != len(exclusions): raise ValueError('Duplicate exclusion ID')
    common = None; results = {}; changes = []
    for model in sorted(prior):
        rows = load_jsonl(fixtures/f'{model}-predictions.jsonl')
        identities = {r['metadata']['source_id']:(r['input'],r['expected']) for r in rows}
        if len(identities) != len(rows): raise ValueError('Duplicate prediction ID')
        if common is None: common = identities
        if identities != common: raise ValueError('Models do not share identical inputs and gold labels')
        if not set(excluded) <= identities.keys(): raise ValueError('Exclusions absent from predictions')
        for sid, exclusion in excluded.items():
            if identities[sid] != (exclusion['input'],exclusion['expected']):
                raise ValueError('Exclusion input/label mismatch')
        old = {r['source_id']:r['math_match'] for r in prior[model]['judgments']}
        if set(old) != identities.keys(): raise ValueError('Previous judgments do not cover all rows')
        for row in rows:
            m=row['metadata']; sid=m['source_id']
            now=compare_latex_math_only(row['expected'],row['prediction'],formula_name=m['formula_name'],input_text=row['input'])
            if now.math_match != old[sid]:
                changes.append({'model':model,'source_id':sid,'input':row['input'],'expected':row['expected'],
                    'prediction':row['prediction'],'old_math_match':old[sid],'new_math_match':now.math_match,
                    'reason':now.reason,'change_type':'scorer_only_same_generation_same_label',
                    'excluded_from_supplementary_subset':sid in excluded})
        reviewed = [r for r in rows if r['metadata']['source_id'] not in excluded]
        results[model] = {'old_frozen_64':prior[model]['metrics'],'new_same_labels_64':metric_pair(rows),
                          'new_reviewed_subset_57':metric_pair(reviewed),
                          'truncated':sum(bool(r.get('hit_token_limit')) for r in rows)}
    output.mkdir(parents=True)
    summary={'protocol':'Retrospective scorer-only reassessment; predictions and gold unchanged. Identical seven development exclusions are supplementary post-hoc analysis. Not a new clean-training result or final-test result.',
             'unavailable':['checkpoint-99 per-example predictions','training probe/challenge predictions','final test predictions'],
             'fixture_manifest_sha256':sha_file(fixtures/'manifest.json'),
             'scorer_sha256':sha_file(Path(__file__).with_name('latex_semantics.py')),
             'models':results,'changed_judgments':len(changes)}
    write_json(output/'summary.json',summary); write_rows(output/'changed_judgments.jsonl',changes)
    lines=['# v5 已有预测离线复评','',summary['protocol'],'',
           '| 模型 | 原64条 micro / macro | 修复评分64条 micro / macro | 排除7条问题标签后57条 micro / macro |',
           '|---|---|---|---|']
    for model, scores in results.items():
        values=[]
        for stage in ('old_frozen_64','new_same_labels_64','new_reviewed_subset_57'):
            m=scores[stage]['postprocessed_metrics'];values.append(f"{m['micro_math_accuracy']:.2%} / {m['macro_math_accuracy']:.2%}")
        lines.append('| '+model+' | '+' | '.join(values)+' |')
    lines += ['',f'共 {len(changes)} 个逐模型判定变化，详见 changed_judgments.jsonl。完整 JSON 同时报告 raw/postprocessed、组指标、格式合规、解析覆盖及未验证数。',
              '', 'cp99 仅保留历史汇总，没有逐条预测，故不伪造新评分。开发集仅4组且分布偏斜；补充排除不能消除所有标签/评分限制。清洗后的训练数据尚未训练，以上涨分只来自评分修复。']
    (output/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures',type=Path,default=Path('training/reviews/v5_predictions'))
    parser.add_argument('--output',type=Path,default=Path('reports/v5-offline-reviewed'))
    args=parser.parse_args(); result=reassess(args.fixtures,args.output)
    print(json.dumps({'models':list(result['models']),'changed_judgments':result['changed_judgments']},ensure_ascii=False))
