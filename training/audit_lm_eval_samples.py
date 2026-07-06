import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


CORRECT_METRICS = ("exact_match", "acc", "acc_norm", "flexible-extract", "prompt_level_strict_acc")


def normalize_answer(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("\\left", "").replace("\\right", "")
    text = re.sub(r"\s+", "", text)
    text = text.strip("`$ .。；;，,")
    return text


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
    return rows


def response_text(row: dict[str, Any]) -> str:
    filtered = row.get("filtered_resps")
    if isinstance(filtered, list) and filtered:
        return str(filtered[0])
    responses = row.get("resps")
    if isinstance(responses, list) and responses:
        first = responses[0]
        if isinstance(first, list) and first:
            return str(first[0])
        return str(first)
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


def last_boxed_content(text: str) -> str | None:
    matches = list(re.finditer(r"\\boxed\s*\{", text))
    for match in reversed(matches):
        start = match.end()
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
                    return text[start:index]
            index += 1
    return None


def looks_truncated(text: str) -> bool:
    stripped = text.rstrip()
    if not stripped:
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
    normalized_response = normalize_answer(response)
    normalized_target = normalize_answer(target)
    boxed = last_boxed_content(response)

    if normalized_target and normalized_target in normalized_response:
        return "target_text_present_extraction_issue"
    if boxed is not None and normalize_answer(boxed) == normalized_target:
        return "boxed_answer_present_extraction_issue"
    if looks_truncated(response):
        return "truncated_or_no_complete_final"
    if "\\boxed" not in response and "final" not in response.lower() and "answer" not in response.lower():
        return "no_explicit_final_answer"
    return "wrong_answer_or_needs_manual_review"


def audit_samples(paths: list[Path], max_examples: int = 20) -> dict[str, Any]:
    totals: Counter[str] = Counter()
    by_task: dict[str, Counter[str]] = defaultdict(Counter)
    examples: list[dict[str, Any]] = []

    for path in paths:
        task = task_name_from_path(path)
        for row in read_jsonl(path):
            category = "official_correct" if official_correct(row) else classify_failure(row)
            totals[category] += 1
            by_task[task][category] += 1
            if category != "official_correct" and len(examples) < max_examples:
                examples.append(
                    {
                        "task": task,
                        "doc_id": row.get("doc_id"),
                        "category": category,
                        "target": target_text(row),
                        "prediction": response_text(row),
                    }
                )

    return {
        "total": sum(totals.values()),
        "categories": dict(sorted(totals.items())),
        "by_task": {task: dict(sorted(counter.items())) for task, counter in sorted(by_task.items())},
        "examples": examples,
    }


def write_markdown(results: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# lm-eval Sample Audit",
        "",
        "This is a diagnostic audit over `--log_samples` JSONL files. It does not replace official lm-eval metrics.",
        "",
        f"- total: {results['total']}",
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
    print(json.dumps({k: v for k, v in results.items() if k != "examples"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
