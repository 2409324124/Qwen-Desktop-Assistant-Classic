import unittest
import json
import tempfile
from pathlib import Path

from training.prepare_dataset import dedupe_records, split_grouped_records, load_sources


def record(input_text, output, family, source_id, **metadata):
    return {
        'instruction': 'Repair the formula', 'input': input_text, 'output': output,
        'canonical_output': output,
        'metadata': {'formula_name': family, 'source_id': source_id,
                     'original_output': output, 'category': 'math', **metadata},
    }


class DatasetGroupingTests(unittest.TestCase):
    def assert_same_group_for_all_seeds(self, rows, first_id, second_id):
        for seed in range(12):
            train, dev, test, leakage, counts = split_grouped_records(rows, seed=seed)
            assignments = {r['metadata']['source_id']: r['metadata']['formula_group_id']
                           for split in (train, dev, test) for r in split}
            self.assertEqual(assignments[first_id], assignments[second_id], f'seed={seed}')
            self.assertTrue(all(v == 0 for v in leakage.values()), leakage)

    def extras(self):
        return [record('extra'+str(i), 'target'+str(i), 'Family'+str(i), 'extra:'+str(i))
                for i in range(8)]

    def test_loading_new_generator_rows_does_not_require_lossy_cached_canonical(self):
        source = record('x_i', r"\mathbf{x}_i + \begin{vmatrix}a&b\\c&d\end{vmatrix}", 'A', 'a')
        source.pop('canonical_output')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'source.jsonl').write_text(json.dumps(source)+'\n', encoding='utf-8')
            rows = load_sources(root, (('new', 'source.jsonl'),))
        self.assertIn(r"\mathbf{x}_{i}", rows[0]['output'])
        self.assertIn(r"\begin{vmatrix}", rows[0]['output'])
        self.assertIsNone(rows[0]['metadata']['original_canonical_output'])
        self.assertEqual(rows[0]['metadata']['original_output'], source['output'])

    def test_duplicate_pair_keeps_both_families_and_all_source_lineage(self):
        rows = [record('same', 'p', 'A', 'a'),
                record('same', 'p', 'B', 'duplicate:b', source_input='ancestor',
                       formula_id='template:b', source_path='original.jsonl', source_line=8),
                record('variant B', 'q', 'B', 'b'), *self.extras()]
        unique, removed = dedupe_records(rows)
        self.assertEqual(removed, 1)
        self.assert_same_group_for_all_seeds(unique, 'a', 'b')
        sources = unique[0]['metadata']['source_records']
        duplicate = next(s for s in sources if s['metadata']['source_id'] == 'duplicate:b')
        self.assertEqual(duplicate['metadata']['formula_id'], 'template:b')
        self.assertEqual(duplicate['metadata']['source_input'], 'ancestor')
        self.assertEqual(duplicate['metadata']['source_line'], 8)
        self.assertEqual(duplicate['output'], 'p')

    def test_original_target_and_revised_target_share_equation_namespace(self):
        rows = [record('first input', 'revised', 'A', 'a', original_output='original'),
                record('second input', 'original', 'B', 'b', original_output='another original'), *self.extras()]
        self.assert_same_group_for_all_seeds(rows, 'a', 'b')

    def test_ancestor_input_and_descendant_source_input_share_namespace(self):
        rows = [record('ancestor', 'p', 'A', 'a'),
                record('descendant', 'q', 'B', 'b', source_input='ancestor'), *self.extras()]
        self.assert_same_group_for_all_seeds(rows, 'a', 'b')

    def test_duplicate_original_target_and_source_input_remain_group_edges(self):
        rows = [record('same', 'p', 'A', 'a'),
                record('same', 'p', 'B', 'duplicate:b', source_input='ancestor',
                       original_output='original', formula_id='template:b'),
                record('ancestor', 'q', 'C', 'c'),
                record('different', 'original', 'D', 'd'),
                record('lineage variant', 'u', 'E', 'e', formula_id='template:b'),
                *self.extras()]
        unique, removed = dedupe_records(rows)
        for second in ('c', 'd', 'e'):
            self.assert_same_group_for_all_seeds(unique, 'a', second)


if __name__ == '__main__':
    unittest.main()
