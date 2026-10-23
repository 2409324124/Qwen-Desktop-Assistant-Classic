import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from tqdm.auto import tqdm


def normalize_formula_text(value: str) -> str:
    return re.sub(r"\s+", "", value.strip())


def exact_match(expected: str, prediction: str) -> bool:
    return expected.strip() == prediction.strip()


def normalized_match(expected: str, prediction: str) -> bool:
    return normalize_formula_text(expected) == normalize_formula_text(prediction)


def _levenshtein_distance(source: str, target: str) -> int:
    if source == target:
        return 0
    if not source:
        return len(target)
    if not target:
        return len(source)
    previous = list(range(len(target) + 1))
    for source_index, source_char in enumerate(source, 1):
        current = [source_index]
        for target_index, target_char in enumerate(target, 1):
            current.append(
                min(
                    previous[target_index] + 1,
                    current[target_index - 1] + 1,
                    previous[target_index - 1] + int(source_char != target_char),
                )
            )
        previous = current
    return previous[-1]


def character_error_rate(expected: str, prediction: str) -> float:
    expected_normalized = normalize_formula_text(expected)
    prediction_normalized = normalize_formula_text(prediction)
    if not expected_normalized:
        return 0.0 if not prediction_normalized else 1.0
    return _levenshtein_distance(expected_normalized, prediction_normalized) / len(expected_normalized)


def _tokens(value: str, tokenizer: str) -> list[str]:
    normalized = normalize_formula_text(value)
    if tokenizer == "char":
        return list(normalized)
    if tokenizer == "whitespace":
        return value.strip().split()
    raise ValueError(f"Unsupported BLEU tokenizer: {tokenizer}")


def _ngrams(tokens: list[str], n: int) -> Counter[tuple[str, ...]]:
    return Counter(tuple(tokens[index : index + n]) for index in range(len(tokens) - n + 1))


def corpus_bleu_4(rows: list[dict[str, str]], *, tokenizer: str = "char") -> float:
    clipped_matches = [0, 0, 0, 0]
    total_predictions = [0, 0, 0, 0]
    prediction_length = 0
    expected_length = 0

    for row in rows:
        expected_tokens = _tokens(row["expected"], tokenizer)
        prediction_tokens = _tokens(row["prediction"], tokenizer)
        expected_length += len(expected_tokens)
        prediction_length += len(prediction_tokens)
        for n in range(1, 5):
            prediction_ngrams = _ngrams(prediction_tokens, n)
            expected_ngrams = _ngrams(expected_tokens, n)
            total_predictions[n - 1] += sum(prediction_ngrams.values())
            clipped_matches[n - 1] += sum(
                min(count, expected_ngrams[ngram])
                for ngram, count in prediction_ngrams.items()
            )

    if prediction_length == 0:
        return 0.0
    precisions = [
        clipped_matches[index] / total_predictions[index]
        if total_predictions[index] else 0.0
        for index in range(4)
    ]
    if min(precisions) == 0.0:
        return 0.0
    brevity_penalty = 1.0 if prediction_length > expected_length else math.exp(1 - expected_length / prediction_length)
    return brevity_penalty * math.exp(sum(math.log(precision) for precision in precisions) / 4)


def load_prediction_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            payload = json.loads(line)
            missing = {"expected", "prediction"} - set(payload)
            if missing:
                raise ValueError(f"{path}:{line_number}: missing fields: {', '.join(sorted(missing))}")
            rows.append(payload)
    return rows


def evaluate_text_correction(
    rows: list[dict[str, Any]],
    *,
    show_progress: bool = False,
    bleu_tokenizer: str = "char",
) -> dict[str, Any]:
    total = len(rows)
    exact = 0
    normalized = 0
    cer_sum = 0.0
    failures: list[dict[str, Any]] = []
    bleu_rows: list[dict[str, str]] = []

    for row in tqdm(rows, desc="Evaluating text correction", unit="formula", disable=not show_progress):
        expected = str(row["expected"])
        prediction = str(row["prediction"])
        is_exact = exact_match(expected, prediction)
        is_normalized = normalized_match(expected, prediction)
        exact += int(is_exact)
        normalized += int(is_normalized)
        cer = character_error_rate(expected, prediction)
        cer_sum += cer
        bleu_rows.append({"expected": expected, "prediction": prediction})
        if not is_normalized:
            failures.append(
                {
                    "input": row.get("input", ""),
                    "expected": expected,
                    "prediction": prediction,
                    "cer": cer,
                    "metadata": row.get("metadata", {}),
                }
            )

    return {
        "total": total,
        "exact_match": exact,
        "normalized_match": normalized,
        "exact_accuracy": exact / total if total else 0.0,
        "normalized_accuracy": normalized / total if total else 0.0,
        "bleu_4": corpus_bleu_4(bleu_rows, tokenizer=bleu_tokenizer) if total else 0.0,
        "bleu_tokenizer": bleu_tokenizer,
        "cer": cer_sum / total if total else 0.0,
        "failures": failures,
    }


def write_report(results: dict[str, Any], output_path: Path, max_failures: int = 20) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Text Correction Benchmark Evaluation",
        "",
        f"- total: {results['total']}",
        f"- exact_accuracy: {results['exact_accuracy']:.4f}",
        f"- normalized_accuracy: {results['normalized_accuracy']:.4f}",
        f"- bleu_4: {results['bleu_4']:.4f}",
        f"- bleu_tokenizer: {results['bleu_tokenizer']}",
        f"- cer: {results['cer']:.4f}",
        "",
        "## Failure Samples",
        "",
    ]
    for index, failure in enumerate(results["failures"][:max_failures], 1):
        lines.extend(
            [
                f"### {index}",
                "",
                f"- input: {failure['input']}",
                f"- expected: `{failure['expected']}`",
                f"- prediction: `{failure['prediction']}`",
                f"- cer: {failure['cer']:.4f}",
                "",
            ]
        )
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate formula/text correction predictions with EM, BLEU-4, and CER.")
    parser.add_argument("--predictions", type=Path, required=True, help="JSONL with expected and prediction fields.")
    parser.add_argument("--report", type=Path, default=Path("reports/text-correction-eval.md"))
    parser.add_argument("--json", type=Path, default=None, help="Optional JSON metrics output path.")
    parser.add_argument("--bleu-tokenizer", choices=("char", "whitespace"), default="char")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = evaluate_text_correction(
        load_prediction_rows(args.predictions),
        show_progress=True,
        bleu_tokenizer=args.bleu_tokenizer,
    )
    write_report(results, args.report)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in results.items() if key != "failures"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
