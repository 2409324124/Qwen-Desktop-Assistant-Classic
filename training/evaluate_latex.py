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


def is_output_protocol_compliant(prediction: str) -> bool:
    """Check output form independently of whether it is the correct formula.

    This checks the supported parser/dataset protocol, not arbitrary TeX syntax.
    Ordinary matrices use bmatrix; determinant/norm matrix delimiters retain
    their distinct vmatrix/Vmatrix semantics.
    """
    value = prediction.strip()
    if not value or '$' in value or '```' in value:
        return False
    if re.search(r"\\[\[\]()]|(?<!\\)(?:\\\\)*[_^](?!\{)|\\(?:over|dfrac|tfrac)\b", value) or '/' in value:
        return False
    if re.search(r"\\(?:text|operatorname|mathrm)\{[^{}]*[\s:：][^{}]*\}", value):
        return False
    if '\n' in value and r"\begin" not in value:
        return False
    environments = re.findall(r"\\begin\{([^{}]+)\}", value)
    if any(env not in {'bmatrix', 'vmatrix', 'Vmatrix'} for env in environments):
        return False
    if re.search(r"\b(?:here|formula|result|answer|because|therefore)\b", value, re.IGNORECASE):
        return False
    parsed = compare_latex_math_only(value, value)
    return parsed.parse_success and parsed.math_match


