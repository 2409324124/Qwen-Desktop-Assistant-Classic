from pathlib import Path
import tempfile
import unittest

from training.evaluate_latex import evaluate_pairs, normalize_latex, is_output_protocol_compliant, write_report


class LatexEvaluationTests(unittest.TestCase):
    def test_group_macro_weights_formulas_equally_for_processed_and_raw(self) -> None:
        rows = [{"input": "x+y", "expected": "x+y", "prediction": "x+y", "metadata": {"formula_group_id": "large"}} for _ in range(3)]
        rows[0].update(raw_prediction="x-y", postprocessed=True)
        rows.append({"input": "x+y", "expected": "x+y", "prediction": "x-y", "metadata": {"formula_group_id": "small"}})
        result = evaluate_pairs(rows)
        self.assertEqual(result["math_accuracy"], 0.75)
        self.assertEqual(result["micro_math_accuracy"], 0.75)
        self.assertEqual(result["macro_math_accuracy"], 0.5)
        self.assertEqual(result["grouped_coverage"], 1.0)
        self.assertEqual(result["group_count"], 2)
        self.assertEqual(result["by_formula_group_id"]["large"]["n"], 3)
        self.assertEqual(result["by_formula_group_id"]["small"]["math_accuracy"], 0.0)
        self.assertEqual(result["by_formula_group_id"]["small"]["output_protocol_compliance_accuracy"], 1.0)
        self.assertEqual(result["raw_metrics"]["micro_math_accuracy"], 0.5)
        self.assertAlmostEqual(result["raw_metrics"]["macro_math_accuracy"], 1 / 3)
        self.assertEqual(result["postprocessed_metrics"]["macro_math_accuracy"], 0.5)
        self.assertEqual(result["macro_output_protocol_compliance_accuracy"], 1.0)
        self.assertEqual(result["macro_parse_coverage"], 1.0)
        self.assertEqual(result["raw_metrics"]["macro_math_parse_coverage"], 1.0)

    def test_ungrouped_samples_do_not_create_macro_denominators(self) -> None:
        row = {"input": "x+y", "expected": "x+y", "prediction": "x+y", "metadata": {"formula_name": "F"}}
        historical = evaluate_pairs([row])
        self.assertIsNone(historical["macro_math_accuracy"])
        self.assertIsNone(historical["raw_metrics"]["macro_math_accuracy"])
        self.assertEqual(historical["grouped_coverage"], 0.0)
        self.assertEqual(historical["by_formula_group_id"], {})
        partial = evaluate_pairs([row, {**row, "prediction": "x-y", "metadata": {"formula_group_id": "g"}}])
        self.assertEqual(partial["math_accuracy"], 0.5)
        self.assertEqual(partial["macro_math_accuracy"], 0.0)
        self.assertEqual(partial["grouped_samples"], 1)
        self.assertEqual(partial["grouped_coverage"], 0.5)
        self.assertEqual(partial["group_count"], 1)

    def test_diagnostic_rows_never_change_primary_micro_or_macro(self) -> None:
        primary = {"input": "x+y", "expected": "x+y", "prediction": "x-y", "metadata": {"formula_group_id": "primary"}}
        diagnostic = {"input": "x+y", "expected": "x+y", "prediction": "x+y", "metadata": {"formula_group_id": "boundary", "formula_name": "Symbol Boundary", "evaluation_role": "diagnostic"}}
        result = evaluate_pairs([primary, diagnostic])
        self.assertEqual(result["input_total"], 2)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["diagnostic_total"], 1)
        self.assertEqual(result["math_accuracy"], 0.0)
        self.assertEqual(result["macro_math_accuracy"], 0.0)
        self.assertEqual(set(result["by_formula_group_id"]), {"primary"})
        self.assertEqual(result["raw_metrics"]["total"], 1)
        self.assertEqual(result["raw_metrics"]["coverage"], 1.0)
        self.assertEqual(result["diagnostic_metrics"]["math_accuracy"], 1.0)
        self.assertEqual(result["diagnostic_metrics"]["raw_metrics"]["total"], 1)
        only_diagnostic = evaluate_pairs([diagnostic])
        self.assertEqual(only_diagnostic["total"], 0)
        self.assertIsNone(only_diagnostic["macro_math_accuracy"])
        self.assertEqual(only_diagnostic["raw_metrics"]["coverage"], 0.0)

    def test_report_renders_grouped_and_separate_diagnostic_metrics(self) -> None:
        result = evaluate_pairs([
            {"input": "x", "expected": "x", "prediction": "x", "metadata": {"formula_group_id": "g"}},
            {"input": "x", "expected": "x", "prediction": "x", "metadata": {"evaluation_role": "diagnostic"}},
        ])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "eval.md"
            write_report(result, path)
            report = path.read_text(encoding="utf-8")
        self.assertIn("macro_math_accuracy: 1.0000", report)
        self.assertIn("## Postprocessed Formula Groups", report)
        self.assertIn("## Raw Formula Groups", report)
        self.assertIn("| g | 1 | 1.0000", report)
        self.assertIn("## Separate Diagnostics", report)

    def test_raw_group_coverage_excludes_unrecoverable_raw_predictions(self) -> None:
        result = evaluate_pairs([
            {"input": "x", "expected": "x", "prediction": "x", "metadata": {"formula_group_id": "missing"}, "postprocessed": True},
            {"input": "x", "expected": "x", "prediction": "x", "metadata": {"formula_group_id": "available"}},
        ])
        self.assertEqual(result["group_count"], 2)
        self.assertEqual(result["raw_metrics"]["coverage"], 0.5)
        self.assertEqual(result["raw_metrics"]["group_count"], 1)
        self.assertEqual(set(result["raw_metrics"]["by_formula_group_id"]), {"available"})

    def test_output_protocol_is_independent_of_mathematical_correctness(self) -> None:
        results = evaluate_pairs([{'input': 'x plus y', 'expected': 'x+y', 'prediction': 'x-y'}])
        self.assertEqual(results['math_accuracy'], 0.0)
        self.assertEqual(results['format_compliance_accuracy'], 0.0)
        self.assertEqual(results['output_protocol_compliance_accuracy'], 1.0)
        self.assertEqual(results['raw_metrics']['output_protocol_compliance_accuracy'], 1.0)
        self.assertFalse(is_output_protocol_compliant(r"\text{Result:} x+y"))
        self.assertFalse(is_output_protocol_compliant("Here is x+y"))
        self.assertFalse(is_output_protocol_compliant(r"\[x+y\]"))

    def test_output_protocol_requires_braced_scripts_and_preserves_determinants(self) -> None:
        self.assertFalse(is_output_protocol_compliant('x_i'))
        self.assertTrue(is_output_protocol_compliant('x_{i}'))
        self.assertFalse(is_output_protocol_compliant('x/y'))
        self.assertTrue(is_output_protocol_compliant(r"\frac{x}{y}"))
        self.assertTrue(is_output_protocol_compliant(r"\begin{vmatrix}a&b\\c&d\end{vmatrix}"))
        self.assertFalse(is_output_protocol_compliant(r"\begin{pmatrix}a&b\\c&d\end{pmatrix}"))

    def test_reports_raw_and_postprocessed_metrics_and_legacy_diagnostics(self) -> None:
        results = evaluate_pairs([{
            "input": "x", "expected": "x", "raw_prediction": "```latex\nx\n```",
            "prediction": "x", "postprocessed": True,
        }, {"input": "x+y", "expected": "x+y", "prediction": "a+b"}])
        self.assertEqual(results["primary_metric"], "faithful_math_accuracy")
        self.assertEqual(results["math_accuracy"], 0.5)
        self.assertEqual(results["raw_metrics"]["exact_accuracy"], 0.0)
        self.assertEqual(results["postprocessed_metrics"]["exact_accuracy"], 0.5)
        self.assertEqual(results["raw_metrics"]["math_accuracy"], 0.0)
        self.assertEqual(results["unverified"], 1)
        self.assertEqual(results["legacy_diagnostics"]["semantic_accuracy"], 1.0)

    def test_unknown_raw_output_is_not_counted_as_raw_measurement(self) -> None:
        results = evaluate_pairs([{"input": "x", "expected": "x", "prediction": "x", "postprocessed": True}])
        self.assertEqual(results["raw_metrics"]["total"], 0)
        self.assertEqual(results["raw_metrics"]["coverage"], 0.0)
        self.assertEqual(results["postprocessed_metrics"]["math_accuracy"], 1.0)

    def test_normalize_latex_removes_layout_noise(self) -> None:
        left = r"\left( \frac{ x }{ y } \right)"
        right = r"(\frac{x}{y})"
        self.assertEqual(normalize_latex(left), normalize_latex(right))

    def test_evaluate_pairs_reports_exact_and_normalized_accuracy(self) -> None:
        results = evaluate_pairs(
            [
                {
                    "input": "fraction x over y",
                    "expected": r"\frac{x}{y}",
                    "prediction": r"\frac{ x }{ y }",
                    "metadata": {"dataset_layer": "clean"},
                },
                {
                    "input": "bad",
                    "expected": "x = y",
                    "prediction": "x = z",
                    "metadata": {"dataset_layer": "hard"},
                },
            ]
        )

        self.assertEqual(results["total"], 2)
        self.assertEqual(results["exact_match"], 0)
        self.assertEqual(results["normalized_match"], 1)
        self.assertEqual(results["by_layer"]["clean"]["normalized_accuracy"], 1.0)
        self.assertEqual(results["by_layer"]["hard"]["normalized_accuracy"], 0.0)
        self.assertEqual(results["semantic_match"], 2)
        self.assertEqual(results["semantic_accuracy"], 1.0)

    def test_evaluate_pairs_uses_semantic_accuracy_as_primary_metric(self) -> None:
        results = evaluate_pairs(
            [
                {
                    "input": "generic product rule",
                    "expected": r"(u\gamma)' = u'\gamma + u\gamma'",
                    "prediction": r"(\gamma u)' = \gamma'u + \gamma u'",
                    "metadata": {"dataset_layer": "clean", "formula_name": "Product Rule"},
                },
                {
                    "input": "attention",
                    "expected": r"\text{Attention}(Q,K,V)=\text{softmax}(QK^T)V",
                    "prediction": r"\text{Attention}(Q,K,V)=\text{softmax}(K^TQ)V",
                    "metadata": {"dataset_layer": "hard", "formula_name": "Self-Attention Mechanism"},
                },
            ]
        )

        self.assertEqual(results["exact_accuracy"], 0.0)
        self.assertEqual(results["semantic_accuracy"], 0.5)
        self.assertEqual(results["match_levels"]["commutative_reorder"], 1)
        self.assertEqual(results["match_levels"]["true_mismatch"], 1)
        self.assertEqual(len(results["failures"]), 1)

    def test_evaluate_pairs_reports_math_only_and_format_compliance_separately(self) -> None:
        results = evaluate_pairs(
            [
                {
                    "input": "Coulomb force: F = k_e * q1q2 / d^2",
                    "expected": r"F = k_{e} \frac{q_{1} q_{2}}{d^{2}}",
                    "prediction": r"\text{Coulomb force: } F = k_{e} \frac{q_{1} q_{2}}{d^{2}}",
                    "metadata": {"dataset_layer": "clean", "formula_name": "Coulomb's Law"},
                },
                {
                    "input": "softmax exp over sum exp [j, sum j, xi_j]",
                    "expected": r"\text{Softmax}(\xi_{j}) = \frac{\exp(\xi_{j})}{\sum_{j} \exp(\xi_{j})}",
                    "prediction": r"\text{Softmax}(x_{i}) = \frac{\exp(x_{i})}{\sum_{j} \exp(x_{j})}",
                    "metadata": {"dataset_layer": "hard", "formula_name": "Softmax Function"},
                },
            ]
        )

        self.assertEqual(results["math_match"], 1)
        self.assertEqual(results["format_compliance_match"], 0)
        self.assertEqual(results["math_accuracy"], 0.5)
        self.assertEqual(results["format_compliance_accuracy"], 0.0)
        self.assertEqual(results["math_match_levels"]["contains_correct_formula"], 1)
        self.assertEqual(results["math_match_levels"]["math_mismatch"], 1)
        self.assertEqual(len(results["math_failures"]), 1)


if __name__ == "__main__":
    unittest.main()
