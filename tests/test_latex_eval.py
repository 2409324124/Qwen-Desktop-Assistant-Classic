import unittest

from training.evaluate_latex import evaluate_pairs, normalize_latex


class LatexEvaluationTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
