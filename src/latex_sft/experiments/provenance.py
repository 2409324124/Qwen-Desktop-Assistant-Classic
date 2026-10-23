"""Historical source evidence is immutable; current execution has its own identity."""
import hashlib
import json
from pathlib import Path, PurePosixPath

EXECUTION_PROTOCOL_VERSION = 'latex-sft-package-v1'
SNAPSHOT_MANIFEST = 'archive/protocols/a082730/manifest.json'
SNAPSHOT_MANIFEST_SHA256 = 'f3617f4af4f660d7c8845f9cbccd3033410639540b0fb411cca2204a032cc851'
SNAPSHOT_PREFIX = 'archive/protocols/a082730/source/'
LEGACY_PROTOCOL_FILES = {'training/run_v5_experiment.py', 'training/run_lora_inference.py',
                         'training/evaluate_latex.py', 'training/latex_semantics.py',
                         'training/latex_postprocess.py', 'training/prompts.py'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe_path(root, relative):
    relative = str(relative)
    pure = PurePosixPath(relative)
    if pure.is_absolute() or '..' in pure.parts or '\\' in relative:
        raise ValueError(f'Invalid evidence path: {relative}')
    path = (Path(root)/relative).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError(f'Evidence escapes checkout: {relative}')
    return path


def snapshot_mapping(root):
    manifest = safe_path(root, SNAPSHOT_MANIFEST)
    if not manifest.is_file() or sha(manifest) != SNAPSHOT_MANIFEST_SHA256:
        raise ValueError('Historical snapshot mapping is missing or changed')
    mapping = json.loads(manifest.read_text(encoding='utf-8'))['files']
    for original, entry in mapping.items():
        safe_path(root, original)
        if entry['path'] != SNAPSHOT_PREFIX + original:
            raise ValueError(f'Invalid historical source mapping: {original}')
        safe_path(root, entry['path'])
    return mapping


def verify_snapshot(root):
    mapping = snapshot_mapping(root)
    for original, entry in mapping.items():
        path = safe_path(root, entry['path'])
        if not path.is_file() or sha(path) != entry['sha256']:
            raise ValueError(f'Historical source snapshot changed: {original}')
    return mapping


def historical_source(root, relative, expected):
    """Resolve pre-migration source without changing any historical digest.

    Other checkouts/fixtures without a migration snapshot still use exact current
    file hashes. A migrated checkout always validates the pinned mapping first.
    Unknown or older source versions never silently pass through the archive.
    """
    current = safe_path(root, relative)
    manifest = safe_path(root, SNAPSHOT_MANIFEST)
    if manifest.exists():
        mapping = snapshot_mapping(root)
        entry = mapping.get(str(relative))
        if entry is not None:
            if entry['sha256'] != expected:
                raise ValueError(f'Historical source hash is not in this snapshot: {relative}')
            archived = safe_path(root, entry['path'])
            if not archived.is_file() or sha(archived) != expected:
                raise ValueError(f'Historical source snapshot changed: {relative}')
            return archived
    if not current.is_file() or sha(current) != expected:
        raise ValueError(f'Hash mismatch: {current}')
    return current


def verify_recorded_protocol(root, hashes):
    if not hashes or set(hashes) != LEGACY_PROTOCOL_FILES:
        raise ValueError('Incomplete or unknown historical execution protocol')
    for relative, expected in hashes.items():
        historical_source(root, relative, expected)
    return {'kind': 'historical', 'snapshot_manifest_sha256': SNAPSHOT_MANIFEST_SHA256,
            'source_files_sha256': hashes}


def package_source_hashes(package_root=None):
    """All executable package modules and shipped semantic resources, not caches."""
    package_root = Path(package_root) if package_root is not None else Path(__file__).resolve().parents[1]
    paths = sorted(path for path in package_root.rglob('*')
                   if path.is_file() and path.suffix in {'.py', '.json', '.txt'}
                   and '__pycache__' not in path.parts)
    return {'src/latex_sft/' + path.relative_to(package_root).as_posix(): sha(path) for path in paths}


def verify_package_checkout(root):
    """A wheel cannot attribute its execution to a different checkout's code."""
    executing = package_source_hashes()
    recorded = package_source_hashes(Path(root)/'src/latex_sft')
    if executing != recorded:
        missing = sorted(executing.keys() - recorded.keys())
        extra = sorted(recorded.keys() - executing.keys())
        changed = sorted(name for name in executing.keys() & recorded.keys()
                         if executing[name] != recorded[name])
        raise ValueError(f'Loaded package differs from research checkout: missing={missing}, extra={extra}, changed={changed}')
    return executing
