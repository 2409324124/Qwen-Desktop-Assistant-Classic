from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from training.latex_semantics import canonicalize_latex, parse_latex


DEFAULT_SOURCE_FILES = (
    "data/frozen/phase1/train_clean_v1_500.jsonl",
    "data/frozen/phase1/train_noisy_v4_900.jsonl",
    "data/frozen/phase1/train_hard_v5_600.jsonl",
)


def canonicalize_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    changed = 0
    added = 0
    output_transformations = 0
    formula_names: Counter[str] = Counter()
    ast_failures: list[dict[str, Any]] = []

    for index, record in enumerate(records, 1):
        cloned = dict(record)
        output = cloned.get("output")
        if not isinstance(output, str) or not output.strip():
            raise ValueError(f"record {index}: missing non-empty output")
        canonical = canonicalize_latex(output)
        previous = cloned.get("canonical_output")
        if previous != canonical:
            changed += 1
        if "canonical_output" not in cloned:
            added += 1
        if output != canonical:
            output_transformations += 1
        cloned["canonical_output"] = canonical
        formula_name = str((cloned.get("metadata") or {}).get("formula_name") or "unknown")
        formula_names[formula_name] += 1
        try:
            parse_latex(canonical)
        except ValueError as exc:
            ast_failures.append(
                {
                    "record": index,
                    "formula_name": formula_name,
                    "error": str(exc),
                    "canonical_output": canonical,
                }
            )
        normalized.append(cloned)

    return normalized, {
        "total": len(records),
        "changed": changed,
        "added": added,
        "output_transformations": output_transformations,
        "ast_failures": ast_failures,
        "formula_families": dict(sorted(formula_names.items())),
    }


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"{path}:{line_number}: expected a JSON object")
            records.append(payload)
    return records


def _serialize_jsonl(records: list[dict[str, Any]]) -> bytes:
    return "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonicalize_files(
    repo_root: Path,
    source_files: tuple[str, ...],
    *,
    write: bool,
) -> dict[str, Any]:
    report: dict[str, Any] = {"mode": "write" if write else "check", "files": {}, "totals": {}}
    total_records = 0
    total_changed = 0
    total_output_transformations = 0
    total_ast_failures = 0

    for relative_path in source_files:
        path = repo_root / relative_path
        before = path.read_bytes()
        records = _load_jsonl(path)
        normalized, stats = canonicalize_records(records)
        after = _serialize_jsonl(normalized)
        if write and before != after:
            temporary = path.with_suffix(path.suffix + ".tmp")
            temporary.write_bytes(after)
            temporary.replace(path)
        file_report = {
            **stats,
            "sha256_before": _sha256(before),
            "sha256_after": _sha256(after),
            "up_to_date": before == after,
        }
        report["files"][relative_path] = file_report
        total_records += stats["total"]
        total_changed += stats["changed"]
        total_output_transformations += stats["output_transformations"]
        total_ast_failures += len(stats["ast_failures"])

    report["totals"] = {
        "records": total_records,
        "changed": total_changed,
        "output_transformations": total_output_transformations,
        "ast_failures": total_ast_failures,
        "ast_coverage": (total_records - total_ast_failures) / total_records if total_records else 0.0,
    }
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Canonicalize frozen LaTeX Ground Truth fields.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Fail when canonical_output is absent or stale.")
    mode.add_argument("--write", action="store_true", help="Update canonical_output in the source JSONL files.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source", action="append", dest="sources", help="Source JSONL relative to repo root.")
    parser.add_argument(
        "--audit",
        type=Path,
        default=Path("training/canonicalization_audit.json"),
        help="Audit JSON output path relative to repo root.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sources = tuple(args.sources) if args.sources else DEFAULT_SOURCE_FILES
    report = canonicalize_files(args.repo_root, sources, write=args.write)
    audit_path = args.audit if args.audit.is_absolute() else args.repo_root / args.audit
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["totals"], ensure_ascii=False, indent=2))
    if args.check and report["totals"]["changed"]:
        sys.exit(1)
    if report["totals"]["ast_failures"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
