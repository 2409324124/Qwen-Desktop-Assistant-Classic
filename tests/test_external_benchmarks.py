import json
import tempfile
import unittest
from pathlib import Path

from training.evaluate_text_correction import (
    character_error_rate,
    corpus_bleu_4,
    evaluate_text_correction,
    normalized_match,
)
from training.audit_lm_eval_samples import (
    audit_samples,
    classify_failure,
    last_boxed_content,
    looks_truncated,
)
from training.prepare_latexc_benchmark import LatexcConversionError, convert_latexc, detect_fields
from training.prepare_dataset import load_jsonl, write_jsonl
from training.run_lora_inference import expected_from_record, load_eval_lines


class ExternalBenchmarkTests(unittest.TestCase):
    def test_detect_fields_uses_common_latexc_names(self) -> None:
        source, target = detect_fields({"noisy": "x / y", "corrected": r"\frac{x}{y}"})

        self.assertEqual(source, "noisy")
        self.assertEqual(target, "corrected")

    def test_detect_fields_reports_available_fields_when_ambiguous(self) -> None:
        with self.assertRaisesRegex(LatexcConversionError, "Available string fields: a, b"):
            detect_fields({"a": "left", "b": "right"})

    def test_convert_latexc_jsonl_and_csv_to_benchmark_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            data_dir.mkdir()
            write_jsonl(
                data_dir / "sample.jsonl",
                [{"source": "x over y", "target": r"\frac{x}{y}"}],
            )
            (data_dir / "sample.csv").write_text(
                "erroneous,correct\nsqrt x,\\sqrt{x}\n",
                encoding="utf-8",
            )

            summary = convert_latexc(data_dir, root / "latexc_eval.jsonl")
            rows = load_jsonl(root / "latexc_eval.jsonl")
            by_input = {row["input"]: row for row in rows}

            self.assertEqual(summary["total"], 2)
            self.assertEqual(by_input["x over y"]["expected"], r"\frac{x}{y}")
            self.assertEqual(by_input["x over y"]["metadata"]["benchmark"], "latexc")
            self.assertEqual(by_input["sqrt x"]["expected"], r"\sqrt{x}")

    def test_convert_latexc_limit_supports_smoke_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "sample.jsonl"
            write_jsonl(
                source,
                [
                    {"source": "a", "target": "A"},
                    {"source": "b", "target": "B"},
                ],
            )

            summary = convert_latexc(source, root / "out.jsonl", limit=1)

            self.assertEqual(summary["total"], 1)
            self.assertEqual(len(load_jsonl(root / "out.jsonl")), 1)

    def test_text_correction_metrics_cover_exact_bleu_and_cer(self) -> None:
        rows = [
            {"expected": r"\frac{x}{y}", "prediction": r"\frac{x}{y}"},
            {"expected": "x+y", "prediction": "x-y"},
        ]
        results = evaluate_text_correction(rows)

        self.assertEqual(results["total"], 2)
        self.assertEqual(results["exact_accuracy"], 0.5)
        self.assertEqual(results["normalized_accuracy"], 0.5)
        self.assertGreater(results["bleu_4"], 0.0)
        self.assertGreater(results["cer"], 0.0)
        self.assertTrue(normalized_match(r"\frac { x } { y }", r"\frac{x}{y}"))
        self.assertEqual(character_error_rate("abc", "abc"), 0.0)

    def test_corpus_bleu_4_returns_one_for_identical_corpus(self) -> None:
        rows = [{"expected": "abcdef", "prediction": "abcdef"}]

        self.assertEqual(corpus_bleu_4(rows), 1.0)

    def test_run_lora_inference_helpers_support_limit_and_expected_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "eval.jsonl"
            path.write_text(
                "\n".join(
                    json.dumps(row)
                    for row in (
                        {"input": "a", "expected": "A"},
                        {"input": "b", "output": "B"},
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            self.assertEqual(len(load_eval_lines(path, limit=1)), 1)
            self.assertEqual(expected_from_record({"expected": "A"}), "A")
            self.assertEqual(expected_from_record({"output": "B"}), "B")
            with self.assertRaises(ValueError):
                expected_from_record({"input": "missing"})

    def test_lm_eval_sample_audit_detects_extraction_and_truncation_cases(self) -> None:
        self.assertEqual(last_boxed_content(r"final \boxed{\frac{1}{2}}."), r"\frac{1}{2}")
        self.assertTrue(looks_truncated("Final answer: x ="))

        extraction_row = {
            "target": r"\frac{1}{2}",
            "filtered_resps": [r"The final answer is $\frac{1}{2}$."],
            "exact_match": 0,
        }
        truncation_row = {
            "target": "42",
            "filtered_resps": ["We compute the value and get 4 +"],
            "exact_match": 0,
        }

        self.assertEqual(classify_failure(extraction_row), "target_text_present_extraction_issue")
        self.assertEqual(classify_failure(truncation_row), "truncated_or_no_complete_final")

    def test_lm_eval_sample_audit_reads_jsonl_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "samples_hendrycks_math500_2026.jsonl"
            path.write_text(
                "\n".join(
                    json.dumps(row)
                    for row in (
                        {"target": "A", "filtered_resps": ["A"], "exact_match": 1},
                        {"target": "B", "filtered_resps": ["C"], "exact_match": 0},
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            results = audit_samples([path])

        self.assertEqual(results["total"], 2)
        self.assertEqual(results["categories"]["official_correct"], 1)
        self.assertEqual(results["categories"]["no_explicit_final_answer"], 1)


if __name__ == "__main__":
    unittest.main()
