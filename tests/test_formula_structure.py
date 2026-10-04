import unittest

from training.formula_structure import structural_signatures
from training.latex_semantics import compare_latex_math_only


class FormulaStructureTests(unittest.TestCase):
    def signature(self, formula, key='structural_signature'):
        result = structural_signatures(formula)
        self.assertTrue(result['parse_success'], result)
        self.assertIsNotNone(result[key])
        return result[key]

    def test_grouping_alpha_rename_does_not_loosen_scoring(self):
        self.assertEqual(self.signature('x+y'), self.signature('a+b'))
        self.assertFalse(compare_latex_math_only('x+y', 'a+b').math_match)
        self.assertNotEqual(self.signature('x+x'), self.signature('a+b'))

    def test_parameter_template_only_abstracts_safe_number_roles(self):
        self.assertNotEqual(self.signature('2*x^{2}'), self.signature('3*a^{3}'))
        self.assertEqual(self.signature('2*x^{2}', 'template_signature'), self.signature('3*a^{3}', 'template_signature'))
        for left, right in [('x+0', 'a+2'), ('-1*x', '-2*a'), ('-1*x', '1*a'), ('x^{1}', 'a^{2}'), ('x^{2.5}', 'a^{3.5}'), ('x_{2}', 'a_{3}'), ('x^{y+2}', 'a^{b+3}'), (r'x^{\frac{2}{3}}', r'a^{\frac{3}{4}}')]:
            self.assertNotEqual(self.signature(left, 'template_signature'), self.signature(right, 'template_signature'))
        self.assertNotEqual(self.signature(r'\sum_{k=1}^{2}x_{k}', 'template_signature'), self.signature(r'\sum_{j=1}^{3}a_{j}', 'template_signature'))

    def test_numeric_template_requires_a_coefficient_or_literal_integer_power_parent(self):
        for left, right in [('x+2', 'a+3'), (r'\frac{x}{2}', r'\frac{a}{3}'),
                            (r'\frac{x}{2*y^{2}}', r'\frac{a}{3*b^{3}}'),
                            (r'\frac{2*x}{y+2}', r'\frac{3*a}{b+3}'),
                            ('x^{y+2*z^{2}}', 'a^{b+3*c^{3}}'), ('2', '3')]:
            self.assertNotEqual(self.signature(left, 'template_signature'), self.signature(right, 'template_signature'))
        for left, right in [('2*x+4', '3*a+4'), ('2*(x+4)', '3*(a+4)'),
                            (r'\frac{2*x}{y+4}', r'\frac{3*a}{b+4}'),
                            ('x^{-2}', 'a^{-3}')]:
            self.assertEqual(self.signature(left, 'template_signature'), self.signature(right, 'template_signature'))

    def test_index_constants_are_alpha_variables_without_erasing_true_constants(self):
        for left, right in [('x_i', 'a_j'), ('x_e', 'a_k'),
                            ('x_i+y_i', 'a_j+b_j'), ('x_i+i', 'a_j+i'),
                            ('x_e+e^{i}', 'a_k+e^{i}'), ('x_k+k', 'a_j+j')]:
            self.assertEqual(self.signature(left), self.signature(right))
        for left, right in [('x_i+y_i', 'a_j+b_k'), ('x_i+i', 'a_j+j'),
                            ('x_e+e', 'a_j+j'), ('x_i+e^{i}', 'a_j+b^{k}')]:
            self.assertNotEqual(self.signature(left), self.signature(right))
        self.assertFalse(compare_latex_math_only('x_i', 'a_j').math_match)

    def test_constants_operator_types_order_and_matrix_types_survive(self):
        for left, right in [(r'e+x', 'a+b'), (r'i+x', 'a+b'), (r'\pi+x', 'a+b'), ('A+B=AB', 'A+B=BA'), (r'a\times b+a', r'b\times a+a'), (r'a\times b', r'a\odot b'), (r'a\times(b\times c)', r'(a\times b)\times c')]:
            self.assertNotEqual(self.signature(left), self.signature(right))
        matrix = r'\begin{bmatrix}a&b\\c&d\end{bmatrix}'
        det = matrix.replace('bmatrix', 'vmatrix')
        self.assertNotEqual(self.signature(matrix), self.signature(det))

    def test_limit_binding_scope_and_capture_are_explicit(self):
        left = r'\lim_{h\to 0}\frac{f(x+h)-f(x)}{h}'
        right = r'\lim_{u\to 0}\frac{g(a+u)-g(a)}{u}'
        self.assertEqual(self.signature(left), self.signature(right))
        self.assertTrue(compare_latex_math_only(left, r'\lim_{u\to 0}\frac{f(x+u)-f(x)}{u}').math_match)
        self.assertNotEqual(self.signature(r'\lim_{h\to 0}(x+h)'), self.signature(r'\lim_{x\to 0}(x+x)'))
        self.assertNotEqual(self.signature(r'\lim_{h\to 2}x', 'template_signature'), self.signature(r'\lim_{u\to 3}a', 'template_signature'))
        self.assertFalse(compare_latex_math_only(r'\lim_{h\to 0}(x+h)+h', r'\lim_{u\to 0}(x+u)+u').math_match)

    def test_arbitrary_functions_have_a_separate_alpha_namespace(self):
        self.assertEqual(self.signature('f(x)+x'), self.signature('g(a)+a'))
        self.assertNotEqual(self.signature('f(x)+f'), self.signature('g(a)+a'))
        self.assertEqual(self.signature(r'f\left(x\right)+x'), self.signature('g(a)+a'))
        self.assertNotEqual(self.signature(r'\sin(x)'), self.signature(r'\cos(a)'))

    def test_failure_is_closed_and_evidence_is_deterministic(self):
        for value in (r'\frac{x}{', r'\int_{0}^{1}f(x)dx', r'\lim_{h+k\to 0}x', r'\unknowncommand{x}'):
            result = structural_signatures(value)
            self.assertFalse(result['parse_success'])
            self.assertIsNone(result['structural_signature'])
            self.assertIsNone(result['template_signature'])
        self.assertEqual(structural_signatures('x+y'), structural_signatures('x+y'))


if __name__ == '__main__':
    unittest.main()
