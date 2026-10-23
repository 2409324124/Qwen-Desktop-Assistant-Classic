import argparse
import csv
import json
from pathlib import Path
from typing import Any, Iterable


SOURCE_FIELD_CANDIDATES = (
    "input",
    "source",
    "src",
    "noisy",
    "error",
    "erroneous",
    "incorrect",
    "corrupted",
    "wrong",
    "original",
    "question",
    "text",
)
TARGET_FIELD_CANDIDATES = (
    "expected",
    "output",
    "target",
    "tgt",
    "label",
    "corrected",
    "correct",
    "clean",
    "reference",
    "formula",
    "latex",
    "truth",
    "ground_truth",
)
SUPPORTED_SUFFIXES = {".jsonl", ".json", ".csv", ".tsv"}


class LatexcConversionError(ValueError):
    pass


def _flatten_record(record: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in record.items():
        full_key = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            flattened.update(_flatten_record(value, full_key))
        else:
            flattened[full_key] = value
    return flattened


def _case_insensitive_lookup(fields: Iterable[str], wanted: str) -> str | None:
    wanted_lower = wanted.lower()
    for field in fields:
        if field.lower() == wanted_lower:
            return field
    return None


def _pick_field(fields: Iterable[str], candidates: tuple[str, ...]) -> str | None:
    fields = list(fields)
    for candidate in candidates:
        exact = _case_insensitive_lookup(fields, candidate)
        if exact is not None:
            return exact
    for candidate in candidates:
        for field in fields:
            normalized = field.lower().replace("-", "_")
            if normalized.endswith("." + candidate) or normalized.endswith("_" + candidate):
                return field
    return None


def detect_fields(
    record: dict[str, Any],
    *,
    source_field: str | None = None,
    target_field: str | None = None,
) -> tuple[str, str]:
    flattened = _flatten_record(record)
    string_fields = [key for key, value in flattened.items() if isinstance(value, str) and value.strip()]
    if source_field is None:
        source_field = _pick_field(string_fields, SOURCE_FIELD_CANDIDATES)
    if target_field is None:
        target_field = _pick_field(
            [field for field in string_fields if field != source_field],
            TARGET_FIELD_CANDIDATES,
        )

    missing = []
    if source_field is None:
        missing.append("source")
    if target_field is None:
        missing.append("target")
    if missing:
        fields = ", ".join(sorted(string_fields)) or "<no string fields>"
        raise LatexcConversionError(f"Could not infer {', '.join(missing)} field(s). Available string fields: {fields}")
    if source_field not in flattened:
        raise LatexcConversionError(f"Configured source field not found: {source_field}")
    if target_field not in flattened:
        raise LatexcConversionError(f"Configured target field not found: {target_field}")
    if source_field == target_field:
        raise LatexcConversionError("Source and target fields must be different")
    return source_field, target_field


def _load_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise LatexcConversionError(f"{path}:{line_number}: expected JSON object")
            yield payload


def _load_json(path: Path) -> Iterable[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        for key in ("data", "train", "test", "validation", "examples"):
            if isinstance(payload.get(key), list):
                payload = payload[key]
                break
    if not isinstance(payload, list):
        raise LatexcConversionError(f"{path}: expected a JSON array or an object containing a data split list")
    for index, item in enumerate(payload, 1):
        if not isinstance(item, dict):
            raise LatexcConversionError(f"{path}:{index}: expected JSON object")
        yield item


def _load_table(path: Path) -> Iterable[dict[str, Any]]:
    dialect = "excel-tab" if path.suffix.lower() == ".tsv" else "excel"
    with path.open("r", encoding="utf-8", newline="") as handle:
        yield from csv.DictReader(handle, dialect=dialect)


def iter_input_files(input_path: Path) -> list[Path]:
    if input_path.is_file():
        if input_path.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise LatexcConversionError(f"Unsupported input suffix: {input_path.suffix}")
        return [input_path]
    if not input_path.is_dir():
        raise LatexcConversionError(f"Input path does not exist: {input_path}")
    return sorted(path for path in input_path.rglob("*") if path.suffix.lower() in SUPPORTED_SUFFIXES)


def iter_records(path: Path) -> Iterable[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        yield from _load_jsonl(path)
    elif suffix == ".json":
        yield from _load_json(path)
    elif suffix in {".csv", ".tsv"}:
        yield from _load_table(path)
    else:
        raise LatexcConversionError(f"Unsupported input suffix: {path.suffix}")


def convert_latexc(
    input_path: Path,
    output_path: Path,
    *,
    source_field: str | None = None,
    target_field: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    if limit is not None and limit < 0:
        raise LatexcConversionError("--limit must be non-negative")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    files = iter_input_files(input_path)
    if not files:
        raise LatexcConversionError(f"No supported files found under {input_path}")

    total = 0
    skipped = 0
    field_pairs: dict[str, int] = {}
    with output_path.open("w", encoding="utf-8") as sink:
        for file_path in files:
            relative = str(file_path.relative_to(input_path)) if input_path.is_dir() else file_path.name
            for row_index, raw_record in enumerate(iter_records(file_path), 1):
                flattened = _flatten_record(raw_record)
                detected_source, detected_target = detect_fields(
                    raw_record,
                    source_field=source_field,
                    target_field=target_field,
                )
                source = str(flattened[detected_source]).strip()
                target = str(flattened[detected_target]).strip()
                if not source or not target:
                    skipped += 1
                    continue
                payload = {
                    "input": source,
                    "expected": target,
                    "metadata": {
                        "benchmark": "latexc",
                        "source_path": relative,
                        "row_index": row_index,
                        "source_field": detected_source,
                        "target_field": detected_target,
                    },
                }
                sink.write(json.dumps(payload, ensure_ascii=False) + "\n")
                total += 1
                field_key = f"{detected_source}->{detected_target}"
                field_pairs[field_key] = field_pairs.get(field_key, 0) + 1
                if limit is not None and total >= limit:
                    return {
                        "input": str(input_path),
                        "output": str(output_path),
                        "files": len(files),
                        "total": total,
                        "skipped": skipped,
                        "field_pairs": field_pairs,
                    }

    return {
        "input": str(input_path),
        "output": str(output_path),
        "files": len(files),
        "total": total,
        "skipped": skipped,
        "field_pairs": field_pairs,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a local LaTeXC checkout into benchmark JSONL.")
    parser.add_argument("--input", type=Path, required=True, help="LaTeXC data file or directory.")
    parser.add_argument("--output", type=Path, default=Path("benchmarks/latexc_eval.jsonl"))
    parser.add_argument("--source-field", default=None, help="Optional explicit noisy/source field name.")
    parser.add_argument("--target-field", default=None, help="Optional explicit clean/target field name.")
    parser.add_argument("--limit", type=int, default=None, help="Optional max records for conversion smoke tests.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = convert_latexc(
        args.input,
        args.output,
        source_field=args.source_field,
        target_field=args.target_field,
        limit=args.limit,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
