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
VERSION_PROFILES = {'v5': PROFILES, 'v5.2': {
    'sft': 'training/qwen3_4b_lora_sft_v5_2.yaml',
    'smoke': 'training/qwen3_4b_lora_smoke_v5_2.yaml'}}
DATA_VERSIONS = {'v5': 'v5', 'v5.2': 'v5.2-reviewed-all-splits'}
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


def verify_dataset(root, data_dir, data_version='v5'):
    summary_path = data_dir/'dataset_summary.json'
    summary = json.loads(summary_path.read_text())
    expected_version = DATA_VERSIONS[data_version]
    if summary.get('data_version') != expected_version:
        raise ValueError(f'Expected audited {data_version} data')
    provenance = (('source_artifacts_sha256', root), ('source_code_sha256', root)) if data_version == 'v5' else (
        ('source_files_sha256', root/'training/reviews/v5_source'),
        ('review_files_sha256', root/'training/reviews'), ('code_sha256', root/'training'))
    for field, base in (*provenance, ('export_files_sha256', data_dir)):
        hashes = summary.get(field)
        if not hashes:
            raise ValueError(f'Missing provenance: {field}')
        for relative, expected in hashes.items():
            path = within(base, relative)
            if not path.is_file() or sha(path) != expected:
                raise ValueError(f'Hash mismatch: {path}')
    required_exports = {*FILES.values(), 'dataset_info.json'}
    if data_version == 'v5.2':
        required_exports.add('review_manifest.jsonl')
        required = {
            'source_files_sha256': {*FILES.values(), 'dataset_info.json'},
            'review_files_sha256': {f'v5_{split}_review.jsonl' for split in ('train', 'eval', 'test')},
            'code_sha256': {'clean_v5_holdouts.py', 'clean_v5_training.py', 'formula_grouping.py',
                            'formula_structure.py', 'latex_semantics.py', 'evaluate_latex.py'}}
        for field, filenames in required.items():
            if not filenames <= summary[field].keys():
                raise ValueError(f'Missing provenance members: {field}')
    if not required_exports <= summary['export_files_sha256'].keys():
        raise ValueError('Required training/evaluation exports are not hash-bound')
    info = json.loads((data_dir/'dataset_info.json').read_text())
    for name in ('train', 'eval_clean'):
        if info[f'latex_formula_{name}']['file_name'] != FILES[name]:
            raise ValueError('Unexpected dataset registry mapping')
    keys, accepted = [], {}
    for name, filename in FILES.items():
        rows = load_jsonl(data_dir/filename)
        split = 'eval' if name == 'eval_clean' else name
        count = summary[name]['total'] if data_version == 'v5' else summary['splits'][split]['accepted']['total']
        if not rows or len(rows) != count:
            raise ValueError(f'Empty or inconsistent {name} split')
        for row in rows:
            meta = row.get('metadata', {})
            if (meta.get('data_version') != expected_version or meta.get('evaluation_role') != 'main'
                    or not meta.get('formula_group_id') or not meta.get('source_id')
                    or meta.get('split') != split):
                raise ValueError(f'Invalid {data_version} membership in {name}')
        accepted[split] = rows
        keys.append({key for row in rows for key in _group_keys(row)} |
                    {('group', row['metadata']['formula_group_id']) for row in rows})
    if any(keys[a] & keys[b] for a,b in ((0,1),(0,2),(1,2))):
        raise ValueError('Cross-split leakage detected')
    if data_version == 'v5.2':
        verify_reviewed_membership(root, data_dir, accepted, expected_version)
    binding = {'summary_sha256': sha(summary_path), 'data_version': expected_version,
               'export_files_sha256': summary['export_files_sha256']}
    if data_version == 'v5':
        binding['review_rule_sha256'] = summary['review_rule_sha256']
    else:
        binding['review_rule_version'] = expected_version
    return binding


