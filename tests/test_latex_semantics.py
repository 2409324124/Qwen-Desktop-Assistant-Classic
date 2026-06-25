import unittest

from training.latex_semantics import canonicalize_latex, compare_latex, compare_latex_math_only, parse_latex


class LatexCanonicalizationTests(unittest.TestCase):
    def test_canonicalize_latex_is_deterministic_and_idempotent(self) -> None:
        source = r"x_i^2 = {a \over b} + \begin{matrix} y_1 & z^3 \\ u & v \end{matrix}"
        expected = (
            r"x_{i}^{2} = \frac{a}{b} + "
            r"\begin{bmatrix} y_{1} & z^{3} \\ u & v \end{bmatrix}"
        )

        canonical = canonicalize_latex(source)

        self.assertEqual(canonical, expected)
        self.assertEqual(canonicalize_latex(canonical), canonical)

    def test_canonicalize_latex_removes_font_only_macros_but_keeps_semantic_modifiers(self) -> None:
        source = r"\mathbf{Q}\boldsymbol{x} + \hat{\mathbf{y}} + \mathcal{L} + \mathbb{E}"

        self.assertEqual(
            canonicalize_latex(source),
            r"Qx + \hat{y} + \mathcal{L} + \mathbb{E}",
        )

    def test_compare_latex_accepts_template_equivalence_but_rejects_wrong_structure(self) -> None:
        equivalent = compare_latex(
            r"L = \frac{1}{N} \sum_{i=1}^{N} (x_i - \hat{x}_i)^2",
            r"L = \sum_{j=1}^{T} (\hat{y}_j - y_j)^2 \frac{1}{T}",
            formula_name="Mean Squared Error",
        )
        wrong = compare_latex(
            r"L = \frac{1}{N} \sum_{i=1}^{N} (x_i - \hat{x}_i)^2",
            r"L = \frac{1}{N} \sum_{i=1}^{N} (x_i - \bar{x})^2",
            formula_name="Mean Squared Error",
        )

        self.assertTrue(equivalent.semantic_match)
        self.assertEqual(equivalent.match_level, "alpha_rename")
        self.assertFalse(wrong.semantic_match)
        self.assertEqual(wrong.match_level, "true_mismatch")

    def test_canonicalize_latex_preserves_escaped_set_braces(self) -> None:
        source = r"\mathcal{L}\{f(t)\}(s) = \int_0^\infty f(t)e^{-st}dt"

        canonical = canonicalize_latex(source)

        self.assertIn(r"\{f(t)\}", canonical)
        self.assertEqual(canonicalize_latex(canonical), canonical)

    def test_parser_accepts_multi_argument_functions_conditionals_and_absolute_values(self) -> None:
        formulas = (
            r"\text{Attention}(Q, K, V) = \text{softmax}(QK^T)V",
            r"f(x|\mu,\sigma^2) = e^{-x^2}",
            r"z = re^{i\phi},\quad r = |z|",
        )

        for formula in formulas:
            with self.subTest(formula=formula):
                self.assertIsNotNone(parse_latex(formula))

    def test_compare_latex_ignores_font_style(self) -> None:
        result = compare_latex(
            r"\text{Attention}(Q, K, V) = \text{softmax}(QK^T)V",
            r"\text{Attention}(\mathbf{Q}, K, \mathbf{V}) = \text{softmax}(\mathbf{Q}K^T)\mathbf{V}",
            formula_name="Self-Attention Mechanism",
        )

        self.assertTrue(result.semantic_match)
        self.assertEqual(result.match_level, "style_only")

    def test_compare_latex_preserves_matrix_multiplication_order(self) -> None:
        result = compare_latex(
            r"\text{Attention}(Q, K, V) = \text{softmax}(QK^T)V",
            r"\text{Attention}(Q, K, V) = \text{softmax}(K^TQ)V",
            formula_name="Self-Attention Mechanism",
        )

        self.assertFalse(result.semantic_match)
        self.assertEqual(result.match_level, "true_mismatch")

    def test_compare_latex_requires_bijective_variable_mapping_and_fixed_constants(self) -> None:
        collapsed = compare_latex("x + y", "y + y")
        replaced_constant = compare_latex(r"A = \pi r^2", r"A = \theta r^2")

        self.assertFalse(collapsed.semantic_match)
        self.assertFalse(replaced_constant.semantic_match)

    def test_math_only_accepts_equivalent_layout_and_operator_forms(self) -> None:
        cases = (
            (r"\Delta S \ge 0", r"\Delta S \geq 0"),
            (r"\int_{-\infty}^{\infty} e^{-x^{2}} dx = \sqrt{\pi}", r"\int_{-\infty}^{\infty} \exp(-x^{2}) \, \mathrm{d}x = \sqrt{\pi}"),
            (r"(\frac{v}{u})' = \frac{v'u - vu'}{u^{2}}", r"\left(\frac{v}{u}\right)^{\prime} = \frac{v^{\prime} u - v u^{\prime}}{u^{2}}"),
            (r"S_{j} = \frac{j}{2}(a_{1} + a_{j})", r"S_{j} = \frac{j(a_{1} + a_{j})}{2}"),
        )

        for expected, prediction in cases:
            with self.subTest(prediction=prediction):
                result = compare_latex_math_only(expected, prediction, input_text=expected)
                self.assertTrue(result.math_match)
                self.assertFalse(result.format_compliant)

    def test_math_only_accepts_correct_formula_with_extra_prefix_but_marks_format_violation(self) -> None:
        result = compare_latex_math_only(
            r"F = k_{e} \frac{q_{1} q_{2}}{d^{2}}",
            r"\text{Coulomb force: } F = k_{e} \frac{q_{1} q_{2}}{d^{2}}",
            input_text="Coulomb force: F = k_e * q1q2 / d^2",
        )

        self.assertTrue(result.math_match)
        self.assertFalse(result.format_compliant)
        self.assertEqual(result.match_level, "contains_correct_formula")

    def test_math_only_accepts_matrix_without_label_but_marks_format_violation(self) -> None:
        result = compare_latex_math_only(
            r"\Sigma = \begin{bmatrix} \sigma_{\phi}^{2} & \rho\sigma_{\phi}\sigma_{\gamma} \\ \rho\sigma_{\phi}\sigma_{\gamma} & \sigma_{\gamma}^{2} \end{bmatrix}",
            r"\begin{bmatrix} \sigma_{\phi}^{2} & \rho\sigma_{\phi}\sigma_{\gamma} \\ \rho\sigma_{\phi}\sigma_{\gamma} & \sigma_{\gamma}^{2} \end{bmatrix}",
            input_text="Cov Mat: Sigma. 2x2. Diag: sigma_phi^2, sigma_gamma^2.",
        )

        self.assertTrue(result.math_match)
        self.assertFalse(result.format_compliant)
        self.assertEqual(result.match_level, "contains_correct_formula")

    def test_math_only_rejects_variable_drift_when_input_names_variables(self) -> None:
        result = compare_latex_math_only(
            r"\text{Softmax}(\xi_{j}) = \frac{\exp(\xi_{j})}{\sum_{j} \exp(\xi_{j})}",
            r"\text{Softmax}(x_{i}) = \frac{\exp(x_{i})}{\sum_{j} \exp(x_{j})}",
            input_text="softmax exp over sum exp [j, sum j, xi_j]",
        )

        self.assertFalse(result.math_match)


if __name__ == "__main__":
    unittest.main()
