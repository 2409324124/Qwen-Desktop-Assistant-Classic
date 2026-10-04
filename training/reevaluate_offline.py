from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from training.audit_lm_eval_samples import audit_samples, read_jsonl, write_markdown
from training.evaluate_latex import evaluate_pairs, load_prediction_rows, write_report
from training.latex_postprocess import postprocess_latex
from training.latex_semantics import canonicalize_latex


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREDICTIONS = {
    "base": ROOT / "reports/qwen3-4b-latex-correction-base-clean-v4-predictions.jsonl",
    "v3": ROOT / "reports/qwen3-4b-latex-correction-lora-v3-clean-v4-predictions.jsonl",
}


def selector(row: dict[str, Any]) -> tuple[str, str, str]:
    metadata = row.get("metadata") or {}
    return str(metadata.get("source_file", "")), str(row["input"]), str(metadata.get("formula_name", ""))


def target_key(value: str) -> str:
    try:
        value = canonicalize_latex(postprocess_latex(value))
    except ValueError:
        pass
    return re.sub(r"\s+", "", value)


def gold_change_category(original: str, revised: str, decision: dict[str, Any]) -> str:
    if original == revised:
        return "unchanged"
    if target_key(original) == target_key(revised):
        return "normalization"
    reasons = decision.get("reasons", [])
    if any(str(reason).startswith("restore_") for reason in reasons):
        return "reviewed_input_restoration"
    return "unverified_change"