def verify_reviewed_membership(root, data_dir, accepted, expected_version):
    """Bind every accepted label and split to the complete frozen review."""
    audit = load_jsonl(data_dir/'review_manifest.jsonl')
    audit_by_key = {(r['split'], r['source_id']): r for r in audit}
    if len(audit_by_key) != len(audit):
        raise ValueError('Duplicate reviewed membership')
    frozen_keys = set()
    for split, rows in accepted.items():
        filename = FILES['eval_clean' if split == 'eval' else split]
        frozen = load_jsonl(root/'training/reviews/v5_source'/filename)
        originals = {r['metadata']['source_id']: r for r in frozen}
        reviews = load_jsonl(root/'training/reviews'/f'v5_{split}_review.jsonl')
        decisions = {r['source_id']: r for r in reviews}
        if len(originals) != len(frozen) or len(decisions) != len(reviews) or set(decisions) != set(originals):
            raise ValueError('Incomplete frozen review membership')
        expected_ids = set()
        for sid, original in originals.items():
            key = (split, sid); frozen_keys.add(key)
            record = audit_by_key.get(key); decision = decisions[sid]
            if (record is None or original['metadata'].get('split') != split
                    or record.get('decision') != decision.get('decision')
                    or record.get('output') != decision.get('output')):
                raise ValueError('Invalid frozen review binding')
            for field in ('input', 'output'):
                digest = hashlib.sha256(original[field].encode()).hexdigest()
                if record.get(field+'_sha256') != digest or decision.get(field+'_sha256') != digest:
                    raise ValueError('Invalid frozen review label binding')
            if record.get('final_action') in {'keep', 'repair'} and not record.get('exported_as_duplicate_of'):
                expected_ids.add(sid)
        actual_ids = [r['metadata']['source_id'] for r in rows]
        if len(set(actual_ids)) != len(actual_ids) or set(actual_ids) != expected_ids:
            raise ValueError('Incomplete accepted review membership')
        for row in rows:
            meta = row['metadata']; sid = meta['source_id']; decision = decisions[sid]
            expected_output = decision.get('output') if decision['decision'] == 'repair' else originals[sid]['output']
            if (row['instruction'] != originals[sid]['instruction']
                    or row['input'] != originals[sid]['input'] or row['output'] != expected_output
                    or meta.get('review_rule_version') != expected_version
                    or meta.get('review_basis') != 'input_and_original_label_only'
                    or meta.get('review_status') != audit_by_key[(split, sid)]['final_action']):
                raise ValueError('Invalid reviewed label or membership')
    if set(audit_by_key) != frozen_keys:
        raise ValueError('Review manifest differs from frozen membership')


def environment():
    packages = {}
    for package in ('llamafactory', 'transformers', 'torch', 'peft', 'accelerate', 'datasets'):
        try: packages[package] = version(package)
        except PackageNotFoundError: packages[package] = None
    return {'python': sys.version, 'packages': packages}


def protocol_hashes(root):
    return {name: sha(root/name) for name in PROTOCOL_FILES}


def training_plan(root, profile, run_dir=None, data_version='v5'):
    config_path = root/VERSION_PROFILES[data_version][profile]
    config = yaml.safe_load(config_path.read_text())
    forbidden = ('adapter_name_or_path', 'resume_from_checkpoint', 'tokenized_path')
    if any(config.get(key) for key in forbidden):
        raise ValueError('v5 requires a fresh base run; adapter/resume/tokenized source override is forbidden')
    if (config['dataset_dir'] != f'training/data/{data_version}' or config['dataset'] != 'latex_formula_train'
            or config.get('eval_dataset') != 'latex_formula_eval_clean'
            or config['model_name_or_path'] != MODEL or config.get('overwrite_output_dir') is not False):
        raise ValueError('Unexpected v5 training configuration')
    data_dir = (root/config['dataset_dir']).resolve()
    data = verify_dataset(root, data_dir, data_version)
    run_dir = (root/(run_dir or config['output_dir'])).resolve()
    config['dataset_dir'] = str(run_dir/'training_data')
    config['output_dir'] = str(run_dir/'checkpoints')
    return {'profile': profile, 'model': MODEL, 'dataset': data,
            'data_version': data_version, 'data_dir': str(data_dir),
            'config_source_sha256': sha(config_path), 'effective_config': config,
            'protocol_sha256': protocol_hashes(root), 'run_dir': str(run_dir),
            'command': ['llamafactory-cli', 'train', str(run_dir/'effective_config.yaml')]}



