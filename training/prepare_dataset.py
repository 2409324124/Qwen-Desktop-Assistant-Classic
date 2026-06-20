import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from training.dataset_quality import apply_quality_overrides, load_quality_overrides
from training.latex_postprocess import postprocess_latex
from training.prompts import SYSTEM_PROMPT


DEFAULT_SOURCES: tuple[tuple[str, str], ...] = (
    ("clean", "train_clean_v1_500.jsonl"),
    ("noisy", "train_noisy_v4_900.jsonl"),
    ("hard", "train_hard_v5_600.jsonl"),
)

TRAIN_ONLY_SOURCES: tuple[tuple[str, str], ...] = (
    ("targeted", "training/targeted_v3_train.jsonl"),
)


class DatasetValidationError(ValueError):
    pass


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise DatasetValidationError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(payload, dict):
                raise DatasetValidationError(f"{path}:{line_number}: record must be a JSON object")
            records.append(payload)
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def validate_records(records: list[dict[str, Any]], source_name: str) -> None:
    seen_pairs: set[tuple[str, str]] = set()
    for index, record in enumerate(records, 1):
        for key in ("instruction", "input", "output"):
            value = record.get(key)
            if not isinstance(value, str) or not value.strip():
                raise DatasetValidationError(f"{source_name}:{index}: missing non-empty '{key}'")

        metadata = record.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            raise DatasetValidationError(f"{source_name}:{index}: metadata must be an object when present")

        pair = (record["input"].strip(), record["output"].strip())
        seen_pairs.add(pair)


def load_sources(repo_root: Path, sources: tuple[tuple[str, str], ...] = DEFAULT_SOURCES) -> list[dict[str, Any]]:
    combined: list[dict[str, Any]] = []
    for layer, relative_path in sources:
        path = repo_root / relative_path
        records = load_jsonl(path)
        validate_records(records, relative_path)
        for index, record in enumerate(records, 1):
            canonical_output = record.get("canonical_output")
            if not isinstance(canonical_output, str) or not canonical_output.strip():
                raise DatasetValidationError(f"{relative_path}:{index}: missing non-empty 'canonical_output'")
            canonical_output = postprocess_latex(canonical_output)
            cloned = dict(record)
            cloned["instruction"] = SYSTEM_PROMPT
            cloned["output"] = canonical_output
            cloned["canonical_output"] = canonical_output
            metadata = dict(cloned.get("metadata") or {})
            metadata["dataset_layer"] = layer
            metadata["source_file"] = relative_path
            cloned["metadata"] = metadata
            combined.append(cloned)
    return combined


def dedupe_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    seen: set[tuple[str, str]] = set()
    deduped: list[dict[str, Any]] = []
    duplicates = 0
    for record in records:
        key = (record["input"].strip(), record["output"].strip())
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        deduped.append(record)
    return deduped, duplicates


def split_key(record: dict[str, Any]) -> tuple[str, str, str]:
    metadata = record.get("metadata") or {}
    layer = metadata.get("dataset_layer") or "unknown"
    category = metadata.get("category") or "unknown"
    rule = metadata.get("hard_rule") or metadata.get("noise_rule") or metadata.get("perspective") or "unknown"
    return str(layer), str(category), str(rule)