def align_predictions(
    rows: list[dict[str, Any]],
    accepted: list[dict[str, Any]],
    quarantined: list[dict[str, Any]],
    manifest: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    decisions = {str(row["source_id"]): row for row in manifest if row.get("source_id")}
    candidates: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    seen: set[str] = set()
    for status, records in (("accepted", accepted), ("quarantined", quarantined)):
        for record in records:
            metadata = record.get("metadata") or {}
            source_id = str(metadata.get("source_id") or record.get("source_id") or "")
            if not source_id:
                raise ValueError("Reviewed records must have metadata.source_id")
            if source_id in seen:
                raise ValueError(f"Duplicate reviewed source_id: {source_id}")
            seen.add(source_id)
            decision = decisions.get(source_id, {})
            revised = str(record.get("canonical_output") or record.get("output") or record.get("expected") or "")
            original = str(metadata.get("original_output") or decision.get("original_output") or revised)
            candidates[selector(record)].append({
                "source_id": source_id,
                "status": status,
                "record": record,
                "expected": revised,
                "aliases": {target_key(original), target_key(revised), target_key(str(metadata.get("original_canonical_output") or original)), target_key(str(decision.get("revised_output") or revised))},
                "decision": decision,
            })

    aligned: dict[str, dict[str, Any]] = {}
    audit: list[dict[str, Any]] = []
    for line, row in enumerate(rows, 1):
        choices = candidates.get(selector(row), [])
        if len(choices) > 1:
            matches = [candidate for candidate in choices if target_key(str(row["expected"])) in candidate["aliases"]]
            if len(matches) == 1:
                choices = matches
        entry: dict[str, Any] = {
            "historical_line": line,
            "input": row["input"],
            "historical_expected": row["expected"],
            "source_file": selector(row)[0],
            "formula_name": selector(row)[2],
            "status": "unmatched" if not choices else "ambiguous" if len(choices) > 1 else choices[0]["status"],
            "candidate_source_ids": [candidate["source_id"] for candidate in choices],
        }
        if len(choices) == 1:
            candidate = choices[0]
            source_id = candidate["source_id"]
            change_category = gold_change_category(str(row["expected"]), candidate["expected"], candidate["decision"])
            entry.update({
                "source_id": source_id,
                "revised_expected": candidate["expected"],
                "gold_text_changed": str(row["expected"]) != candidate["expected"],
                "gold_changed": target_key(str(row["expected"])) != target_key(candidate["expected"]),
                "gold_change_category": change_category,
                "mathematical_difference_proven": False,
                "historical_gold_matches_review_alias": target_key(str(row["expected"])) in candidate["aliases"],
                "review_action": candidate["decision"].get("action"),
                "review_reasons": candidate["decision"].get("reasons", candidate["decision"].get("reason", [])),
            })
            if candidate["status"] == "accepted":
                if source_id in aligned:
                    raise ValueError(f"Multiple historical predictions map to the same source_id: {source_id}")
                aligned[source_id] = {
                    **row,
                    "expected": candidate["expected"],
                    "historical_expected": row["expected"],
                    "historical_line": line,
                    "gold_change_category": change_category,
                    "review_reasons": entry["review_reasons"],
                    "metadata": {**(row.get("metadata") or {}), **(candidate["record"].get("metadata") or {})},
                }
        audit.append(entry)
    return aligned, audit


def load_reviewed_dataset(directory: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[Path]]:
    if not directory.is_dir():
        raise ValueError(f"Reviewed dataset directory does not exist: {directory}")
    accepted: list[dict[str, Any]] = []
    quarantined: list[dict[str, Any]] = []
    files = [directory / f"latex_formula_{name}.jsonl" for name in ("train", "eval", "test", "quarantine") if (directory / f"latex_formula_{name}.jsonl").is_file()]
    if not files:
        raise ValueError(f"No reviewed latex_formula_*.jsonl files: {directory}")
    for path in files:
        destination = quarantined if "quarantine" in path.stem else accepted
        destination.extend(read_jsonl(path))
    manifest_path = directory / "review_manifest.jsonl"
    if not manifest_path.is_file():
        raise ValueError(f"Reviewed dataset manifest does not exist: {manifest_path}")
    return accepted, quarantined, read_jsonl(manifest_path), [*files, manifest_path]


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def reevaluate(
    dataset_dir: Path,
    predictions: dict[str, Path],
    output_dir: Path,
    math_samples: list[Path],
) -> dict[str, Any]:
    accepted, quarantined, manifest, dataset_files = load_reviewed_dataset(dataset_dir)
    historical: dict[str, list[dict[str, Any]]] = {}
    aligned: dict[str, dict[str, dict[str, Any]]] = {}
    audits: dict[str, list[dict[str, Any]]] = {}
    for model, path in predictions.items():
        if not re.fullmatch(r"[A-Za-z0-9_-]+", model):
            raise ValueError(f"Invalid model label: {model}")
        historical[model] = load_prediction_rows(path)
        aligned[model], audits[model] = align_predictions(historical[model], accepted, quarantined, manifest)
    common = set.intersection(*(set(rows) for rows in aligned.values()))
    if not common:
        raise ValueError("No shared accepted samples could be aligned across the historical models")
    first = next(iter(aligned))
    source_ids = [source_id for source_id in aligned[first] if source_id in common]
    output_dir = output_dir.resolve()
    inputs = [*dataset_files, *predictions.values(), *math_samples]
    for path in inputs:
        if output_dir == path.resolve() or output_dir in path.resolve().parents:
            raise ValueError(f"Output directory contains an input artifact: {path}")
    output_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {
        "protocol": "Retrospective re-evaluation of saved generations with faithful scoring and reviewed labels; no inference or training was run. These historical samples are not the independent v4 validation/test splits.",
        "dataset_dir": str(dataset_dir.resolve()),
        "shared_accepted_samples": len(source_ids),
        "input_artifacts": [{"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in inputs],
        "models": {},
    }
    lines = ["# Historical offline re-evaluation", "", summary["protocol"], "", f"Shared accepted samples: {len(source_ids)}", "",
             "All columns below use the same saved generations and the same shared accepted samples. Legacy semantic scoring is a diagnostic and retains the old permissive alpha-renaming policy.", "",
             "| model | legacy original gold (diagnostic) | faithful original gold | faithful reviewed gold | raw faithful reviewed gold | processed exact reviewed gold | unverified reviewed gold |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    alignment_lines = ["", "## Alignment and label review", "",
                       "Label text changes include layout normalization. Reviewed input restorations are identified by manifest restore_* reasons; an unverified comparison is not proof that two formulas differ mathematically.", "",
                       "| model | historical | accepted | quarantined | unmatched / ambiguous | label text changes | reviewed input restorations | normalization / unverified changes |",
                       "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    historical_lines = ["", "## Original complete historical split", "",
                        "These rows include every original historical sample and retain the original labels. Their denominators differ from the reviewed shared subset above; the legacy diagnostic reproduces the old headline score without editing the old reports.", "",
                        "| model | samples | legacy semantic (diagnostic) | faithful original gold |",
                        "| --- | ---: | ---: | ---: |"]
    for model, rows in aligned.items():
        selected = [rows[source_id] for source_id in source_ids]
        metrics = evaluate_pairs(selected)
        common_original = evaluate_pairs([{**row, "expected": row["historical_expected"]} for row in selected])
        original_metrics = evaluate_pairs(historical[model])
        counts = Counter(entry["status"] for entry in audits[model])
        changes = Counter(row["gold_change_category"] for row in selected if row["gold_change_category"] != "unchanged")
        revised_count = changes["reviewed_input_restoration"]
        summary["models"][model] = {
            "historical_total": len(historical[model]),
            "alignment_counts": dict(counts),
            "shared_accepted_total": len(selected),
            "revised_gold_labels": revised_count,
            "gold_text_changes": sum(changes.values()),
            "gold_change_categories": dict(changes),
            "gold_change_interpretation": "restore_* manifest reasons identify input-grounded label restorations; normalization and unverified changes are listed separately. No mathematical difference is claimed proven from string inequality or an unverified rule result.",
            "historical_labels_faithful_metrics": original_metrics,
            "historical_legacy_diagnostics": original_metrics["legacy_diagnostics"],
            "common_original_gold_metrics": common_original,
            "common_original_gold_legacy_diagnostics": common_original["legacy_diagnostics"],
            "reviewed_shared_metrics": metrics,
        }
        write_jsonl(output_dir / f"{model}-alignment.jsonl", audits[model])
        write_jsonl(output_dir / f"{model}-accepted-predictions.jsonl", selected)
        write_json(output_dir / f"{model}-metrics.json", metrics)
        write_json(output_dir / f"{model}-original-gold-shared-metrics.json", common_original)
        write_report(metrics, output_dir / f"{model}-eval.md")
        lines.append(f"| {model} | {common_original['legacy_diagnostics']['semantic_accuracy']:.2%} | {common_original['math_accuracy']:.2%} | {metrics['math_accuracy']:.2%} | {metrics['raw_metrics']['math_accuracy']:.2%} | {metrics['exact_accuracy']:.2%} | {metrics['unverified']} |")
        alignment_lines.append(f"| {model} | {len(historical[model])} | {counts['accepted']} | {counts['quarantined']} | {counts['unmatched']} / {counts['ambiguous']} | {sum(changes.values())} | {revised_count} | {changes['normalization']} / {changes['unverified_change']} |")
        historical_lines.append(f"| {model} | {len(historical[model])} | {original_metrics['legacy_diagnostics']['semantic_accuracy']:.2%} | {original_metrics['math_accuracy']:.2%} |")
    lines.extend(alignment_lines)
    lines.extend(historical_lines)
    if math_samples:
        math_audit = audit_samples(math_samples)
        summary["math500_diagnostics"] = math_audit["boxed_diagnostics"]
        write_json(output_dir / "math500-audit.json", math_audit)
        write_jsonl(output_dir / "math500-sample-audit.jsonl", math_audit["sample_diagnostics"])
        write_markdown(math_audit, output_dir / "math500-audit.md")
        lines.extend(["", "## MATH-500 extraction diagnostics", "", math_audit["boxed_diagnostics"]["interpretation"], "",
                      f"Official correct: {math_audit['boxed_diagnostics']['official_correct']}/{math_audit['total']}; final boxed text matches: {math_audit['boxed_diagnostics']['boxed_text_match']}/{math_audit['total']}; unextractable: {math_audit['boxed_diagnostics']['unextractable']}; nontrivial boxed suffix requiring review: {math_audit['boxed_diagnostics']['boxed_suffix_unverified']}; suspected truncation: {math_audit['boxed_diagnostics']['suspected_truncation']}."])
    else:
        summary["math500_diagnostics"] = None
    write_json(output_dir / "summary.json", summary)
    (output_dir / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-evaluate historical saved generations against reviewed v4 data without running inference.")
    parser.add_argument("--dataset-dir", type=Path, default=ROOT / "training/data/v4")
    parser.add_argument("--predictions", action="append", metavar="NAME=PATH", help="Model label and historical prediction JSONL; repeat for paired comparisons. Defaults to saved Base and v3.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports/offline-v4")
    parser.add_argument("--math-samples", nargs="+", type=Path, help="Logged MATH-500 JSONL files; defaults to the formal vLLM run when present.")
    args = parser.parse_args()
    predictions = DEFAULT_PREDICTIONS
    if args.predictions:
        predictions = {}
        for item in args.predictions:
            if "=" not in item:
                parser.error("--predictions must be NAME=PATH")
            name, path = item.split("=", 1)
            if name in predictions:
                parser.error(f"Duplicate model label: {name}")
            predictions[name] = Path(path)
    math_samples = args.math_samples if args.math_samples is not None else sorted((ROOT / "benchmark_artifacts/remote-20260706-vllm-formal").rglob("samples_hendrycks_math500*.jsonl"))
    summary = reevaluate(args.dataset_dir, predictions, args.output_dir, math_samples)
    print(json.dumps({"shared_accepted_samples": summary["shared_accepted_samples"], "models": {name: {"math_accuracy": value["reviewed_shared_metrics"]["math_accuracy"], "raw_math_accuracy": value["reviewed_shared_metrics"]["raw_metrics"]["math_accuracy"], "alignment_counts": value["alignment_counts"]} for name, value in summary["models"].items()}, "math500_diagnostics": summary["math500_diagnostics"], "output_dir": str(args.output_dir.resolve())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