def write_training_projection(plan, root):
    """Write only flat model-facing columns; retain audited records separately."""
    directory = Path(plan['run_dir'])/'training_data'
    directory.mkdir(exist_ok=False)
    source_dir = Path(plan['data_dir'])
    registry = json.loads((source_dir/'dataset_info.json').read_text())
    projected_registry, mapping, source_hashes, counts = {}, [], {}, {}
    for split in ('train', 'eval_clean'):
        filename = FILES[split]
        source = source_dir/filename
        source_hashes[str(source)] = sha(source)
        projected = []
        for physical_line, line in enumerate(source.read_text(encoding='utf-8').splitlines(), 1):
            if not line.strip(): continue
            row = json.loads(line)
            flat = {key: row[key] for key in ('instruction', 'input', 'output')}
            if any(not isinstance(value, str) for value in flat.values()):
                raise ValueError('Training projection requires string instruction/input/output')
            projected.append(flat)
            mapping.append({'projected_file': filename, 'projected_line': len(projected),
                            'source_file': str(source), 'source_line': physical_line,
                            'source_id': row['metadata']['source_id'],
                            'formula_group_id': row['metadata']['formula_group_id'],
                            'source_record_sha256': hashlib.sha256(json.dumps(row, ensure_ascii=False, sort_keys=True).encode()).hexdigest()})
        (directory/filename).write_text(''.join(json.dumps(row, ensure_ascii=False)+'\n' for row in projected), encoding='utf-8')
        counts[filename] = len(projected)
        name = 'latex_formula_'+split
        projected_registry[name] = {**registry[name], 'file_name': filename, 'formatting': 'alpaca',
                                   'columns': {'prompt': 'input', 'response': 'output', 'system': 'instruction'}}
    write_json(directory/'dataset_info.json', projected_registry)
    (directory/'source_map.jsonl').write_text(''.join(json.dumps(row, ensure_ascii=False)+'\n' for row in mapping), encoding='utf-8')
    files = [*counts, 'dataset_info.json', 'source_map.jsonl']
    return {'version': 'flat-training-columns-v1', 'directory': str(directory),
            'files_sha256': {name: sha(directory/name) for name in files},
            'source_files_sha256': source_hashes, 'rows': counts,
            'source_mapping_file': 'source_map.jsonl'}


def verify_training_projection(projection):
    directory = Path(projection['directory'])
    for filename, digest in projection['files_sha256'].items():
        path = within(directory, filename)
        if not path.is_file() or sha(path) != digest:
            raise ValueError(f'Training projection changed: {path}')
    for filename, digest in projection['source_files_sha256'].items():
        path = Path(filename)
        if not path.is_file() or sha(path) != digest:
            raise ValueError(f'Training projection source changed: {path}')

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
    if plan.get('training_projection'):
        verify_training_projection(plan['training_projection'])
    data_version = plan['data_version']
    data_dir = Path(plan['data_dir'])
    if data_dir.resolve() != (root/f'training/data/{data_version}').resolve():
        raise ValueError('Dataset directory binding changed since planning')
    if verify_dataset(root, data_dir, data_version) != plan['dataset']:
        raise ValueError('Dataset binding changed since planning')
    if protocol_hashes(root) != plan['protocol_sha256']:
        raise ValueError('Experiment protocol changed since planning')
    if 'profile' in plan:
        config_path = root/VERSION_PROFILES[data_version][plan['profile']]
        if sha(config_path) != plan['config_source_sha256']:
            raise ValueError('Training configuration changed since planning')
        expected = yaml.safe_load(config_path.read_text())
        expected['dataset_dir'] = str(Path(plan['run_dir'])/'training_data')
        expected['output_dir'] = str(Path(plan['run_dir'])/'checkpoints')
        effective = dict(plan['effective_config'])
        if effective.get('model_revision') == plan.get('model_revision'):
            effective.pop('model_revision', None)
        if effective != expected:
            raise ValueError('Effective training configuration binding changed')
        if plan.get('training_projection'):
            projection = plan['training_projection']
            sources = {str(data_dir/FILES[split]): sha(data_dir/FILES[split]) for split in ('train', 'eval_clean')}
            if (projection['source_files_sha256'] != sources
                    or projection['directory'] != expected['dataset_dir']):
                raise ValueError('Training projection dataset binding changed')
    if 'eval_file' in plan:
        expected = str(data_dir/FILES['eval_clean'])
        if plan['eval_file'] != expected or any(
                c['command'][c['command'].index('--eval-file')+1] != expected for c in plan['candidates']):
            raise ValueError('Evaluation dataset path binding changed')
    if plan.get('training_run_dir'):
        candidates, revision = discover_checkpoints(Path(plan['training_run_dir']), plan['dataset'], plan['protocol_sha256'], data_dir)
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
    plan['training_projection'] = write_training_projection(plan, root)
    verify_training_projection(plan['training_projection'])
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


