import unittest

from training.latex_semantics import canonicalize_latex, canonicalize_latex_faithful, compare_latex, compare_latex_math_only, parse_latex


class LatexCanonicalizationTests(unittest.TestCase):
    def test_scalar_force_fraction_regrouping_reproduces_four_audited_cases(self) -> None:
        cases = (
            ("Newton's Law of Universal Gravitation", r"F = G \frac{M \mu}{d^{2}}", r"F = \frac{G M \mu}{d^{2}}"),
            ("Newton's Law of Universal Gravitation", r"F = G \frac{m_{0} m}{R^{2}}", r"F = \frac{G m_{0} m}{R^{2}}"),
            ("Coulomb's Law", r"F = k_{e} \frac{q_{1} q_{2}}{r^{2}}", r"F = \frac{k_{e} q_{1} q_{2}}{r^{2}}"),
            ("Coulomb's Law", r"F = k_{e} \frac{q_{1} q_{2}}{R^{2}}", r"F = \frac{k_{e} q_{1} q_{2}}{R^{2}}"),
        )
        for family, expected, prediction in cases:
            for left, right in ((expected, prediction), (prediction, expected)):
                with self.subTest(family=family, prediction=right):
                    result = compare_latex_math_only(left, right, formula_name=family)
                    self.assertTrue(result.math_match)
                    self.assertFalse(result.format_compliant)

    def test_scalar_fraction_regrouping_preserves_fidelity_and_domain(self) -> None:
        expected = r"F = G \frac{M m}{r^{2}}"
        invalid = (
            r"F = \frac{G M m}{R^{2}}", r"F = \frac{G M m}{r^{3}}",
            r"F = \frac{G M n}{r^{2}}", r"F = \frac{G M}{m r^{2}}",
            r"F = -\frac{G M m}{r^{2}}", r"F = \frac{2 G M m}{r^{2}}",
            r"\frac{G M m}{r^{2}}", r"F = \frac{\mathbf{G} M m}{r^{2}}",
            r"F = \frac{G M m}{r^{2}}" + "\nF=0",
        )
        for prediction in invalid:
            with self.subTest(prediction=prediction):
                self.assertFalse(compare_latex_math_only(expected, prediction, formula_name="Newton's Law of Universal Gravitation").math_match)
        self.assertFalse(compare_latex_math_only(r"G\frac{r}{r}", "G", formula_name="Coulomb's Law").math_match)

    def test_scalar_fraction_regrouping_is_scoped_and_keeps_operators(self) -> None:
        cases = (
            (r"G\frac{a b}{r^2}", r"\frac{G a b}{r^2}", None),
            (r"G\frac{\mathbf{A}\mathbf{B}}{r^2}", r"\frac{G\mathbf{A}\mathbf{B}}{r^2}", "Coulomb's Law"),
            (r"G\frac{a}{\begin{bmatrix}r\end{bmatrix}}", r"\frac{Ga}{\begin{bmatrix}r\end{bmatrix}}", "Coulomb's Law"),
            (r"G\frac{a\times b}{r^2}", r"\frac{Ga\times b}{r^2}", "Coulomb's Law"),
            (r"G\frac{a b}{r^2}", r"\frac{G b a}{r^2}", "Newton's Law of Universal Gravitation"),
            (r"G\frac{\sum_{i=1}^{N} x_i}{r^2}", r"\frac{G\sum_{j=1}^{N} x_j}{r^2}", "Coulomb's Law"),
        )
        for expected, prediction, family in cases:
            with self.subTest(prediction=prediction):
                self.assertFalse(compare_latex_math_only(expected, prediction, formula_name=family).math_match)

    def test_primary_metric_preserves_free_symbols_constants_and_operators(self) -> None:
        cases = (
            ("x+y", "a+b"), (r"e^{x}", r"a^{x}"), (r"e^{ix}", r"e^{jx}"),
            ("AB", "BA"), (r"a \times b", "ab"), (r"A \odot B", "AB"),
            (r"\mathbb{R}", "R"), (r"\mathcal{L}", "L"),
            (r"\begin{vmatrix}a&b\\c&d\end{vmatrix}", r"\begin{bmatrix}a&b\\c&d\end{bmatrix}"),
            ("x=1", "x=1\nx=2"), ("x=1", "x=1\nx=1"),
            (r"x^{2}", r"x^{1}^{2}"), (r"\text{Mass}", r"\text{mass}"),
        )
        for expected, prediction in cases:
            with self.subTest(prediction=prediction):
                self.assertFalse(compare_latex_math_only(expected, prediction).math_match)

    def test_primary_metric_renames_only_locally_bound_variables(self) -> None:
        expected = r"\sum_{i=1}^{N} x_{i}"
        self.assertTrue(compare_latex_math_only(expected, r"\sum_{j=1}^{N} x_{j}").math_match)
        self.assertFalse(compare_latex_math_only(expected, r"\sum_{j=1}^{M} x_{j}").math_match)
        self.assertFalse(compare_latex_math_only(expected + "+i", r"\sum_{j=1}^{N} x_{j}+j").math_match)
        self.assertFalse(compare_latex_math_only(r"\sum_{i=1}^{N} (x_{i}+j)", r"\sum_{j=1}^{N} (x_{j}+j)").math_match)

    def test_primary_metric_marks_unsupported_formulas_unverified(self) -> None:
        result = compare_latex_math_only(r"\frac{x}{y}", r"\frac{x}{")
        self.assertFalse(result.math_match)
        self.assertEqual(result.verification_status, "unverified")

    def test_primary_metric_preserves_explicit_operator_order_even_in_scalar_family(self) -> None:
        for operator in (r"\times", r"\odot"):
            self.assertFalse(compare_latex_math_only("a" + operator + " b", "b" + operator + " a", formula_name="Product Rule").math_match)

    def test_primary_metric_preserves_explicit_product_grouping(self) -> None:
        # A cross product is not associative; unknown operator types provide
        # no license to erase their parentheses.
        for operator in (r"\times", r"\odot", r"\cdot"):
            left = "a" + operator + "(b" + operator + " c)"
            right = "(a" + operator + " b)" + operator + " c"
            self.assertFalse(compare_latex_math_only(left, right).math_match)
            self.assertTrue(compare_latex_math_only(left, left).math_match)

    def test_primary_metric_preserves_determinant_but_accepts_layout_variations(self) -> None:
        determinant = r"\begin{vmatrix}a&b\\c&d\end{vmatrix}"
        self.assertTrue(compare_latex_math_only(determinant, r"\left[" + determinant + r"\right]").math_match)
        self.assertTrue(compare_latex_math_only(r"x_i + y", r"y+x_{i}").math_match)

    def test_safe_canonicalizer_preserves_types_fonts_operators_and_scope(self) -> None:
        original = r"\mathbb{R} + \mathbf{x}_i + \begin{vmatrix}a&b\\c&d\end{vmatrix} + a\times(b\times c)"
        normalized = canonicalize_latex_faithful(original)
        self.assertIn(r"\mathbb{R}", normalized)
        self.assertIn(r"\mathbf{x}_{i}", normalized)
        self.assertIn(r"\begin{vmatrix}", normalized)
        self.assertIn(r"a\times(b\times c)", normalized)
        self.assertTrue(compare_latex_math_only(original, normalized).math_match)
        self.assertEqual(canonicalize_latex_faithful(normalized), normalized)
        self.assertEqual(canonicalize_latex_faithful(r"{a \over b} + x_i"), r"\frac{a}{b} + x_{i}")
        self.assertIn(r"\leftarrow", canonicalize_latex_faithful(r"x\leftarrow y"))

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

    def test_math_only_does_not_drop_matrix_equation_label(self) -> None:
        result = compare_latex_math_only(
            r"\Sigma = \begin{bmatrix} \sigma_{\phi}^{2} & \rho\sigma_{\phi}\sigma_{\gamma} \\ \rho\sigma_{\phi}\sigma_{\gamma} & \sigma_{\gamma}^{2} \end{bmatrix}",
            r"\begin{bmatrix} \sigma_{\phi}^{2} & \rho\sigma_{\phi}\sigma_{\gamma} \\ \rho\sigma_{\phi}\sigma_{\gamma} & \sigma_{\gamma}^{2} \end{bmatrix}",
            input_text="Cov Mat: Sigma. 2x2. Diag: sigma_phi^2, sigma_gamma^2.",
        )

        self.assertFalse(result.math_match)
        self.assertFalse(result.format_compliant)
        self.assertEqual(result.verification_status, "unverified")

    def test_math_only_rejects_variable_drift_when_input_names_variables(self) -> None:
        result = compare_latex_math_only(
            r"\text{Softmax}(\xi_{j}) = \frac{\exp(\xi_{j})}{\sum_{j} \exp(\xi_{j})}",
            r"\text{Softmax}(x_{i}) = \frac{\exp(x_{i})}{\sum_{j} \exp(x_{j})}",
            input_text="softmax exp over sum exp [j, sum j, xi_j]",
        )

        self.assertFalse(result.math_match)


if __name__ == "__main__":
    unittest.main()
