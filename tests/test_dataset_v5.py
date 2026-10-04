import copy
import json
import tempfile
import unittest
from pathlib import Path

from training.formula_grouping import prepare_grouping_records, load_family_registry
from training.prepare_dataset import split_grouped_records, dedupe_records, build_datasets, load_jsonl, write_jsonl
from tools.data_generation.mine_sympy import build_templates


def row(family, output, source, **metadata):
    return {'instruction':'restore', 'input':output, 'output':output, 'canonical_output':output,
            'metadata':{'source_id':source, 'formula_name':family, 'original_output':output,
                        'category':'test', **metadata}}


class DatasetV5Tests(unittest.TestCase):
    def test_registry_covers_exactly_all_templates(self):
        registry = load_family_registry()
        self.assertEqual(set(registry), {t['name'] for t in build_templates()})

    def test_relatives_and_transitive_structure_never_cross_splits(self):
        rows = [row("Euler's Formula",r'e^{ix}=\cos x+i\sin x','a'),
                row("Euler's Identity",r'e^{i\pi}+1=0','b'),
                row('Fourier Transform','F=x+y','c'),row('Laplace Transform','L=x-y','d'),
                row("Coulomb's Law",r'F=k\frac{a b}{r^{2}}','e'),
                row("Newton's Law of Universal Gravitation",r'G=c\frac{u v}{s^{2}}','f'),
                row('Mass-Energy Equivalence','Q=a+b','g')]
        accepted, held, diagnostic = prepare_grouping_records(rows)
        self.assertFalse(held); self.assertFalse(diagnostic)
        for seed in range(8):
            train,dev,test,leakage,_ = split_grouped_records(copy.deepcopy(accepted),seed=seed)
            where = {r['metadata']['source_id']:i for i,s in enumerate((train,dev,test)) for r in s}
            self.assertEqual(where['a'],where['b'])
            self.assertEqual(where['c'],where['d'])
            self.assertEqual(where['e'],where['f'])
            self.assertEqual(where['c'],where['g'])
            self.assertTrue(all(n==0 for n in leakage.values()))
            self.assertIn('structure_overlap',leakage)
            self.assertIn('template_overlap',leakage)
            self.assertIn('near_family_overlap',leakage)

    def test_fail_closed_and_separate_symbol_diagnostic(self):
        rows=[row('Unknown Family','x+y','a'),row('Sample Mean',r'\unknowncommand{x}','b'),
              row('Symbol Boundary',r'\alpha\beta','c')]
        accepted,held,diagnostic=prepare_grouping_records(rows)
        self.assertFalse(accepted)
        self.assertEqual(len(held),2)
        self.assertEqual(len(diagnostic),1)
        self.assertEqual(diagnostic[0]['metadata']['evaluation_role'],'diagnostic')
        self.assertTrue(all(r['metadata']['grouping_reasons'] for r in held))

    def test_unparseable_original_target_also_requires_review(self):
        rows=[row('Sample Mean','x+y','a',original_output=r'\unknowncommand{x}')]
        accepted,held,_=prepare_grouping_records(rows)
        self.assertFalse(accepted);self.assertEqual(len(held),1)

    def test_duplicate_keeps_structure_and_near_family_bridges(self):
        rows=[row('Sample Mean','x+y','a'),row('Fourier Transform','x+y','b'),
              row('Laplace Transform','u-v','c')]
        accepted,_,_=prepare_grouping_records(rows)
        deduped,_=dedupe_records(accepted)
        splits=split_grouped_records(deduped)
        ids={r['metadata']['formula_group_id'] for s in splits[:3] for r in s}
        self.assertEqual(len(ids),1)

    def test_historical_output_directory_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);old=root/'v4';old.mkdir()
            (old/'dataset_summary.json').write_text('{"data_version":"v4"}')
            with self.assertRaisesRegex(ValueError,'historical dataset'):
                build_datasets(root,old,.1,42,sources=(),train_only_sources=(),quality_overrides=[])
            self.assertEqual((old/'dataset_summary.json').read_text(),'{"data_version":"v4"}')

    def test_input_order_does_not_change_group_assignment(self):
        rows=[row(t['name'],f'x+{i}',str(i)) for i,t in enumerate(build_templates())]
        ready,_,_=prepare_grouping_records(rows)
        def assignments(items):
            splits=split_grouped_records(items,seed=42)
            return {r['metadata']['source_id']:(i,r['metadata']['formula_group_id']) for i,s in enumerate(splits[:3]) for r in s}
        self.assertEqual(assignments(copy.deepcopy(ready)),assignments(list(reversed(copy.deepcopy(ready)))))

    def test_exports_complete_audit_and_are_deterministic(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            records=[row('Sample Mean','x+y','a'),row('Fourier Transform','u-v','b'),
                     row('Symbol Boundary',r'\alpha\beta','c'),row('Unknown','p','d')]
            write_jsonl(root/'source.jsonl',records)
            for output in ('first','second'):
                result=build_datasets(root,root/output,.1,42,sources=(('clean','source.jsonl'),),train_only_sources=(),quality_overrides=[])
                self.assertEqual(result['data_version'],'v5')
                self.assertEqual(result['diagnostic']['total'],1)
                self.assertTrue(all(n==0 for n in result['leakage'].values()))
                self.assertTrue((root/output/'group_connections.jsonl').exists())
                self.assertTrue((root/output/'group_manifest.jsonl').exists())
                manifest=load_jsonl(root/output/'review_manifest.jsonl')
                self.assertEqual(len(manifest),len(records))
                self.assertEqual(sum(x['action']=='diagnostic' for x in manifest),1)
            for name in result['export_files_sha256']:
                self.assertEqual((root/'first'/name).read_bytes(),(root/'second'/name).read_bytes(),name)


if __name__=='__main__':unittest.main()
