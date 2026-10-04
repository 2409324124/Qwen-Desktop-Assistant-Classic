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
    response_text,
    reliable_last_boxed_content,
)
from training.reevaluate_offline import align_predictions, reevaluate
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

    def test_boxed_extraction_does_not_reuse_an_earlier_box(self) -> None:
        self.assertIsNone(last_boxed_content(r"Intermediate \boxed{42}. Final \boxed{4"))
        self.assertTrue(looks_truncated(r"Intermediate \boxed{42}. Final \boxed{4"))
        self.assertEqual(last_boxed_content(r"First \boxed{1}; final \boxed{\frac{2}{3}}"), r"\frac{2}{3}")

    def test_sample_diagnostics_preserve_case_and_do_not_match_substrings(self) -> None:
        for row in (
            {"target": "42", "resps": [[r"Question mentions 42. Final answer: \boxed{142}"]]},
            {"target": "A", "resps": [[r"Final answer: \boxed{a}"]]},
            {"target": "42", "resps": [[r"Final answer: \boxed{5}"]], "filtered_resps": ["42"]},
        ):
            self.assertNotIn("extraction_issue", classify_failure(row))
        self.assertEqual(response_text({"resps": [["raw"]], "filtered_resps": ["filtered"]}), "raw")

    def test_boxed_suffix_must_not_contain_a_later_claim(self) -> None:
        contradictory = r"Final \boxed{42}" + "\nActually final answer: 43"
        self.assertEqual(last_boxed_content(contradictory), "42")
        self.assertIsNone(reliable_last_boxed_content(contradictory))
        self.assertFalse(looks_truncated(contradictory))
        self.assertEqual(classify_failure({"target": "42", "resps": [[contradictory]], "exact_match": 0}), "boxed_suffix_requires_manual_review")
        self.assertEqual(reliable_last_boxed_content(r"$$\boxed{42}$$."), "42")
        self.assertIsNone(reliable_last_boxed_content(r"\boxed{42} is the correct value."))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "samples_math500_2026.jsonl"
            write_jsonl(path, [{"target": "42", "resps": [[contradictory]], "exact_match": 0}])
            diagnostic = audit_samples([path])["boxed_diagnostics"]
        self.assertEqual(diagnostic["boxed_text_match"], 0)
        self.assertEqual(diagnostic["boxed_suffix_unverified"], 1)
        self.assertEqual(diagnostic["unextractable"], 1)

    def test_boxed_diagnostics_are_a_lower_bound_with_unextractable_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "samples_hendrycks_math500_2026.jsonl"
            write_jsonl(path, [
                {"target": "42", "resps": [[r"Final \boxed{42}"]], "exact_match": 0},
                {"target": "2", "resps": [[r"Final \boxed{12}"]], "exact_match": 0},
                {"target": "A", "resps": [[r"Final \boxed{a}"]], "exact_match": 0},
                {"target": "42", "resps": [[r"Earlier \boxed{42}; final \boxed{4"]], "exact_match": 0},
            ])
            result = audit_samples([path])["boxed_diagnostics"]
        self.assertEqual(result["boxed_text_match"], 1)
        self.assertEqual(result["boxed_text_accuracy_lower_bound"], 0.25)
        self.assertEqual(result["unextractable"], 1)
        self.assertEqual(result["suspected_truncation"], 1)
        self.assertEqual(result["official_correct"], 0)

    def test_full_sample_diagnostics_are_not_limited_by_failure_examples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "samples_math500_2026.jsonl"
            rows = [
                {"doc_id": 3, "doc": {"unique_id": "test/3"}, "target": "42", "resps": [[r"\boxed{42}"]], "exact_match": 0},
                {"doc_id": 4, "doc": {"unique_id": "test/4"}, "target": "5", "resps": [["Final answer: 5 +"]], "exact_match": 0},
            ]
            path.write_text(json.dumps(rows[0]) + "\n\n" + json.dumps(rows[1]) + "\n", encoding="utf-8")
            result = audit_samples([path], max_examples=0)
        self.assertEqual(result["examples"], [])
        diagnostics = result["sample_diagnostics"]
        self.assertEqual(len(diagnostics), 2)
        self.assertEqual([row["source_line"] for row in diagnostics], [1, 3])
        self.assertEqual(diagnostics[0]["unique_id"], "test/3")
        self.assertTrue(diagnostics[0]["boxed_text_match"])
        self.assertEqual(diagnostics[0]["complete_boxed"], "42")
        self.assertEqual(diagnostics[0]["reliable_final_boxed"], "42")
        self.assertFalse(diagnostics[1]["extractable"])
        self.assertTrue(diagnostics[1]["suspected_truncation"])

    def test_offline_alignment_uses_original_gold_to_disambiguate_and_revises_labels(self) -> None:
        accepted = [
            {"input": "same", "output": "x+2", "metadata": {"source_file": "s.jsonl", "formula_name": "F", "source_id": "s:1", "original_output": "x+1"}},
            {"input": "same", "output": "y+1", "metadata": {"source_file": "s.jsonl", "formula_name": "F", "source_id": "s:2", "original_output": "y+1"}},
        ]
        quarantined = [{"input": "ambiguous", "output": "x", "metadata": {"source_file": "s.jsonl", "formula_name": "F", "source_id": "s:3"}}]
        predictions = [
            {"input": "same", "expected": "x+1", "prediction": "x+2", "metadata": {"source_file": "s.jsonl", "formula_name": "F"}},
            {"input": "ambiguous", "expected": "x", "prediction": "x", "metadata": {"source_file": "s.jsonl", "formula_name": "F"}},
        ]
        aligned, audit = align_predictions(predictions, accepted, quarantined, [])
        self.assertEqual(list(aligned), ["s:1"])
        self.assertEqual(aligned["s:1"]["expected"], "x+2")
        self.assertEqual(aligned["s:1"]["historical_expected"], "x+1")
        self.assertEqual([row["status"] for row in audit], ["accepted", "quarantined"])

    def test_offline_alignment_does_not_guess_duplicate_or_unmatched_lineage(self) -> None:
        accepted = [
            {"input": "same", "output": value, "metadata": {"source_file": "s", "formula_name": "F", "source_id": f"s:{n}"}}
            for n, value in enumerate(("x+1", "y+1"), 1)
        ]
        rows = [
            {"input": "same", "expected": "z+1", "prediction": "z+1", "metadata": {"source_file": "s", "formula_name": "F"}},
            {"input": "missing", "expected": "x", "prediction": "x", "metadata": {"source_file": "s", "formula_name": "F"}},
        ]
        aligned, audit = align_predictions(rows, accepted, [], [])
        self.assertEqual(aligned, {})
        self.assertEqual([row["status"] for row in audit], ["ambiguous", "unmatched"])

    def test_offline_reevaluation_uses_shared_samples_and_preserves_historical_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / "v4"
            dataset.mkdir()
            metadata = {"source_file": "source.jsonl", "formula_name": "F", "source_id": "s:1", "original_output": "x+1"}
            write_jsonl(dataset / "latex_formula_train.jsonl", [
                {"input": "x+2", "output": "x+2", "metadata": metadata},
                {"input": "y+1", "output": "y+1", "metadata": {**metadata, "source_id": "s:2", "original_output": "y+1"}},
            ])
            write_jsonl(dataset / "latex_formula_quarantine.jsonl", [])
            write_jsonl(dataset / "review_manifest.jsonl", [{"source_id": "s:1", "original_output": "x+1", "revised_output": "x+2", "action": "replace_output", "reasons": ["restore_explicit_input"]}])
            base = root / "base.jsonl"
            v3 = root / "v3.jsonl"
            row = {"input": "x+2", "expected": "x+1", "prediction": "x+2", "metadata": {"source_file": "source.jsonl", "formula_name": "F"}}
            write_jsonl(base, [{**row, "raw_prediction": "x+1", "postprocessed": True}, {**row, "input": "y+1", "expected": "y+1", "prediction": "y+1"}])
            write_jsonl(v3, [row])
            math_samples = root / "samples_math500_2026.jsonl"
            write_jsonl(math_samples, [{"doc_id": 0, "target": "42", "resps": [[r"\boxed{42}"]], "exact_match": 0}])
            original_files = {path: path.read_bytes() for path in (base, v3)}
            result = reevaluate(dataset, {"base": base, "v3": v3}, root / "reports", [math_samples])
            self.assertEqual(result["shared_accepted_samples"], 1)
            self.assertEqual(result["models"]["base"]["reviewed_shared_metrics"]["raw_metrics"]["math_accuracy"], 0.0)
            self.assertEqual(result["models"]["base"]["reviewed_shared_metrics"]["math_accuracy"], 1.0)
            self.assertEqual(result["models"]["base"]["revised_gold_labels"], 1)
            self.assertEqual(result["models"]["base"]["common_original_gold_metrics"]["math_accuracy"], 0.0)
            self.assertEqual(result["models"]["base"]["gold_change_categories"], {"reviewed_input_restoration": 1})
            self.assertIn("common_original_gold_legacy_diagnostics", result["models"]["base"])
            self.assertTrue((root / "reports/comparison.md").is_file())
            sample_audit = load_jsonl(root / "reports/math500-sample-audit.jsonl")
            self.assertEqual(len(sample_audit), 1)
            self.assertTrue(sample_audit[0]["boxed_text_match"])
            for path, contents in original_files.items():
                self.assertEqual(path.read_bytes(), contents)


if __name__ == "__main__":
    unittest.main()
