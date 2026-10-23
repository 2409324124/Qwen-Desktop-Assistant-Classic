import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from training.clean_v5_holdouts import build, isolate_components
from training.clean_v5_training import load_jsonl, write_rows
from tests.test_clean_v5_training import record, decision


class HoldoutCleanupTests(unittest.TestCase):
    def test_transitive_cross_split_component_quarantines_all_sides(self):
        a=record('a','Product Rule','x+y','train-group')
        sibling=record('b','Product Rule','x-y','train-group')
        dev=record('c',"Coulomb's Law",'x/y','dev-group','eval')
        test=record('d','Sample Mean','x^{3}','test-group','test')
        a['metadata']['structural_signatures'].append('bridge-one')
        dev['metadata']['structural_signatures']+=['bridge-one','bridge-two']
        test['metadata']['structural_signatures'].append('bridge-two')
        kept,held,groups,edges=isolate_components({'train':[a,sibling],'eval':[dev],'test':[test]})
        self.assertTrue(all(not rows for rows in kept.values()))
        self.assertEqual({r['metadata']['source_id'] for r in held},{'a','b','c','d'})
        self.assertEqual(groups[0]['original_splits'],['eval','test','train'])
        self.assertEqual(len(groups),1)
        self.assertTrue(any(e['value']=='bridge-two' for e in edges))

    def test_within_split_connections_merge_groups_without_changing_ownership(self):
        a=record('a','Product Rule','x+y','g1');b=record('b','Sample Mean','u+v','g2')
        kept,held,groups,_=isolate_components({'train':[a,b],'eval':[],'test':[]})
        self.assertFalse(held);self.assertEqual(len(groups),1)
        self.assertEqual(len({r['metadata']['formula_group_id'] for r in kept['train']}),1)
        self.assertEqual({r['metadata']['original_formula_group_id'] for r in kept['train']},{'g1','g2'})
        self.assertTrue(all(r['metadata']['split']=='train' for r in kept['train']))

    def fixture(self,root):
        source=root/'source';reviews=root/'reviews';source.mkdir();reviews.mkdir()
        rows={'train':record('a','Product Rule','x+y','train'),
              'eval':record('b',"Coulomb's Law",r'\frac{a}{b}','dev','eval'),
              'test':record('c','Sample Mean','x^{3}','test','test')}
        for split,row in rows.items():
            filename='eval_clean' if split=='eval' else split
            write_rows(source/f'latex_formula_{filename}.jsonl',[row])
            d=decision(row);d['review_basis']='input_and_original_label_only'
            write_rows(reviews/f'v5_{split}_review.jsonl',[d])
        (source/'dataset_info.json').write_text('{}\n')
        return source,reviews

    def test_reproducible_exports_never_read_predictions_or_modify_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source,reviews=self.fixture(root)
            before={str(p):p.read_bytes() for p in [*source.iterdir(),*reviews.iterdir()]}
            (reviews/'model-predictions.jsonl').write_text('INVALID, MUST NOT BE READ')
            with patch('training.clean_v5_holdouts.load_jsonl',wraps=load_jsonl) as reads:
                first=build(source,reviews,root/'first')
                self.assertEqual(len(reads.call_args_list),6)
                self.assertTrue(all('prediction' not in str(c.args[0]) for c in reads.call_args_list))
            (reviews/'model-predictions.jsonl').write_text('COMPLETELY DIFFERENT PREDICTIONS')
            second=build(source,reviews,root/'second')
            self.assertEqual(first,second)
            self.assertTrue(all(Path(name).read_bytes()==data for name,data in before.items()))
            self.assertEqual({p.name:p.read_bytes() for p in (root/'first').iterdir()},
                             {p.name:p.read_bytes() for p in (root/'second').iterdir()})
            self.assertTrue(all(v==0 for v in first['leakage'].values()))
            with self.assertRaisesRegex(ValueError,'overwrite'):build(source,reviews,root/'first')

    def test_unbound_holdout_review_fails_before_creating_export(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source,reviews=self.fixture(root)
            path=reviews/'v5_test_review.jsonl';rows=load_jsonl(path);rows[0].pop('review_basis');write_rows(path,rows)
            with self.assertRaisesRegex(ValueError,'input/gold-only'):build(source,reviews,root/'result')
            self.assertFalse((root/'result').exists())


if __name__=='__main__':unittest.main()