def discover_checkpoints(run_dir, data, protocol, data_dir=None):
    manifest = json.loads((run_dir/'run_manifest.json').read_text())
    if manifest.get('profile') != 'sft' or manifest.get('status') != 'completed':
        raise ValueError('Checkpoint comparison requires a completed v5 SFT run, not smoke/partial training')
    if not manifest.get('training_projection'):
        raise ValueError('Missing bound training projection')
    verify_training_projection(manifest['training_projection'])
    if data_dir is not None:
        if manifest.get('data_dir') != str(data_dir):
            raise ValueError('Training dataset directory differs from evaluation')
        sources = {str(data_dir/FILES[split]): sha(data_dir/FILES[split]) for split in ('train', 'eval_clean')}
        projection = manifest['training_projection']
        if (projection['source_files_sha256'] != sources
                or projection['directory'] != str(run_dir/'training_data')):
            raise ValueError('Training projection dataset binding differs from evaluation')
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


def evaluation_plan(root, run_dir=None, baseline_only=False, output=None, max_new_tokens=256, data_version='v5'):
    if max_new_tokens <= 0: raise ValueError('max_new_tokens must be positive')
    data_dir = (root/f'training/data/{data_version}').resolve()
    data = verify_dataset(root, data_dir, data_version)
    protocol = protocol_hashes(root)
    candidates = [{'name': 'base', 'adapter': None, 'sha256': None}]
    run_dir = (root/(run_dir or f'saves/qwen3-4b-latex-correction/lora/sft-{data_version}')).resolve()
    revision = None
    if not baseline_only:
        checkpoints, revision = discover_checkpoints(run_dir, data, protocol, data_dir)
        candidates += checkpoints
    output = (root/(output or (f'reports/{data_version}/base-development' if baseline_only else f'reports/{data_version}/checkpoint-development'))).resolve()
    for candidate in candidates:
        candidate['command'] = [sys.executable, '-B', '-m', 'training.run_lora_inference',
                                '--model', MODEL, '--eval-file', str(data_dir/FILES['eval_clean']),
                                '--out', str(output/candidate['name']/'predictions.jsonl'),
                                '--max-new-tokens', str(max_new_tokens)]
        if candidate['adapter']: candidate['command'] += ['--adapter', candidate['adapter']]
    return {'model': MODEL, 'model_revision': revision, 'dataset': data,
            'data_version': data_version, 'data_dir': str(data_dir), 'protocol_sha256': protocol, 'split': 'development',
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
        lines = [f"# {plan['data_version']} development comparison", '', '| Model | Raw micro | Raw macro | Post micro | Post macro |',
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
    training.add_argument('--data-version', choices=DATA_VERSIONS, default='v5')
    training.add_argument('--profile', choices=PROFILES, default='sft')
    training.add_argument('--run-dir', type=Path)
    training.add_argument('--execute', action='store_true')
    evaluation = sub.add_parser('evaluate', help='Development baseline/checkpoint plan; --execute runs inference')
    evaluation.add_argument('--data-version', choices=DATA_VERSIONS, default='v5')
    evaluation.add_argument('--baseline-only', action='store_true')
    evaluation.add_argument('--run-dir', type=Path)
    evaluation.add_argument('--output', type=Path)
    evaluation.add_argument('--max-new-tokens', type=int, default=256)
    evaluation.add_argument('--execute', action='store_true')
    args = parser.parse_args(argv)
    if args.action == 'train':
        plan = training_plan(ROOT, args.profile, args.run_dir, args.data_version)
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        if args.execute:
            plan['hardware'] = check_training_runtime()
            train(plan, ROOT)
    else:
        plan = evaluation_plan(ROOT, args.run_dir, args.baseline_only, args.output, args.max_new_tokens, args.data_version)
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        if args.execute: evaluate(plan, ROOT)


if __name__ == '__main__': main()
