import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


CORRECT_METRICS = ("exact_match", "acc", "acc_norm", "flexible-extract", "prompt_level_strict_acc")


def normalize_answer(value: Any) -> str:
    text = str(value if value is not None else "").strip()
    if text.endswith(("$.", r"\].", r"\).", "`.")):
        text = text[:-1].rstrip()
    for opening, closing in (("$$", "$$"), ("$", "$"), (r"\[", r"\]"), (r"\(", r"\)"), ("`", "`")):
        if text.startswith(opening) and text.endswith(closing) and len(text) >= len(opening) + len(closing):
            text = text[len(opening):-len(closing)].strip()
            break
    text = re.sub(r"\\(?:left|right)(?![A-Za-z])", "", text)
    return re.sub(r"\s+", "", text)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [row for _, row in _read_jsonl_with_lines(path)]


def _read_jsonl_with_lines(path: Path) -> list[tuple[int, dict[str, Any]]]:
    rows: list[tuple[int, dict[str, Any]]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                rows.append((line_number, json.loads(line)))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
    return rows


def response_text(row: dict[str, Any]) -> str:
    responses = row.get("resps")
    if isinstance(responses, list) and responses:
        first = responses[0]
        if isinstance(first, list) and first:
            return str(first[0])
        return str(first)
    filtered = row.get("filtered_resps")
    if isinstance(filtered, list) and filtered:
        return str(filtered[0])
    return ""


def target_text(row: dict[str, Any]) -> str:
    if "target" in row:
        return str(row["target"])
    doc = row.get("doc")
    if isinstance(doc, dict):
        for key in ("answer", "target", "label"):
            if key in doc:
                return str(doc[key])
    return ""


def task_name_from_path(path: Path) -> str:
    name = path.name
    if name.startswith("samples_"):
        name = name[len("samples_") :]
    return name.split("_20", 1)[0]


def official_correct(row: dict[str, Any]) -> bool:
    for key in CORRECT_METRICS:
        value = row.get(key)
        if isinstance(value, bool):
            if value:
                return True
        elif isinstance(value, (int, float)) and value >= 1:
            return True
    return False


def _last_boxed_group(text: str) -> tuple[str, int] | None:
    matches = list(re.finditer(r"\\boxed\s*\{", text))
    if not matches:
        return None
    start = matches[-1].end()
    depth = 1
    index = start
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index], index + 1
        index += 1
    return None


def last_boxed_content(text: str) -> str | None:
    group = _last_boxed_group(text)
    return group[0] if group is not None else None


def reliable_last_boxed_content(text: str) -> str | None:
    group = _last_boxed_group(text)
    if group is None:
        return None
    content, end = group
    suffix = re.sub(r"\\[\]\)]", "", text[end:])
    if not re.fullmatch(r"[\s$`*_.。;,，:：!！?？)\]}-]*", suffix):
        return None
    return content


def looks_truncated(text: str) -> bool:
    stripped = text.rstrip()
    if not stripped:
        return True
    if re.search(r"\\boxed\s*\{", stripped) and last_boxed_content(stripped) is None:
        return True
    if stripped[-1] in "=+-*/([{,<>":
        return True
    if stripped.count("$$") % 2:
        return True
    if stripped.count("\\[") != stripped.count("\\]"):
        return True
    return False


def classify_failure(row: dict[str, Any]) -> str:
    if official_correct(row):
        return "official_correct"

    response = response_text(row)
    target = target_text(row)
    normalized_target = normalize_answer(target)
    boxed = reliable_last_boxed_content(response)

    if boxed is not None and normalized_target and normalize_answer(boxed) == normalized_target:
        return "boxed_answer_present_extraction_issue"
    if last_boxed_content(response) is not None and boxed is None:
        return "boxed_suffix_requires_manual_review"
    final = re.search(r"\b(?:final\s+answer|answer)\s*(?:is|:|=)\s*(.+)\Z", response, re.IGNORECASE | re.DOTALL)
    explicit_answer = final.group(1) if final else response
    if normalized_target and normalize_answer(explicit_answer) == normalized_target:
        return "target_text_present_extraction_issue"
    if looks_truncated(response):
        return "truncated_or_no_complete_final"
    if "\\boxed" not in response and "final" not in response.lower() and "answer" not in response.lower():
        return "no_explicit_final_answer"
    return "wrong_answer_or_needs_manual_review"


