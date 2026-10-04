import random
import tempfile
import unittest
from pathlib import Path

from training.review_dataset import review_records
from training.prepare_dataset import build_datasets, load_jsonl, write_jsonl
from tools.data_generation.mine_sympy import build_templates, allocate_symbols
from tools.data_generation.noisy_builder import apply_keyword_shorthand, apply_partial_formula_reference


def record(text, output, family='Example', layer='clean', source='source.jsonl:1'):
    return {'instruction': 'restore', 'input': text, 'output': output,
            'canonical_output': output, 'metadata': {'formula_name': family,
                'category': 'stats_ml', 'dataset_layer': layer, 'source_id': source}}


class DatasetV4Tests(unittest.TestCase):
    def test_review_isolates_ambiguous_and_conflicting_labels(self):
        rows = [record('Sample Mean 那个式子', r'\bar{x}=x', 'Sample Mean'),
                record('x+y', 'x+y', source='a:1'), record('x+y', 'x-y', source='a:2')]
        accepted, quarantined, decisions = review_records(rows)
        self.assertEqual(accepted, [])
        self.assertEqual(len(quarantined), 3)
        self.assertTrue(all(x['reason'] for x in decisions))
        self.assertEqual(rows[0]['output'], r'\bar{x}=x')

    def test_review_repairs_only_explicit_bce_grouping(self):
        bad = r'L = -\frac{1}{N}\sum_{i=1}^{N} y_{i}\log(\hat{y}_{i})+(1-y_{i})\log(1-\hat{y}_{i})'
        rows = [record('L = -1/N * sum(y_i*log(yhat_i) + (1-y_i)*log(1-yhat_i) for i in range(1,N+1))', bad, 'Cross-Entropy Loss'),
                record('cross entropy loss', bad, 'Cross-Entropy Loss', source='a:2')]
        accepted, quarantined, decisions = review_records(rows)
        self.assertEqual(len(accepted), 1)
        self.assertEqual(len(quarantined), 1)
        self.assertIn(r'\sum_{i=1}^{N} [', accepted[0]['output'])
        self.assertTrue(accepted[0]['output'].endswith(']'))
        self.assertEqual(decisions[0]['action'], 'replace_output')
        self.assertEqual(rows[0]['output'], bad)

    def test_review_rejects_variable_collisions(self):
        rows = [record('sum_N', r'\sum_{N=1}^{N} x_{N}', 'Sample Mean'),
                record('RMSNorm(gamma)', r'\text{RMSNorm}(\gamma)=\gamma\odot\gamma', 'RMSNorm', source='a:2')]
        accepted, quarantined, _ = review_records(rows)
        self.assertEqual(len(accepted), 0)
        self.assertEqual(len(quarantined), 2)

    def test_index_restoration_preserves_free_indices_and_avoids_capture(self):
        cases = [record('a_j = sum(x_i for i in range(1,N+1))',r'a_{j}=\sum_{j=1}^{N}x_{j}','Sample Mean'),
                 record('L = sum(x_j+z_j for j in range(1,N+1))',r'L=\sum_{i=1}^{N}(x_{i}+z_{j})','Sample Mean')]
        for row in cases:
            accepted, held, _ = review_records([row])
            self.assertFalse(accepted)
            self.assertEqual(held[0]['output'],row['output'])

    def test_sum_operand_is_not_a_binder(self):
        row = record('L = -1/N * sum(y[i]*log(y_hat[i])+(1-y[i])*log(1-y_hat[i]) for i from 1 to N)',
                     r'L=-\frac{1}{N}\sum_{i=1}^{N}y_{i}\log(\hat{y}_{i})+(1-y_{i})\log(1-\hat{y}_{i})', 'Cross-Entropy Loss')
        accepted,_,_=review_records([row])
        self.assertEqual(len(accepted),1)
        self.assertIn(r'\sum_{i=1}',accepted[0]['output'])
        self.assertNotIn(r'\sum_{y=1}',accepted[0]['output'])

    def test_bce_comment_group_cannot_supply_sum_scope(self):
        row=record('L = -1/N sum_i y_i*log(y_hat_i)+(1-y_i)*log(1-y_hat_i); note ((1-y_i)+log(y_hat_i)+log(1-y_hat_i))',
                   r'L=-\frac{1}{N}\sum_{i=1}^{N}y_{i}\log(\hat{y}_{i})+(1-y_{i})\log(1-\hat{y}_{i})','Cross-Entropy Loss')
        self.assertFalse(review_records([row])[0])

    def test_explicit_structure_and_mixed_language_symbols_are_verified(self):
        cases=[record('E=m_0*c^2',r'E=c m_{0}^{2}'),
               record('能量质量 E = m0 c^2',r'E=M_{0}c^{2}'),
               record('余弦定理：c^2=a^2+b^2-2ab',r'c^{2}=a^{2}+b^{2}-2ab\cos(\phi)')]
        for row in cases: self.assertFalse(review_records([row])[0])
        row=record('E=m_0*c^2',r'E=m_{0}c^{2}')
        self.assertEqual(len(review_records([row])[0]),1)

    def test_generated_symbols_respect_fixed_constants_and_roles(self):
        random.seed(42)
        for template in build_templates():
            for _ in range(20):
                symbols = allocate_symbols(template['latex'])
                output = template['latex'].format(**symbols)
                if '{i}' in template['latex'] and '{N}' in template['latex']:
                    self.assertNotEqual(symbols['i'], symbols['N'])
                if template['name'] == 'RMSNorm':
                    self.assertNotEqual(symbols['x'], r'\gamma')
                if template['name'] in ('Fourier Transform', 'Schrodinger Equation'):
                    self.assertNotEqual(symbols['t'], 'i')
                if template['name'] == 'Cross-Entropy Loss':
                    self.assertIn(r'\left[', output)

    def test_shorthand_retains_formula_symbols_and_expression(self):
        formula = r'\theta = v_{0} + a T'
        for fn in (apply_keyword_shorthand, apply_partial_formula_reference):
            text = fn('velocity', 'Kinematic Velocity Equation', formula, random.Random(1))
            self.assertIn('theta', text)
            self.assertIn('T', text)
            self.assertIn('=', text)

    def test_targeted_is_reviewed_and_grouped_with_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            families=[t['name'] for t in build_templates()][:15]
            rows = [record(f'x+{i}', f'x+{i}', families[i], source=f's:{i}') for i in range(15)]
            targeted = record('different wording x+1', 'x+1', families[1], 'targeted', 't:1')
            ambiguous = record('Sample Mean 那个式子', 'x', 'Sample Mean', 'targeted', 't:2')
            write_jsonl(root/'source.jsonl', rows)
            write_jsonl(root/'targeted.jsonl', [targeted, ambiguous])
            summary = build_datasets(root, root/'v4', 0.1, 42,
                sources=(('clean','source.jsonl'),), train_only_sources=(('targeted','targeted.jsonl'),), quality_overrides=[])
            splits = [load_jsonl(root/'v4'/f'latex_formula_{s}.jsonl') for s in ('train','eval','test')]
            locations = [i for i, split in enumerate(splits) for row in split if row['metadata']['formula_name']==families[1]]
            self.assertEqual(len(set(locations)), 1)
            self.assertEqual(summary['leakage']['input_overlap'], 0)
            self.assertEqual(summary['leakage']['target_overlap'], 0)
            self.assertTrue(all(x['metadata'].get('formula_group_id') for split in splits for x in split))
            self.assertTrue(any(x['input']==ambiguous['input'] for x in load_jsonl(root/'v4'/'latex_formula_quarantine.jsonl')))


if __name__ == '__main__':
    unittest.main()
