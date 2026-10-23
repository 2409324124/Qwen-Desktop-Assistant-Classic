"""Migration safety: frozen evidence and current execution have separate identities."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from latex_sft.__main__ import main
from latex_sft.experiments import run_v5_experiment as workflow
from latex_sft.experiments.provenance import (
    historical_source, verify_snapshot, verify_recorded_protocol,
    LEGACY_PROTOCOL_FILES, SNAPSHOT_MANIFEST, SNAPSHOT_PREFIX,
)

ROOT = Path(__file__).resolve().parents[1]


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT/'archive/protocols/a082730', self.root/'archive/protocols/a082730')
        self.mapping = json.loads((self.root/SNAPSHOT_MANIFEST).read_text())['files']

    def test_legacy_code_resolves_original_bytes_not_compatibility_wrappers(self):
        name = 'training/evaluate_latex.py'
        path = historical_source(self.root, name, self.mapping[name]['sha256'])
        self.assertEqual(path, self.root/(SNAPSHOT_PREFIX+name))
        self.assertNotEqual(path.read_bytes(), (ROOT/name).read_bytes())
        self.assertEqual(set(verify_snapshot(self.root)), set(self.mapping))

    def test_snapshot_bytes_mapping_and_unknown_prior_hash_fail_closed(self):
        name = 'training/evaluate_latex.py'
        target = self.root/(SNAPSHOT_PREFIX+name)
        original = target.read_bytes()
        target.write_bytes(original+b'\n# changed')
        with self.assertRaisesRegex(ValueError, 'snapshot changed'):
            historical_source(self.root, name, self.mapping[name]['sha256'])
        with self.assertRaisesRegex(ValueError, 'snapshot changed'):
            verify_snapshot(self.root)
        target.write_bytes(original)
        with self.assertRaisesRegex(ValueError, 'not in this snapshot'):
            historical_source(self.root, name, '0'*64)
        manifest = self.root/SNAPSHOT_MANIFEST
        manifest.write_text(manifest.read_text()+'\n')
        with self.assertRaisesRegex(ValueError, 'mapping is missing or changed'):
            verify_snapshot(self.root)

    def test_traversal_and_symlink_escape_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Invalid evidence path'):
            historical_source(self.root, '../elsewhere.py', '0'*64)
        name = 'training/evaluate_latex.py'
        path = self.root/(SNAPSHOT_PREFIX+name)
        path.unlink()
        path.symlink_to(ROOT/name)
        with self.assertRaisesRegex(ValueError, 'escapes checkout'):
            verify_snapshot(self.root)

    def test_historical_protocol_requires_all_original_members(self):
        hashes = {name: self.mapping[name]['sha256'] for name in LEGACY_PROTOCOL_FILES}
        self.assertEqual(verify_recorded_protocol(self.root, hashes)['kind'], 'historical')
        hashes.pop('training/prompts.py')
        with self.assertRaisesRegex(ValueError, 'Incomplete or unknown'):
            verify_recorded_protocol(self.root, hashes)

    def test_reviewed_dataset_verifies_without_rebinding_frozen_hashes(self):
        binding = workflow.verify_dataset(ROOT, ROOT/'training/data/v5.2', 'v5.2')
        summary = json.loads((ROOT/'training/data/v5.2/dataset_summary.json').read_text())
        self.assertEqual(binding['export_files_sha256'], summary['export_files_sha256'])
        plan = workflow.training_plan(ROOT, 'sft', data_version='v5.2')
        self.assertEqual(plan['execution_protocol_version'], 'latex-sft-package-v1')
        self.assertIn('src/latex_sft/core/resources/latex-correction.txt', plan['protocol_sha256'])
        self.assertNotIn('training/prompts.py', plan['protocol_sha256'])


class CurrentExecutionBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT/'src/latex_sft', self.root/'src/latex_sft',
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))

    def test_all_runtime_dependencies_are_bound_and_edits_rejected(self):
        from latex_sft.experiments.provenance import verify_package_checkout
        protocol = workflow.protocol_hashes(self.root)
        self.assertEqual(protocol, verify_package_checkout(ROOT))
        for member in ('data/text.py', 'data/components.py', 'core/output_protocol.py',
                       'core/resources/latex-correction.txt', '__main__.py'):
            self.assertIn('src/latex_sft/'+member, protocol)
        path = self.root/'src/latex_sft/data/text.py'
        path.write_bytes(path.read_bytes()+b'\n# changed implementation\n')
        with self.assertRaisesRegex(ValueError, 'Loaded package differs'):
            workflow.protocol_hashes(self.root)

    def test_added_and_missing_package_modules_are_rejected(self):
        extra = self.root/'src/latex_sft/injected.py'
        extra.write_text('# not in installed package\n')
        with self.assertRaisesRegex(ValueError, 'Loaded package differs'):
            workflow.protocol_hashes(self.root)
        extra.unlink()
        (self.root/'src/latex_sft/data/text.py').unlink()
        with self.assertRaisesRegex(ValueError, 'Loaded package differs'):
            workflow.protocol_hashes(self.root)

    def test_new_data_requires_exact_current_membership_for_both_versions(self):
        from latex_sft.data.provenance import current_code_hashes
        hashes = current_code_hashes()
        directory = self.root/'dataset'; directory.mkdir()
        for version, field in (('v5', 'source_code_sha256'), ('v5.2', 'current_code_sha256')):
            for kind in ('omitted', 'extra'):
                with self.subTest(version=version, kind=kind):
                    altered = dict(hashes)
                    if kind == 'omitted':
                        altered.pop('src/latex_sft/data/text.py')
                    else:
                        altered['src/latex_sft/not-used.py'] = '0'*64
                    summary = {'data_version': workflow.DATA_VERSIONS[version],
                               'execution_protocol_version': 'latex-sft-package-v1', field: altered}
                    (directory/'dataset_summary.json').write_text(json.dumps(summary))
                    with self.assertRaisesRegex(ValueError, 'current provenance members'):
                        workflow.verify_dataset(self.root, directory, version)

    def test_new_reviewed_summary_is_accepted_with_complete_current_identity(self):
        from latex_sft.data.provenance import current_code_hashes, MODULE_PATHS
        for relative in ('training/data/v5.2', 'training/reviews/v5_source'):
            shutil.copytree(ROOT/relative, self.root/relative)
        for split in ('train', 'eval', 'test'):
            relative = 'training/reviews/v5_'+split+'_review.jsonl'
            shutil.copy2(ROOT/relative, self.root/relative)
        directory = self.root/'training/data/v5.2'
        path = directory/'dataset_summary.json'
        summary = json.loads(path.read_text())
        summary['execution_protocol_version'] = 'latex-sft-package-v1'
        summary['current_code_sha256'] = current_code_hashes()
        summary['code_sha256'] = {name: workflow.sha(self.root/'src/latex_sft'/MODULE_PATHS.get(name, 'data/'+name))
                                  for name in summary['code_sha256']}
        path.write_text(json.dumps(summary))
        workflow.verify_dataset(self.root, directory, 'v5.2')
        summary['current_code_sha256'].pop('src/latex_sft/data/text.py')
        path.write_text(json.dumps(summary))
        with self.assertRaisesRegex(ValueError, 'current provenance members'):
            workflow.verify_dataset(self.root, directory, 'v5.2')


class PackageCliTests(unittest.TestCase):
    def test_subcommand_help_reaches_real_flags_without_resolving_checkout(self):
        for command, flag in (('train', '--profile'), ('evaluate', '--baseline-only'),
                              ('infer', '--max-new-tokens'), ('score', '--predictions')):
            output = io.StringIO()
            with self.subTest(command=command), patch('latex_sft.paths.repository_root', side_effect=ValueError('no checkout')):
                with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as result:
                    main([command, '--help'])
                self.assertEqual(result.exception.code, 0)
                self.assertIn(flag, output.getvalue())

    def test_new_cli_defaults_reviewed_data_without_running_training(self):
        with patch.object(workflow, 'main') as run:
            main(['train'])
            run.assert_called_once_with(['train', '--data-version', 'v5.2'])
        with patch.object(workflow, 'main') as run:
            main(['evaluate', '--data-version=v5', '--baseline-only'])
            run.assert_called_once_with(['evaluate', '--data-version=v5', '--baseline-only'])

    def test_scoring_works_outside_checkout(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            predictions = directory/'predictions.jsonl'
            predictions.write_text(json.dumps({'input': 'x+y', 'expected': 'x+y', 'prediction': 'x+y'})+'\n')
            with patch('pathlib.Path.cwd', return_value=directory), contextlib.redirect_stdout(io.StringIO()):
                main(['score', '--predictions', str(predictions), '--report', str(directory/'report.md'),
                      '--json', str(directory/'metrics.json')])
            self.assertEqual(json.loads((directory/'metrics.json').read_text())['math_accuracy'], 1.0)


if __name__ == '__main__':
    unittest.main()
