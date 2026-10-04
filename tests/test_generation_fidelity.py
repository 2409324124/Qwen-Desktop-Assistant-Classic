import random
import unittest
from unittest.mock import patch

from tools.data_generation import hard_builder, noisy_builder


class GenerationFidelityTests(unittest.TestCase):
    FORMULAS = (
        r"\theta = v_{0} + a T",
        r"z_{k}=\hat{u}_{k}\odot\gamma+\bar{q}_{k}'",
        r"A\times B + C\cdot D + E\otimes F",
        r"L=-1.0\frac{1}{N}\sum_{j=1}^{N}\left[y_j\log(\hat{y}_j)+(1-y_j)\log(1-\hat{y}_j)\right]",
        r"M=\begin{vmatrix}a&b\\c&d\end{vmatrix}+\frac{a}{\frac{b}{c}}",
    )

    def test_surface_helpers_do_not_delete_formula_content(self):
        cases = self.FORMULAS + ("x_i + y_j", "x x", "RMSNorm(x) = x elementwise_mul gamma", "L=-1.0, y_j+h_k")
        for source in cases:
            with self.subTest(source=source):
                self.assertEqual(noisy_builder.sanitize_surface_text(source), source)
                self.assertEqual(noisy_builder.maybe_trim(source, random.Random(0)), source)
                self.assertEqual(noisy_builder.latex_to_ascii_fragment(source), source)

    def test_every_rule_retains_complete_current_formula_and_source_provenance(self):
        for module, weights, selector, key in (
            (noisy_builder, noisy_builder.DEFAULT_RULE_WEIGHTS, "choose_applicable_rule", "noise_rule"),
            (hard_builder, hard_builder.DEFAULT_HARD_RULE_WEIGHTS, "choose_hard_rule", "hard_rule"),
        ):
            for formula in self.FORMULAS:
                source = {"instruction": "restore", "input": "stale context using x and t", "output": formula,
                          "metadata": {"formula_name": "Kinematic Velocity Equation"}}
                for rule in weights:
                    for seed in (0, 1, 4, 10):
                        with self.subTest(module=module.__name__, formula=formula, rule=rule, seed=seed):
                            with patch.object(module, selector, return_value=rule):
                                generated = module.mutate_record(source, random.Random(seed))
                            self.assertIn(formula, generated["input"])
                            self.assertNotIn("v0 a t", generated["input"])
                            self.assertNotIn("stale context", generated["input"])
                            self.assertEqual(generated["output"], formula)
                            self.assertEqual(generated["metadata"]["source_input"], source["input"])
                            self.assertEqual(generated["metadata"][key], rule)
                self.assertEqual(source["input"], "stale context using x and t")

    def test_distinct_symbol_roles_and_operators_cannot_collapse_to_one_input(self):
        formulas = (r"x_{i}\times y_{j}", r"a_{k}\times b_{n}", r"x_{i}\odot y_{j}", r"x_{i}\cdot y_{j}", r"\hat{x}_{i}\times y_{j}")
        for module in (noisy_builder, hard_builder):
            outputs = [module.mutate_record({"instruction": "restore", "input": "formula", "output": formula}, random.Random(42))["input"] for formula in formulas]
            self.assertEqual(len(set(outputs)), len(formulas))


if __name__ == "__main__":
    unittest.main()
