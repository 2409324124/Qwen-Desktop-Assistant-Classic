"""Refactoring must preserve every recorded judgment, not only headline scores."""
import hashlib
import json
from pathlib import Path
import unittest

from latex_sft.evaluation.evaluate_latex import evaluate_pairs, load_prediction_rows

ROOT = Path(__file__).resolve().parents[1]


class SavedPredictionParityTests(unittest.TestCase):
    def assert_same_judgments(self, actual, recorded):
        if isinstance(recorded, dict):
            self.assertEqual(actual.keys(), recorded.keys())
            for key in recorded:
                self.assert_same_judgments(actual[key], recorded[key])
        elif isinstance(recorded, list):
            self.assertEqual(len(actual), len(recorded))
            for a, b in zip(actual, recorded):
                self.assert_same_judgments(a, b)
        elif isinstance(recorded, float):
            # Python 3.12 changed float sum rounding; decisions/counts remain exact.
            self.assertAlmostEqual(actual, recorded, places=14)
        else:
            self.assertEqual(actual, recorded)

    def test_all_reviewed_development_judgments_are_unchanged(self):
        development = ROOT / 'reports/v5.2-colab-sft-20261023/development'
        for name in ('base', 'checkpoint-30', 'checkpoint-60'):
            with self.subTest(model=name):
                directory = development / name
                recorded = json.loads((directory / 'metrics.json').read_text())
                actual = evaluate_pairs(load_prediction_rows(directory / 'predictions.jsonl'))
                self.assert_same_judgments(actual, recorded)

    def test_imported_math_evidence_matches_original_exports(self):
        for name, expected_files in (('v52-math-20261023', 6), ('v52-math-long-20261023', 2)):
            with self.subTest(run=name):
                directory = ROOT / 'reports' / name
                manifest = json.loads((directory / 'import-manifest.json').read_text())
                for relative, digest in manifest['files'].items():
                    path = (directory / relative).resolve()
                    self.assertTrue(path.is_relative_to(directory.resolve()))
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest, relative)
                self.assertEqual(len(list((directory / 'results').rglob('samples_*.jsonl'))), expected_files)


if __name__ == '__main__':
    unittest.main()
