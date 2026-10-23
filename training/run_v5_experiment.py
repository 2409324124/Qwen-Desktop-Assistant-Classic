"""Version-bound v5 training and development evaluation; execution is opt-in."""
import argparse
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path
import re
import subprocess
import sys

import yaml

from training.evaluate_latex import evaluate_pairs, load_prediction_rows, write_report
from training.prepare_dataset import _group_keys, load_jsonl

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'Qwen/Qwen3-4B-Instruct-2507'
FILES = {split: f'latex_formula_{split}.jsonl' for split in ('train', 'eval_clean', 'test')}
PROFILES = {'sft': 'training/qwen3_4b_lora_sft_v5.yaml', 'smoke': 'training/qwen3_4b_lora_smoke_v5.yaml'}
PROTOCOL_FILES = ('training/run_v5_experiment.py', 'training/run_lora_inference.py',
                  'training/evaluate_latex.py', 'training/latex_semantics.py',
                  'training/latex_postprocess.py', 'training/prompts.py')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def within(root, relative):
    path = (root/relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Artifact escapes its root: {relative}')
    return path


def verify_dataset(root, data_dir):
    summary_path = data_dir/'dataset_summary.json'
    summary = json.loads(summary_path.read_text())
    if summary.get('data_version') != 'v5':
        raise ValueError('Expected audited v5 data')
    for field, base in (('source_artifacts_sha256', root), ('source_code_sha256', root),
                        ('export_files_sha256', data_dir)):
        hashes = summary.get(field)
        if not hashes:
            raise ValueError(f'Missing provenance: {field}')
        for relative, expected in hashes.items():
            path = within(base, relative)
            if not path.is_file() or sha(path) != expected:
                raise ValueError(f'Hash mismatch: {path}')
    if not set((*FILES.values(), 'dataset_info.json')) <= summary['export_files_sha256'].keys():
        raise ValueError('Required training/evaluation exports are not hash-bound')
    info = json.loads((data_dir/'dataset_info.json').read_text())
    for name in ('train', 'eval_clean'):
        if info[f'latex_formula_{name}']['file_name'] != FILES[name]:
            raise ValueError('Unexpected dataset registry mapping')
    keys = []
    for name, filename in FILES.items():
        rows = load_jsonl(data_dir/filename)
        if not rows or len(rows) != summary[name]['total']:
            raise ValueError(f'Empty or inconsistent {name} split')
        for row in rows:
            meta = row.get('metadata', {})
            if (meta.get('data_version') != 'v5' or meta.get('evaluation_role') != 'main'
                    or not meta.get('formula_group_id') or not meta.get('source_id')
                    or meta.get('split') != ('eval' if name == 'eval_clean' else name)):
                raise ValueError(f'Invalid v5 membership in {name}')
        keys.append({key for row in rows for key in _group_keys(row)} |
                    {('group', row['metadata']['formula_group_id']) for row in rows})
    if any(keys[a] & keys[b] for a,b in ((0,1),(0,2),(1,2))):
        raise ValueError('Cross-split leakage detected')
    return {'summary_sha256': sha(summary_path), 'data_version': 'v5',
            'review_rule_sha256': summary['review_rule_sha256'],
            'export_files_sha256': summary['export_files_sha256']}


def environment():
    packages = {}
    for package in ('llamafactory', 'transformers', 'torch', 'peft', 'accelerate', 'datasets'):
        try: packages[package] = version(package)
        except PackageNotFoundError: packages[package] = None
    return {'python': sys.version, 'packages': packages}


def protocol_hashes(root):
    return {name: sha(root/name) for name in PROTOCOL_FILES}


def training_plan(root, profile, run_dir=None):
    config_path = root/PROFILES[profile]
    config = yaml.safe_load(config_path.read_text())
    forbidden = ('adapter_name_or_path', 'resume_from_checkpoint', 'tokenized_path')
    if any(config.get(key) for key in forbidden):
        raise ValueError('v5 requires a fresh base run; adapter/resume/tokenized source override is forbidden')
    if (config['dataset_dir'] != 'training/data/v5' or config['dataset'] != 'latex_formula_train'
            or config.get('eval_dataset') != 'latex_formula_eval_clean'
            or config['model_name_or_path'] != MODEL or config.get('overwrite_output_dir') is not False):
        raise ValueError('Unexpected v5 training configuration')
    data_dir = root/config['dataset_dir']
    data = verify_dataset(root, data_dir)
    run_dir = (root/(run_dir or config['output_dir'])).resolve()
    config['dataset_dir'] = str(data_dir.resolve())
    config['output_dir'] = str(run_dir/'checkpoints')
    return {'profile': profile, 'model': MODEL, 'dataset': data,
            'config_source_sha256': sha(config_path), 'effective_config': config,
            'protocol_sha256': protocol_hashes(root), 'run_dir': str(run_dir),
            'command': ['llamafactory-cli', 'train', str(run_dir/'effective_config.yaml')]}


def resolve_model_revision():
    from huggingface_hub import model_info
    revision = model_info(MODEL).sha
    if not revision or not re.fullmatch(r'[0-9a-f]{40,64}', revision):
        raise ValueError('Could not resolve an immutable base-model revision')
    return revision


def ensure_cached_model(revision):
    from huggingface_hub import snapshot_download
    try:
        snapshot = Path(snapshot_download(MODEL, revision=revision, local_files_only=True))
    except Exception as error:
        raise ValueError(f'Base model is not cached. Download manually: hf download {MODEL} --revision {revision}') from error
    index = snapshot/'model.safetensors.index.json'
    weights = set(json.loads(index.read_text())['weight_map'].values()) if index.is_file() else {'model.safetensors'}
    if not weights or any(not (snapshot/name).is_file() or (snapshot/name).stat().st_size == 0 for name in weights):
        raise ValueError(f'Model weights are incomplete. Download manually: hf download {MODEL} --revision {revision}')
    return str(snapshot)


def check_training_runtime():
    import torch
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise ValueError('The v5 BF16 profile requires a CUDA GPU with BF16 support')
    return {'gpu': torch.cuda.get_device_name(0), 'cuda': torch.version.cuda}


def verify_execution_binding(plan, root):
    if verify_dataset(root, root/'training/data/v5') != plan['dataset']:
        raise ValueError('Dataset binding changed since planning')
    if protocol_hashes(root) != plan['protocol_sha256']:
        raise ValueError('Experiment protocol changed since planning')
    if 'profile' in plan and sha(root/PROFILES[plan['profile']]) != plan['config_source_sha256']:
        raise ValueError('Training configuration changed since planning')
    if plan.get('training_run_dir'):
        candidates, revision = discover_checkpoints(Path(plan['training_run_dir']), plan['dataset'], plan['protocol_sha256'])
        identities = [{k:c[k] for k in ('name','adapter','sha256')} for c in plan['candidates'][1:]]
        if candidates != identities or revision != plan['model_revision']:
            raise ValueError('Checkpoint binding changed since planning')


def train(plan, root, runner=subprocess.run, resolver=resolve_model_revision, model_check=ensure_cached_model):
    run_dir = Path(plan['run_dir'])
    if run_dir.exists(): raise FileExistsError(run_dir)
    verify_execution_binding(plan, root)
    plan = {**plan, 'model_revision': resolver(), 'effective_config': dict(plan['effective_config'])}
    model_check(plan['model_revision'])
    verify_execution_binding(plan, root)
    plan['effective_config']['model_revision'] = plan['model_revision']
    run_dir.mkdir(parents=True, exist_ok=False)
    config_path = run_dir/'effective_config.yaml'
    config_path.write_text(yaml.safe_dump(plan['effective_config'], sort_keys=False), encoding='utf-8')
    manifest = {**plan, 'environment': environment(), 'config_sha256': sha(config_path), 'status': 'running'}
    write_json(run_dir/'run_manifest.json', manifest)
    try:
        verify_execution_binding(plan, root)
        runner(plan['command'], cwd=root, check=True)
        verify_execution_binding(plan, root)
        paths = sorted((run_dir/'checkpoints').glob('checkpoint-*'))
        if not paths: raise ValueError('Training produced no checkpoints')
        manifest['checkpoints'] = {p.name: checkpoint_files(p) for p in paths}
    except Exception:
        manifest['status'] = 'failed'
        write_json(run_dir/'run_manifest.json', manifest)
        raise
    manifest['status'] = 'completed'
    write_json(run_dir/'run_manifest.json', manifest)


def checkpoint_files(path):
    config = path/'adapter_config.json'
    weights = [p for p in path.glob('adapter_model.*') if p.suffix in {'.safetensors', '.bin'}]
    if not config.is_file() or not weights or any(p.stat().st_size == 0 for p in weights):
        raise ValueError(f'Incomplete adapter checkpoint: {path}')
    if json.loads(config.read_text()).get('base_model_name_or_path') != MODEL:
        raise ValueError(f'Checkpoint base model does not match v5: {path}')
    state = path/'trainer_state.json'
    return {p.name: sha(p) for p in sorted([config, *weights, *([state] if state.is_file() else [])])}


def discover_checkpoints(run_dir, data, protocol):
    manifest = json.loads((run_dir/'run_manifest.json').read_text())
    if manifest.get('profile') != 'sft' or manifest.get('status') != 'completed':
        raise ValueError('Checkpoint comparison requires a completed v5 SFT run, not smoke/partial training')
    if manifest.get('dataset') != data or manifest.get('protocol_sha256') != protocol:
        raise ValueError('Training data or evaluation protocol differs from the recorded run')
    if sha(run_dir/'effective_config.yaml') != manifest['config_sha256']:
        raise ValueError('Training configuration changed after launch')
    paths = sorted((p for p in (run_dir/'checkpoints').glob('checkpoint-*') if re.fullmatch(r'checkpoint-\d+', p.name)),
                   key=lambda p: int(p.name.split('-')[1]))
    if not paths:
        raise ValueError('No saved checkpoints found')
    actual = {p.name: checkpoint_files(p) for p in paths}
    if actual != manifest.get('checkpoints'):
        raise ValueError('Saved checkpoints changed after training completed')
    return [{'name': p.name, 'adapter': str(p), 'sha256': actual[p.name]} for p in paths], manifest['model_revision']


def evaluation_plan(root, run_dir=None, baseline_only=False, output=None, max_new_tokens=256):
    if max_new_tokens <= 0: raise ValueError('max_new_tokens must be positive')
    data_dir = root/'training/data/v5'
    data = verify_dataset(root, data_dir)
    protocol = protocol_hashes(root)
    candidates = [{'name': 'base', 'adapter': None, 'sha256': None}]
    run_dir = (root/(run_dir or 'saves/qwen3-4b-latex-correction/lora/sft-v5')).resolve()
    revision = None
    if not baseline_only:
        checkpoints, revision = discover_checkpoints(run_dir, data, protocol)
        candidates += checkpoints
    output = (root/(output or ('reports/v5/base-development' if baseline_only else 'reports/v5/checkpoint-development'))).resolve()
    for candidate in candidates:
        candidate['command'] = [sys.executable, '-B', '-m', 'training.run_lora_inference',
                                '--model', MODEL, '--eval-file', str(data_dir/FILES['eval_clean']),
                                '--out', str(output/candidate['name']/'predictions.jsonl'),
                                '--max-new-tokens', str(max_new_tokens)]
        if candidate['adapter']: candidate['command'] += ['--adapter', candidate['adapter']]
    return {'model': MODEL, 'model_revision': revision, 'dataset': data, 'protocol_sha256': protocol, 'split': 'development',
            'eval_file': str(data_dir/FILES['eval_clean']), 'max_new_tokens': max_new_tokens,
            'selection': 'postprocessed macro_math_accuracy, then micro_math_accuracy; base/earlier step breaks ties',
            'candidates': candidates, 'output': str(output), 'baseline_only': baseline_only,
            'training_run_dir': str(run_dir) if not baseline_only else None}


def validate_predictions(rows, expected):
    if len(rows) != len(expected): raise ValueError('Incomplete prediction coverage')
    for row, source in zip(rows, expected):
        if row.get('input') != source['input'] or row.get('expected') != source['output'] or row.get('metadata') != source['metadata']:
            raise ValueError('Prediction data/order/membership does not match the audited development set')
        if not isinstance(row.get('raw_prediction'), str) or not isinstance(row.get('prediction'), str):
            raise ValueError('Both raw and postprocessed predictions are required')


def evaluate(plan, root, runner=subprocess.run, resolver=resolve_model_revision, model_check=ensure_cached_model):
    output = Path(plan['output'])
    if output.exists(): raise FileExistsError(output)
    verify_execution_binding(plan, root)
    revision = plan['model_revision'] or resolver()
    model_check(revision)
    verify_execution_binding(plan, root)
    plan = {**plan, 'model_revision': revision, 'candidates': [
        {**c, 'command': [*c['command'], '--revision', revision]} for c in plan['candidates']]}
    output.mkdir(parents=True, exist_ok=False)
    manifest = {**plan, 'environment': environment(), 'status': 'running'}
    write_json(output/'evaluation_manifest.json', manifest)
    expected = load_jsonl(Path(plan['eval_file']))
    results = []
    try:
        for candidate in plan['candidates']:
            directory = output/candidate['name']; directory.mkdir()
            verify_execution_binding(plan, root)
            runner(candidate['command'], cwd=root, check=True)
            verify_execution_binding(plan, root)
            predictions = directory/'predictions.jsonl'
            rows = load_prediction_rows(predictions)
            validate_predictions(rows, expected)
            metrics = evaluate_pairs(rows)
            write_json(directory/'metrics.json', metrics)
            write_report(metrics, directory/'report.md')
            results.append({'name': candidate['name'], 'prediction_sha256': sha(predictions),
                            'raw': metrics['raw_metrics'], 'postprocessed': metrics['postprocessed_metrics']})
        ranking = sorted(results, key=lambda r: (-r['postprocessed']['macro_math_accuracy'],
                                                 -r['postprocessed']['micro_math_accuracy']))
        write_json(output/'comparison.json', {'selection': plan['selection'], 'results': results,
                                              'recommended_model': ranking[0]['name'] if not plan['baseline_only'] else None,
                                              'note': 'Development selection only; no test-set scores. A base win means no demonstrated SFT gain.'})
        lines = ['# v5 development comparison', '', '| Model | Raw micro | Raw macro | Post micro | Post macro |',
                 '| --- | ---: | ---: | ---: | ---: |']
        for r in results:
            lines.append(f"| {r['name']} | {r['raw']['micro_math_accuracy']:.4f} | {r['raw']['macro_math_accuracy']:.4f} | {r['postprocessed']['micro_math_accuracy']:.4f} | {r['postprocessed']['macro_math_accuracy']:.4f} |")
        lines += ['', 'Development only. Test remains reserved; historical v3 is not an unseen baseline.',
                  'Recommendation: '+(ranking[0]['name'] if not plan['baseline_only'] else 'baseline only; no checkpoint selection'), '']
        (output/'comparison.md').write_text('\n'.join(lines), encoding='utf-8')
    except Exception:
        manifest['status'] = 'failed'
        write_json(output/'evaluation_manifest.json', manifest)
        raise
    manifest['status'] = 'completed'
    write_json(output/'evaluation_manifest.json', manifest)
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    training = sub.add_parser('train', help='Validate and print a training plan; --execute launches it')
    training.add_argument('--profile', choices=PROFILES, default='sft')
    training.add_argument('--run-dir', type=Path)
    training.add_argument('--execute', action='store_true')
    evaluation = sub.add_parser('evaluate', help='Development baseline/checkpoint plan; --execute runs inference')
    evaluation.add_argument('--baseline-only', action='store_true')
    evaluation.add_argument('--run-dir', type=Path)
    evaluation.add_argument('--output', type=Path)
    evaluation.add_argument('--max-new-tokens', type=int, default=256)
    evaluation.add_argument('--execute', action='store_true')
    args = parser.parse_args(argv)
    if args.action == 'train':
        plan = training_plan(ROOT, args.profile, args.run_dir)
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        if args.execute:
            plan['hardware'] = check_training_runtime()
            train(plan, ROOT)
    else:
        plan = evaluation_plan(ROOT, args.run_dir, args.baseline_only, args.output, args.max_new_tokens)
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        if args.execute: evaluate(plan, ROOT)


if __name__ == '__main__': main()
