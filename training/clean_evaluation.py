import argparse
import json
from pathlib import Path
from typing import Any

from training.dataset_quality import apply_quality_overrides, load_quality_overrides
from training.prepare_dataset import load_jsonl, write_jsonl


def clean_evaluation(
    input_path: Path,
    output_path: Path,
    quarantine_path: Path,
    audit_path: Path,
    overrides_path: Path,
) -> dict[str, Any]:
    records = load_jsonl(input_path)
    target_field = "expected" if records and "expected" in records[0] else "output"
    accepted, rejected, counts = apply_quality_overrides(
        records,
        load_quality_overrides(overrides_path),
        target_field=target_field,
        require_all_overrides=False,
    )
    write_jsonl(output_path, accepted)
    write_jsonl(quarantine_path, rejected)
    audit = {
        "input": str(input_path),
        "output": str(output_path),
        "quarantine": str(quarantine_path),
        "target_field": target_field,
        "total": len(records),
        "clean_total": len(accepted),
        **counts,
    }
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply reviewed quality decisions to an eval or prediction JSONL.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--quarantine", type=Path, default=Path("reports/eval-quarantine.jsonl"))
    parser.add_argument("--audit", type=Path, default=Path("reports/eval-quality-audit.json"))
    parser.add_argument(
        "--overrides",
        type=Path,
        default=Path("training/dataset_quality_overrides.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = clean_evaluation(args.input, args.output, args.quarantine, args.audit, args.overrides)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