def _evaluate_pairs(rows: list[dict[str, Any]], *, show_progress: bool = False) -> dict[str, Any]:
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
            "output_protocol_compliance": 0,
            "parsed": 0,
            "math_parsed": 0,
            "unverified": 0,
        }

    by_layer: dict[str, dict[str, int]] = defaultdict(empty_stats)
    by_formula: dict[str, dict[str, int]] = defaultdict(empty_stats)
    by_formula_group: dict[str, dict[str, int]] = defaultdict(empty_stats)
    failures: list[dict[str, Any]] = []
    math_failures: list[dict[str, Any]] = []
    exact = 0
    normalized = 0
    canonical = 0
    symbol_fidelity = 0
    semantic = 0
    math = 0
    format_compliance = 0
    output_protocol_compliance = 0
    parsed = 0
    math_parsed = 0
    unverified = 0
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
        protocol_compliant = is_output_protocol_compliant(prediction)
        is_exact = comparison.exact_match
        is_normalized = normalize_latex(prediction) == normalize_latex(expected)
        exact += int(is_exact)
        normalized += int(is_normalized)
        canonical += int(comparison.canonical_match)
        symbol_fidelity += int(comparison.symbol_fidelity_match)
        semantic += int(comparison.semantic_match)
        math += int(math_comparison.math_match)
        format_compliance += int(math_comparison.format_compliant)
        output_protocol_compliance += int(protocol_compliant)
        parsed += int(comparison.parse_success)
        math_parsed += int(math_comparison.parse_success)
        unverified += int(math_comparison.verification_status == "unverified")
        match_levels[comparison.match_level] += 1
        math_match_levels[math_comparison.match_level] += 1

        layer = str(metadata.get("dataset_layer") or "unknown")
        buckets = [by_layer[layer], by_formula[formula_name]]
        group_value = metadata.get("formula_group_id")
        group_id = str(group_value).strip() if group_value is not None else ""
        if group_id:
            buckets.append(by_formula_group[group_id])
        for bucket in buckets:
            bucket["total"] += 1
            bucket["exact"] += int(is_exact)
            bucket["normalized"] += int(is_normalized)
            bucket["canonical"] += int(comparison.canonical_match)
            bucket["symbol_fidelity"] += int(comparison.symbol_fidelity_match)
            bucket["semantic"] += int(comparison.semantic_match)
            bucket["math"] += int(math_comparison.math_match)
            bucket["format_compliance"] += int(math_comparison.format_compliant)
            bucket["output_protocol_compliance"] += int(protocol_compliant)
            bucket["parsed"] += int(comparison.parse_success)
            bucket["math_parsed"] += int(math_comparison.parse_success)
            bucket["unverified"] += int(math_comparison.verification_status == "unverified")

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
                    "verification_status": math_comparison.verification_status,
                }
            )

    total = len(rows)
    def summarize(groups: dict[str, dict[str, int]]) -> dict[str, Any]:
        summary: dict[str, Any] = {}
        for name, stats in sorted(groups.items()):
            group_total = stats["total"]
            summary[name] = {
                "total": group_total,
                "n": group_total,
                "exact_match": stats["exact"],
                "normalized_match": stats["normalized"],
                "canonical_match": stats["canonical"],
                "symbol_fidelity_match": stats["symbol_fidelity"],
                "semantic_match": stats["semantic"],
                "math_match": stats["math"],
                "unverified": stats["unverified"],
                "format_compliance_match": stats["format_compliance"],
                "output_protocol_compliance_match": stats["output_protocol_compliance"],
                "output_protocol_compliance_accuracy": stats["output_protocol_compliance"] / group_total if group_total else 0.0,
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

    group_summary = summarize(by_formula_group)
    grouped_samples = sum(stats["n"] for stats in group_summary.values())

    def macro(metric: str) -> float | None:
        return sum(stats[metric] for stats in group_summary.values()) / len(group_summary) if group_summary else None

    return {
        "total": total,
        "primary_metric": "faithful_math_accuracy",
        "unverified": unverified,
        "unverified_rate": unverified / total if total else 0.0,
        "math_match": math,
        "format_compliance_match": format_compliance,
        "format_compliance_meaning": "mathematically correct and historical structural format match; not independent output protocol compliance",
        "output_protocol_compliance_match": output_protocol_compliance,
        "output_protocol_compliance_accuracy": output_protocol_compliance / total if total else 0.0,
        "exact_match": exact,
        "normalized_match": normalized,
        "canonical_match": canonical,
        "symbol_fidelity_match": symbol_fidelity,
        "semantic_match": semantic,
        "math_accuracy": math / total if total else 0.0,
        "micro_math_accuracy": math / total if total else 0.0,
        "macro_math_accuracy": macro("math_accuracy"),
        "macro_output_protocol_compliance_accuracy": macro("output_protocol_compliance_accuracy"),
        "macro_parse_coverage": macro("parse_coverage"),
        "macro_math_parse_coverage": macro("math_parse_coverage"),
        "grouped_samples": grouped_samples,
        "group_count": len(group_summary),
        "grouped_coverage": grouped_samples / total if total else 0.0,
        "by_formula_group_id": group_summary,
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


def _evaluate_with_raw(rows: list[dict[str, Any]], *, show_progress: bool = False) -> dict[str, Any]:
    results = _evaluate_pairs(rows, show_progress=show_progress)
    # Inference records raw_prediction when processing changed it. An explicit
    # postprocessed flag without raw text cannot reconstruct a raw measurement.
    raw_rows = []
    for row in rows:
        if "raw_prediction" in row:
            raw_rows.append({**row, "prediction": row["raw_prediction"]})
        elif not row.get("postprocessed"):
            raw_rows.append(row)
    raw_results = _evaluate_pairs(raw_rows)
    keys = ("total", "math_match", "math_accuracy", "micro_math_accuracy", "macro_math_accuracy", "macro_output_protocol_compliance_accuracy", "macro_parse_coverage", "macro_math_parse_coverage", "grouped_samples", "group_count", "grouped_coverage", "by_formula_group_id", "unverified", "unverified_rate", "format_compliance_match", "format_compliance_accuracy", "output_protocol_compliance_match", "output_protocol_compliance_accuracy", "exact_match", "exact_accuracy", "normalized_match", "normalized_accuracy", "canonical_match", "canonical_accuracy", "parse_coverage", "math_parse_coverage")
    results["raw_metrics"] = {key: raw_results[key] for key in keys}
    results["raw_metrics"]["coverage"] = len(raw_rows) / len(rows) if rows else 0.0
    results["postprocessed_metrics"] = {key: results[key] for key in keys}
    results["legacy_diagnostics"] = {key: results[key] for key in ("semantic_match", "semantic_accuracy", "symbol_fidelity_match", "symbol_fidelity_accuracy", "match_levels")}
    return results


def evaluate_pairs(rows: list[dict[str, Any]], *, show_progress: bool = False) -> dict[str, Any]:
    primary = []
    diagnostic = []
    for row in rows:
        metadata = row.get("metadata") or {}
        destination = diagnostic if metadata.get("evaluation_role") == "diagnostic" else primary
        destination.append(row)
    results = _evaluate_with_raw(primary, show_progress=show_progress)
    results["input_total"] = len(rows)
    results["diagnostic_total"] = len(diagnostic)
    results["diagnostic_metrics"] = _evaluate_with_raw(diagnostic) if diagnostic else None
    return results


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

    def optional_metric(value: float | None) -> str:
        return f"{value:.4f}" if value is not None else "null (no explicit formula groups)"

    lines = [
        "# Qwen3-4B LaTeX Correction Evaluation",
        "",
        f"- total: {results['total']}",
        f"- input_total: {results['input_total']} (includes diagnostics)",
        f"- diagnostic_total: {results['diagnostic_total']} (excluded from all primary metrics)",
        f"- math_accuracy: {results['math_accuracy']:.4f} (faithful mathematical equivalence primary)",
        f"- macro_math_accuracy: {optional_metric(results['macro_math_accuracy'])} (each labelled formula group has equal weight)",
        f"- grouped_samples: {results['grouped_samples']}; group_count: {results['group_count']}; grouped_coverage: {results['grouped_coverage']:.4f}",
        f"- macro_output_protocol_compliance_accuracy: {optional_metric(results['macro_output_protocol_compliance_accuracy'])}",
        f"- macro_math_parse_coverage: {optional_metric(results['macro_math_parse_coverage'])}",
        f"- unverified: {results['unverified']} (equivalence not established; not scored correct)",
        f"- raw_math_accuracy: {results['raw_metrics']['math_accuracy']:.4f}",
        f"- raw_macro_math_accuracy: {optional_metric(results['raw_metrics']['macro_math_accuracy'])}",
        f"- raw_grouped_samples: {results['raw_metrics']['grouped_samples']}; raw_group_count: {results['raw_metrics']['group_count']}; raw_grouped_coverage: {results['raw_metrics']['grouped_coverage']:.4f}",
        f"- raw_exact_accuracy: {results['raw_metrics']['exact_accuracy']:.4f}",
        f"- raw_format_compliance_accuracy: {results['raw_metrics']['format_compliance_accuracy']:.4f}",
        f"- raw_output_protocol_compliance_accuracy: {results['raw_metrics']['output_protocol_compliance_accuracy']:.4f}",
        f"- raw_coverage: {results['raw_metrics']['coverage']:.4f}",
        f"- postprocessed_math_accuracy: {results['postprocessed_metrics']['math_accuracy']:.4f}",
        f"- postprocessed_format_compliance_accuracy: {results['postprocessed_metrics']['format_compliance_accuracy']:.4f}",
        f"- postprocessed_output_protocol_compliance_accuracy: {results['postprocessed_metrics']['output_protocol_compliance_accuracy']:.4f}",
        f"- postprocessed_exact_accuracy: {results['postprocessed_metrics']['exact_accuracy']:.4f}",
        f"- format_compliance_accuracy: {results['format_compliance_accuracy']:.4f} (correct formula + historical structural format match; not independent protocol compliance)",
        f"- output_protocol_compliance_accuracy: {results['output_protocol_compliance_accuracy']:.4f} (supported single bare formula; independent of correctness)",
        f"- semantic_accuracy: {results['semantic_accuracy']:.4f} (legacy historical diagnostic only)",
        f"- symbol_fidelity_accuracy: {results['symbol_fidelity_accuracy']:.4f} (legacy historical diagnostic only)",
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

    for label, metrics in (("Postprocessed", results), ("Raw", results["raw_metrics"])):
        lines.extend(["", f"## {label} Formula Groups", ""])
        if not metrics["by_formula_group_id"]:
            lines.append("No explicit formula_group_id metadata; macro metrics are null.")
            continue
        lines.extend(["| formula_group_id | n | math accuracy | output protocol compliance | parse coverage | math parse coverage |",
                      "| --- | ---: | ---: | ---: | ---: | ---: |"])
        for group_id, stats in metrics["by_formula_group_id"].items():
            lines.append(f"| {group_id} | {stats['n']} | {stats['math_accuracy']:.4f} | {stats['output_protocol_compliance_accuracy']:.4f} | {stats['parse_coverage']:.4f} | {stats['math_parse_coverage']:.4f} |")
    if results["diagnostic_metrics"] is not None:
        diagnostic = results["diagnostic_metrics"]
        lines.extend(["", "## Separate Diagnostics", "",
                      f"- total: {diagnostic['total']}",
                      f"- math_accuracy: {diagnostic['math_accuracy']:.4f}",
                      f"- output_protocol_compliance_accuracy: {diagnostic['output_protocol_compliance_accuracy']:.4f}",
                      f"- raw_math_accuracy: {diagnostic['raw_metrics']['math_accuracy']:.4f}",
                      f"- raw_coverage: {diagnostic['raw_metrics']['coverage']:.4f}",
                      "These rows do not enter primary micro, macro, parse, format, or legacy aggregates."])

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
