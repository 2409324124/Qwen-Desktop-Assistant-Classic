import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


def normalize_latex(value: str) -> str:
    normalized = value.strip()
    normalized = normalized.replace("\\left", "").replace("\\right", "")
    normalized = normalized.replace("\\,", "").replace("\\;", "").replace("\\quad", "")
    normalized = re.sub(r"\s+", "", normalized)
    normalized = normalized.replace(r"\operatorname", "")
    return normalized


def evaluate_pairs(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_layer: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "exact": 0, "normalized": 0})
    failures: list[dict[str, Any]] = []
    exact = 0
    normalized = 0

    for row in rows:
        expected = str(row["expected"])
        prediction = str(row["prediction"])
        is_exact = prediction.strip() == expected.strip()
        is_normalized = normalize_latex(prediction) == normalize_latex(expected)
        exact += int(is_exact)
        normalized += int(is_normalized)

        metadata = row.get("metadata") or {}
        layer = str(metadata.get("dataset_layer") or "unknown")
        by_layer[layer]["total"] += 1
        by_layer[layer]["exact"] += int(is_exact)
        by_layer[layer]["normalized"] += int(is_normalized)

        if not is_normalized:
            failures.append(
                {
                    "input": row.get("input", ""),
                    "expected": expected,
                    "prediction": prediction,
                    "metadata": metadata,
                }
            )

    total = len(rows)
    layer_summary = {}
    for layer, stats in sorted(by_layer.items()):
        layer_total = stats["total"]
        layer_summary[layer] = {
            "total": layer_total,
            "exact_match": stats["exact"],
            "normalized_match": stats["normalized"],
            "exact_accuracy": stats["exact"] / layer_total if layer_total else 0.0,
            "normalized_accuracy": stats["normalized"] / layer_total if layer_total else 0.0,
        }

    return {
        "total": total,
        "exact_match": exact,
        "normalized_match": normalized,
        "exact_accuracy": exact / total if total else 0.0,
        "normalized_accuracy": normalized / total if total else 0.0,
        "by_layer": layer_summary,
        "failures": failures,
    }


def load_prediction_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            payload = json.loads(line)
            missing = {"input", "expected", "prediction"} - set(payload)
            if missing:
                raise ValueError(f"{path}:{line_number}: missing fields: {', '.join(sorted(missing))}")
            rows.append(payload)
    return rows


def write_report(results: dict[str, Any], output_path: Path, max_failures: int = 20) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Qwen3-4B LaTeX Correction Evaluation",
        "",
        f"- total: {results['total']}",
        f"- exact_accuracy: {results['exact_accuracy']:.4f}",
        f"- normalized_accuracy: {results['normalized_accuracy']:.4f}",
        "",
        "## By Layer",
        "",
        "| layer | total | exact | normalized | normalized accuracy |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for layer, stats in results["by_layer"].items():
        lines.append(
            f"| {layer} | {stats['total']} | {stats['exact_match']} | "
            f"{stats['normalized_match']} | {stats['normalized_accuracy']:.4f} |"
        )

    lines.extend(["", "## Failure Samples", ""])
    for index, failure in enumerate(results["failures"][:max_failures], 1):
        lines.extend(
            [
                f"### {index}",
                "",
                f"- input: {failure['input']}",
                f"- expected: `{failure['expected']}`",
                f"- prediction: `{failure['prediction']}`",
                "",
            ]
        )

    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate LaTeX correction predictions.")
    parser.add_argument("--predictions", type=Path, required=True, help="JSONL with input, expected, prediction.")
    parser.add_argument("--report", type=Path, default=Path("reports/qwen3-4b-latex-correction-eval.md"))
    parser.add_argument("--json", type=Path, default=None, help="Optional JSON metrics output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = evaluate_pairs(load_prediction_rows(args.predictions))
    write_report(results, args.report)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in results.items() if k != "failures"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
