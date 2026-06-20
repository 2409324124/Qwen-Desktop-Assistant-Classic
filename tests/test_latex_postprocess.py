import unittest

from training.latex_postprocess import postprocess_latex


class LatexPostprocessTests(unittest.TestCase):
    def test_splits_glued_greek_and_latin_commands(self) -> None:
        self.assertEqual(
            postprocess_latex(r"(\alphau)' = \alpha'u + \alphau'"),
            r"(\alpha u)' = \alpha'u + \alpha u'",
        )
        self.assertEqual(
            postprocess_latex(r"(\phixi)' = \phi'xi + \phixi'"),
            r"(\phi\xi)' = \phi'\xi + \phi\xi'",
        )

    def test_demotes_invalid_single_letter_latex_command(self) -> None:
        self.assertEqual(
            postprocess_latex(r"(\u\gamma)' = \u'\gamma + \u\gamma'"),
            r"(u\gamma)' = u'\gamma + u\gamma'",
        )

    def test_preserves_known_commands_and_text_blocks(self) -> None:
        source = (
            r"\text{Softmax alpha xi}(\xi_{i}) = "
            r"\frac{\exp(\xi_{i})}{\sum_{j} \exp(\xi_{j})} + \mathcal{L}"
        )

        self.assertEqual(postprocess_latex(source), source)


if __name__ == "__main__":
    unittest.main()
