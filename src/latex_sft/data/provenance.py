"""Current data-code identities; frozen historical hashes live in the archive."""
from pathlib import Path

EXECUTION_PROTOCOL_VERSION = "latex-sft-package-v1"

MODULE_PATHS = {
    "latex_semantics.py": "core/semantics.py",
    "latex_postprocess.py": "core/postprocess.py",
    "prompts.py": "core/prompts.py",
    "evaluate_latex.py": "evaluation/evaluate_latex.py",
}


def current_source_path(name: str) -> Path:
    """Resolve a historical basename to the canonical implementation source."""
    package_root = Path(__file__).resolve().parents[1]
    return package_root / MODULE_PATHS.get(name, "data/" + name)


def current_source_paths() -> list[Path]:
    """Include shared kernels, resources and registries in new data provenance."""
    package_root = Path(__file__).resolve().parents[1]
    paths = [path for part in ("core", "data") for path in (package_root / part).rglob("*")
             if path.is_file() and path.suffix in {".py", ".json", ".txt"}]
    evaluation = package_root / "evaluation/evaluate_latex.py"
    if evaluation.is_file():
        paths.append(evaluation)
    return sorted(paths)


def current_code_hashes() -> dict[str, str]:
    """Content-address all code/resources relevant to new data execution."""
    import hashlib
    package_root = Path(__file__).resolve().parents[1]
    return {"src/latex_sft/" + path.relative_to(package_root).as_posix():
            hashlib.sha256(path.read_bytes()).hexdigest()
            for path in current_source_paths()}
