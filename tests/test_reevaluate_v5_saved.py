from pathlib import Path
import json
import shutil
import tempfile
import unittest

from training.reevaluate_v5_saved import reassess

FIXTURES = Path(__file__).resolve().parents[1]/'training/reviews/v5_predictions'


class SavedReassessmentTests(unittest.TestCase):
    def test_actual_saved_generations_only_change_four_force_judgments_per_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'result'; report=reassess(FIXTURES,output)
            self.assertEqual(report['changed_judgments'],12)
            changed=[json.loads(line) for line in (output/'changed_judgments.jsonl').read_text().splitlines()]
            ids={model:{r['source_id'] for r in changed if r['model']==model} for model in report['models']}
            self.assertEqual(len(ids['base']),4)
            self.assertTrue(all(s==ids['base'] for s in ids.values()))
            self.assertTrue(all(not r['old_math_match'] and r['new_math_match'] for r in changed))
            self.assertEqual(report['models']['base']['new_same_labels_64']['raw_metrics']['math_match'],29)
            self.assertEqual(report['models']['checkpoint-66']['new_same_labels_64']['raw_metrics']['math_match'],45)
            for model in report['models'].values():
                self.assertEqual(model['new_reviewed_subset_57']['raw_metrics']['total'],57)
            with self.assertRaises(ValueError):reassess(FIXTURES,output)

    def test_modified_predictions_fail_before_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); fixtures=root/'inputs';shutil.copytree(FIXTURES,fixtures)
            with (fixtures/'base-predictions.jsonl').open('a') as f:f.write('\n')
            with self.assertRaisesRegex(ValueError,'fixture mismatch'):reassess(fixtures,root/'result')
            self.assertFalse((root/'result').exists())


if __name__=='__main__':unittest.main()