def audit_samples(paths: list[Path], max_examples: int = 20) -> dict[str, Any]:
    totals: Counter[str] = Counter()
    by_task: dict[str, Counter[str]] = defaultdict(Counter)
    examples: list[dict[str, Any]] = []
    sample_diagnostics: list[dict[str, Any]] = []
    boxed_counts: Counter[str] = Counter()

    for path in paths:
        task = task_name_from_path(path)
        for source_line, row in _read_jsonl_with_lines(path):
            response = response_text(row)
            boxed = reliable_last_boxed_content(response)
            complete = last_boxed_content(response)
            target = normalize_answer(target_text(row))
            boxed_counts["total"] += 1
            boxed_counts["official_correct"] += int(official_correct(row))
            boxed_counts["complete_boxed"] += int(complete is not None)
            boxed_counts["reliable_final_boxed"] += int(boxed is not None)
            boxed_counts["boxed_suffix_unverified"] += int(complete is not None and boxed is None)
            boxed_counts["unextractable"] += int(boxed is None)
            boxed_counts["boxed_text_match"] += int(boxed is not None and bool(target) and normalize_answer(boxed) == target)
            boxed_counts["suspected_truncation"] += int(looks_truncated(response))
            category = "official_correct" if official_correct(row) else classify_failure(row)
            sample_diagnostics.append({
                "source_path": str(path.resolve()),
                "source_line": source_line,
                "task": task,
                "doc_id": row.get("doc_id"),
                "unique_id": (row.get("doc") or {}).get("unique_id", row.get("unique_id")),
                "target": target_text(row),
                "complete_boxed": complete,
                "reliable_final_boxed": boxed,
                "category": category,
                "suspected_truncation": looks_truncated(response),
                "extractable": boxed is not None,
                "boxed_text_match": boxed is not None and bool(target) and normalize_answer(boxed) == target,
                "official_correct": official_correct(row),
            })
            totals[category] += 1
            by_task[task][category] += 1
            if category != "official_correct" and len(examples) < max_examples:
                examples.append(
                    {
                        "task": task,
                        "doc_id": row.get("doc_id"),
                        "category": category,
                        "target": target_text(row),
                        "prediction": response,
                        "final_boxed": boxed,
                        "suspected_truncation": looks_truncated(response),
                    }
                )

    return {
        "total": sum(totals.values()),
        "categories": dict(sorted(totals.items())),
        "by_task": {task: dict(sorted(counter.items())) for task, counter in sorted(by_task.items())},
        "examples": examples,
        "sample_diagnostics": sample_diagnostics,
        "boxed_diagnostics": {
            **{key: boxed_counts[key] for key in ("total", "official_correct", "complete_boxed", "reliable_final_boxed", "boxed_suffix_unverified", "boxed_text_match", "unextractable", "suspected_truncation")},
            "boxed_text_accuracy_lower_bound": boxed_counts["boxed_text_match"] / boxed_counts["total"] if boxed_counts["total"] else 0.0,
            "interpretation": "Case-sensitive final-boxed text matches are an extraction diagnostic lower bound, not a replacement mathematical accuracy. Only presentation wrappers, punctuation, and whitespace may follow a reliable final box; other suffixes require manual review. Unextractable answers are not necessarily wrong; truncation is only suspected without finish reasons or token counts.",
        },
    }


def write_markdown(results: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# lm-eval Sample Audit",
        "",
        "This is a diagnostic audit over `--log_samples` JSONL files. It does not replace official lm-eval metrics.",
        "",
        f"- total: {results['total']}",
        f"- final boxed text matches: {results['boxed_diagnostics']['boxed_text_match']}",
        f"- boxed text match lower bound: {results['boxed_diagnostics']['boxed_text_accuracy_lower_bound']:.4f}",
        f"- unextractable final boxed: {results['boxed_diagnostics']['unextractable']}",
        f"- boxed suffix requires manual review: {results['boxed_diagnostics']['boxed_suffix_unverified']}",
        f"- suspected truncation: {results['boxed_diagnostics']['suspected_truncation']}",
        "",
        results['boxed_diagnostics']['interpretation'],
        "",
        "## Categories",
        "",
        "| category | count |",
        "| --- | ---: |",
    ]
    for category, count in results["categories"].items():
        lines.append(f"| {category} | {count} |")

    lines.extend(["", "## By Task", "", "| task | category | count |", "| --- | --- | ---: |"])
    for task, stats in results["by_task"].items():
        for category, count in stats.items():
            lines.append(f"| {task} | {category} | {count} |")

    lines.extend(["", "## Failure Samples", ""])
    for index, sample in enumerate(results["examples"], 1):
        prediction = str(sample["prediction"]).replace("`", "\\`")
        target = str(sample["target"]).replace("`", "\\`")
        lines.extend(
            [
                f"### {index}. {sample['task']} doc_id={sample['doc_id']}",
                "",
                f"- category: `{sample['category']}`",
                f"- target: `{target}`",
                f"- prediction: `{prediction[:2000]}`",
                "",
            ]
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit lm-eval --log_samples JSONL files.")
    parser.add_argument("samples", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="Markdown audit report path.")
    parser.add_argument("--json", type=Path, help="Optional JSON audit summary path.")
    parser.add_argument("--max-examples", type=int, default=20)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = audit_samples(args.samples, max_examples=args.max_examples)
    write_markdown(results, args.output)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in results.items() if k not in {"examples", "sample_diagnostics"}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