def split_records(
    records: list[dict[str, Any]],
    *,
    eval_ratio: float = 0.1,
    seed: int = 42,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not 0 < eval_ratio < 1:
        raise ValueError("eval_ratio must be between 0 and 1")

    rng = random.Random(seed)
    buckets: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        buckets[split_key(record)].append(record)

    train: list[dict[str, Any]] = []
    eval_records: list[dict[str, Any]] = []
    for bucket_records in buckets.values():
        shuffled = list(bucket_records)
        rng.shuffle(shuffled)
        eval_count = round(len(shuffled) * eval_ratio)
        if len(shuffled) > 1:
            eval_count = max(1, eval_count)
        eval_count = min(eval_count, max(0, len(shuffled) - 1))
        eval_records.extend(shuffled[:eval_count])
        train.extend(shuffled[eval_count:])

    rng.shuffle(train)
    rng.shuffle(eval_records)
    return train, eval_records




def dataset_info() -> dict[str, Any]:
    columns = {"prompt": "input", "response": "output", "system": "instruction"}
    return {
        "latex_formula_train": {
            "file_name": "latex_formula_train.jsonl",
            "formatting": "alpaca",
            "columns": columns,
        },
        "latex_formula_eval": {
            "file_name": "latex_formula_eval.jsonl",
            "formatting": "alpaca",
            "columns": columns,
        },
        "latex_formula_eval_clean": {
            "file_name": "latex_formula_eval_clean.jsonl",
            "formatting": "alpaca",
            "columns": columns,
        },
    }

def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {"total": len(records), "layers": {}, "categories": {}}
    for record in records:
        metadata = record.get("metadata") or {}
        layer = str(metadata.get("dataset_layer") or "unknown")
        category = str(metadata.get("category") or "unknown")
        summary["layers"][layer] = summary["layers"].get(layer, 0) + 1
        summary["categories"][category] = summary["categories"].get(category, 0) + 1
    return summary


def build_datasets(
    repo_root: Path,
    out_dir: Path,
    eval_ratio: float,
    seed: int,
    *,
    sources: tuple[tuple[str, str], ...] = DEFAULT_SOURCES,
    train_only_sources: tuple[tuple[str, str], ...] = TRAIN_ONLY_SOURCES,
    quality_overrides: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    source_records = load_sources(repo_root, sources)
    train_only_records = load_sources(repo_root, train_only_sources) if train_only_sources else []
    overrides_path = repo_root / "training/dataset_quality_overrides.json"
    overrides = load_quality_overrides(overrides_path) if quality_overrides is None else quality_overrides
    quality_records, quarantined_records, quality_counts = apply_quality_overrides(
        source_records,
        overrides,
    )
    records, duplicate_count = dedupe_records(quality_records)
    train, eval_records = split_records(records, eval_ratio=eval_ratio, seed=seed)
    train.extend(train_only_records)
    validate_records(train, "train split")
    validate_records(eval_records, "eval split")

    train_path = out_dir / "latex_formula_train.jsonl"
    eval_path = out_dir / "latex_formula_eval.jsonl"
    eval_clean_path = out_dir / "latex_formula_eval_clean.jsonl"
    quarantine_path = out_dir / "latex_formula_quarantine.jsonl"
    write_jsonl(train_path, train)
    write_jsonl(eval_path, eval_records)
    write_jsonl(eval_clean_path, eval_records)
    write_jsonl(quarantine_path, quarantined_records)

    summary = {
        "source": summarize(source_records),
        "train_only_source": summarize(train_only_records),
        "quality_review": quality_counts,
        "quality_accepted": summarize(quality_records),
        "quarantine": summarize(quarantined_records),
        "deduped_source": summarize(records),
        "duplicate_input_output_pairs_removed": duplicate_count,
        "train": summarize(train),
        "eval": summarize(eval_records),
        "eval_clean": summarize(eval_records),
        "train_path": str(train_path),
        "eval_path": str(eval_path),
        "eval_clean_path": str(eval_clean_path),
        "quarantine_path": str(quarantine_path),
    }
    summary_path = out_dir / "dataset_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    dataset_info_path = out_dir / "dataset_info.json"
    dataset_info_path.write_text(json.dumps(dataset_info(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare frozen LaTeX correction datasets for LLaMA-Factory.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, default=Path("training/data"))
    parser.add_argument("--eval-ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = args.out_dir if args.out_dir.is_absolute() else args.repo_root / args.out_dir
    summary = build_datasets(args.repo_root, out_dir, args.eval_ratio, args.seed)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
