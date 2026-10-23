import copy
import json
from pathlib import Path
import tempfile
import unittest

from training.clean_v5_training import build, leakage_report, review_training, sha_text, write_rows
from training.formula_grouping import prepare_grouping_records


def record(sid, family, formula, group, split='train'):
    r={'instruction':'restore','input':formula,'output':formula,'canonical_output':formula,
       'metadata':{'source_id':sid,'formula_name':family,'original_output':formula,
                   'formula_group_id':group,'split':split,'category':'test'}}
    r=prepare_grouping_records([r])[0][0]
    return r


def decision(row, number=1, action='keep', output=None):
    d={'source_id':row['metadata']['source_id'],'row':number,'decision':action,
       'reason':'Explicit input formula preserves every symbol and scope.',
       'input_sha256':sha_text(row['input']),'output_sha256':sha_text(row['output'])}
    if output is not None:d['output']=output
    return d


class CleanTrainingTests(unittest.TestCase):
    def test_exhaustive_review_and_stale_labels_fail_closed(self):
        r=record('a','Product Rule','x+y','g1')
        with self.assertRaises(ValueError):review_training([r],[],[])
        d=decision(r); d['input_sha256']='wrong'
        with self.assertRaisesRegex(ValueError,'Stale'):review_training([r],[d],[])
        d=decision(r);d['reason']=''
        with self.assertRaisesRegex(ValueError,'evidence'):review_training([r],[d],[])

    def test_unique_repair_preserves_history_and_original(self):
        r=record('a','Softmax Function','x+y','g1'); before=copy.deepcopy(r)
        fixed,held,audit,_=review_training([r],[decision(r,action='repair',output='x-y')],[])
        self.assertFalse(held);self.assertEqual(r,before)
        self.assertEqual(fixed[0]['output'],'x-y')
        self.assertEqual(fixed[0]['metadata']['reviewed_v5_output'],'x+y')
        self.assertGreaterEqual(len(fixed[0]['metadata']['structural_signatures']),2)
        self.assertEqual(audit[0]['final_action'],'repair')

    def test_unparsed_repair_is_quarantined(self):
        r=record('a','Product Rule','x+y','g1')
        kept,held,audit,_=review_training([r],[decision(r,action='repair',output=r'\unknown{x}')],[])
        self.assertFalse(kept);self.assertEqual(len(held),1)
        self.assertEqual(audit[0]['final_action'],'quarantine')

    def test_repair_connection_quarantines_whole_original_training_component(self):
        first=record('a','Product Rule','x+y','g1')
        sibling=record('b','Product Rule','x-y','g1')
        safe=record('c','Sample Mean','x^{3}','g2')
        heldout=record('d',"Coulomb's Law",'a/b','dev','eval')
        rows=[first,sibling,safe]
        decisions=[decision(first,action='repair',output='x/y'),decision(sibling,2),decision(safe,3)]
        kept,held,audit,_=review_training(rows,decisions,[[heldout]])
        self.assertEqual([r['metadata']['source_id'] for r in kept],['c'])
        self.assertEqual(len(held),2)
        self.assertTrue(all(not x for x in leakage_report([kept,[heldout],[]]).values()))

    def test_conflicting_inputs_after_repair_are_not_exported(self):
        a=record('a','Product Rule','x+y','g1'); b=copy.deepcopy(a);b['metadata']['source_id']='b'
        kept,held,_,_=review_training([a,b],[decision(a),decision(b,2,'repair','x-y')],[])
        self.assertFalse(kept);self.assertEqual(len(held),2)

    def test_export_is_deterministic_and_does_not_overwrite_frozen_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/'v5';source.mkdir()
            train=record('a','Product Rule','x+y','train')
            dev=record('b',"Coulomb's Law",'a/b','dev','eval')
            test=record('c','Sample Mean','x^{3}','test','test')
            for name,rows in [('train',[train]),('eval_clean',[dev]),('test',[test])]:
                write_rows(source/f'latex_formula_{name}.jsonl',rows)
            (source/'dataset_info.json').write_text('{}\n')
            review=root/'review.jsonl';write_rows(review,[decision(train)])
            before={p.name:p.read_bytes() for p in source.iterdir()}
            build(source,review,root/'a');build(source,review,root/'b')
            self.assertEqual(before,{p.name:p.read_bytes() for p in source.iterdir()})
            self.assertEqual({p.name:p.read_bytes() for p in (root/'a').iterdir()},
                             {p.name:p.read_bytes() for p in (root/'b').iterdir()})
            with self.assertRaises(ValueError):build(source,review,source)


if __name__=='__main__':unittest.main()
