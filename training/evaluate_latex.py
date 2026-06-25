import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from tqdm.auto import tqdm

from training.latex_semantics import compare_latex, compare_latex_math_only


def normalize_latex(value: str) -> str:
    normalized = value.strip()
    normalized = normalized.replace("\\left", "").replace("\\right", "")
    normalized = normalized.replace("\\,", "").replace("\\;", "").replace("\\quad", "")
    normalized = re.sub(r"\s+", "", normalized)
    normalized = normalized.replace(r"\operatorname", "")
    return normalized


def evaluate_pairs(rows: list[dict[str, Any]], *, show_progress: bool = False) -> dict[str, Any]:
    def empty_stats() -> dict[str, int]:
        return {
            "total": 0,
            "exact": 0,
            "normalized": 0,
            "canonical": 0,
            "symbol_fidelity": 0,
            "semantic": 0,
            "math": 0,
            "format_compliance": 0,
            "parsed": 0,
            "math_parsed": 0,
        }

    by_layer: dict[str, dict[str, int]] = defaultdict(empty_stats)
    by_formula: dict[str, dict[str, int]] = defaultdict(empty_stats)
    failures: list[dict[str, Any]] = []
    math_failures: list[dict[str, Any]] = []
    exact = 0
    normalized = 0
    canonical = 0
    symbol_fidelity = 0
    semantic = 0
    math = 0
    format_compliance = 0
    parsed = 0
    math_parsed = 0
    match_levels: Counter[str] = Counter()
    math_match_levels: Counter[str] = Counter()

    for row in tqdm(rows, desc="Evaluating", unit="formula", disable=not show_progress):
        expected = str(row["expected"])
        prediction = str(row["prediction"])
        metadata = row.get("metadata") or {}
        formula_name = str(metadata.get("formula_name") or "unknown")
        comparison = compare_latex(expected, prediction, formula_name=formula_name)
        math_comparison = compare_latex_math_only(
            expected,
            prediction,
            formula_name=formula_name,
            input_text=str(row.get("input") or ""),
        )
        is_exact = comparison.exact_match
        is_normalized = normalize_latex(prediction) == normalize_latex(expected)
        exact += int(is_exact)
        normalized += int(is_normalized)
        canonical += int(comparison.canonical_match)
        symbol_fidelity += int(comparison.symbol_fidelity_match)
        semantic += int(comparison.semantic_match)
        math += int(math_comparison.math_match)
        format_compliance += int(math_comparison.format_compliant)
        parsed += int(comparison.parse_success)
        math_parsed += int(math_comparison.parse_success)
        match_levels[comparison.match_level] += 1
        math_match_levels[math_comparison.match_level] += 1

        layer = str(metadata.get("dataset_layer") or "unknown")
        for bucket in (by_layer[layer], by_formula[formula_name]):
            bucket["total"] += 1
            bucket["exact"] += int(is_exact)
            bucket["normalized"] += int(is_normalized)
            bucket["canonical"] += int(comparison.canonical_match)
            bucket["symbol_fidelity"] += int(comparison.symbol_fidelity_match)
            bucket["semantic"] += int(comparison.semantic_match)
            bucket["math"] += int(math_comparison.math_match)
            bucket["format_compliance"] += int(math_comparison.format_compliant)
            bucket["parsed"] += int(comparison.parse_success)
            bucket["math_parsed"] += int(math_comparison.parse_success)

        if not comparison.semantic_match:
            failures.append(
                {
                    "input": row.get("input", ""),
                    "expected": expected,
                    "prediction": prediction,
                    "metadata": metadata,
                    "match_level": comparison.match_level,
                    "reason": comparison.reason,
                }
            )
        if not math_comparison.math_match:
            math_failures.append(
                {
                    "input": row.get("input", ""),
                    "expected": expected,
                    "prediction": prediction,
                    "metadata": metadata,
                    "match_level": math_comparison.match_level,
                    "reason": math_comparison.reason,
                }
            )

    total = len(rows)
    def summarize(groups: dict[str, dict[str, int]]) -> dict[str, Any]:
        summary: dict[str, Any] = {}
        for name, stats in sorted(groups.items()):
            group_total = stats["total"]
            summary[name] = {
                "total": group_total,
                "exact_match": stats["exact"],
                "normalized_match": stats["normalized"],
                "canonical_match": stats["canonical"],
                "symbol_fidelity_match": stats["symbol_fidelity"],
                "semantic_match": stats["semantic"],
                "math_match": stats["math"],
                "format_compliance_match": stats["format_compliance"],
                "exact_accuracy": stats["exact"] / group_total if group_total else 0.0,
                "normalized_accuracy": stats["normalized"] / group_total if group_total else 0.0,
                "canonical_accuracy": stats["canonical"] / group_total if group_total else 0.0,
                "symbol_fidelity_accuracy": stats["symbol_fidelity"] / group_total if group_total else 0.0,
                "semantic_accuracy": stats["semantic"] / group_total if group_total else 0.0,
                "math_accuracy": stats["math"] / group_total if group_total else 0.0,
                "format_compliance_accuracy": stats["format_compliance"] / group_total if group_total else 0.0,
                "parse_coverage": stats["parsed"] / group_total if group_total else 0.0,
                "math_parse_coverage": stats["math_parsed"] / group_total if group_total else 0.0,
            }
        return summary

    return {
        "total": total,
        "math_match": math,
        "format_compliance_match": format_compliance,
        "exact_match": exact,
        "normalized_match": normalized,
        "canonical_match": canonical,
        "symbol_fidelity_match": symbol_fidelity,
        "semantic_match": semantic,
        "math_accuracy": math / total if total else 0.0,
        "format_compliance_accuracy": format_compliance / total if total else 0.0,
        "exact_accuracy": exact / total if total else 0.0,
        "normalized_accuracy": normalized / total if total else 0.0,
        "canonical_accuracy": canonical / total if total else 0.0,
        "symbol_fidelity_accuracy": symbol_fidelity / total if total else 0.0,
        "semantic_accuracy": semantic / total if total else 0.0,
        "parse_coverage": parsed / total if total else 0.0,
        "math_parse_coverage": math_parsed / total if total else 0.0,
        "math_match_levels": dict(sorted(math_match_levels.items())),
        "match_levels": dict(sorted(match_levels.items())),
        "by_layer": summarize(by_layer),
        "by_formula": summarize(by_formula),
        "failures": failures,
        "math_failures": math_failures,
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
        f"- math_accuracy: {results['math_accuracy']:.4f} (math-only primary)",
        f"- format_compliance_accuracy: {results['format_compliance_accuracy']:.4f}",
        f"- semantic_accuracy: {results['semantic_accuracy']:.4f} (legacy)",
        f"- symbol_fidelity_accuracy: {results['symbol_fidelity_accuracy']:.4f}",
        f"- canonical_accuracy: {results['canonical_accuracy']:.4f}",
        f"- exact_accuracy: {results['exact_accuracy']:.4f}",
        f"- normalized_accuracy: {results['normalized_accuracy']:.4f}",
        f"- parse_coverage: {results['parse_coverage']:.4f}",
        f"- math_parse_coverage: {results['math_parse_coverage']:.4f}",
        "",
        "## Math Match Levels",
        "",
        "| level | count |",
        "| --- | ---: |",
    ]
    for level, count in results["math_match_levels"].items():
        lines.append(f"| {level} | {count} |")
    lines.extend(
        [
        "",
        "## Legacy Match Levels",
        "",
        "| level | count |",
        "| --- | ---: |",
        ]
    )
    for level, count in results["match_levels"].items():
        lines.append(f"| {level} | {count} |")
    lines.extend(
        [
            "",
            "## By Layer",
            "",
            "| layer | total | exact | symbol fidelity | semantic | math | format compliance | math accuracy | parse coverage |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for layer, stats in results["by_layer"].items():
        lines.append(
            f"| {layer} | {stats['total']} | {stats['exact_match']} | "
            f"{stats['symbol_fidelity_match']} | {stats['semantic_match']} | "
            f"{stats['math_match']} | {stats['format_compliance_match']} | "
            f"{stats['math_accuracy']:.4f} | {stats['parse_coverage']:.4f} |"
        )

    lines.extend(["", "## Math Failure Samples", ""])
    for index, failure in enumerate(results["math_failures"][:max_failures], 1):
        lines.extend(
            [
                f"### {index}",
                "",
                f"- input: {failure['input']}",
                f"- expected: `{failure['expected']}`",
                f"- prediction: `{failure['prediction']}`",
                f"- match_level: {failure['match_level']}",
                f"- reason: {failure['reason']}",
                "",
            ]
        )

    lines.extend(["", "## Legacy Semantic Failure Samples", ""])
    for index, failure in enumerate(results["failures"][:max_failures], 1):
        lines.extend(
            [
                f"### {index}",
                "",
                f"- input: {failure['input']}",
                f"- expected: `{failure['expected']}`",
                f"- prediction: `{failure['prediction']}`",
                f"- match_level: {failure['match_level']}",
                f"- reason: {failure['reason']}",
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
    results = evaluate_pairs(load_prediction_rows(args.predictions), show_progress=True)
    write_report(results, args.report)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in results.items() if k != "failures"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
