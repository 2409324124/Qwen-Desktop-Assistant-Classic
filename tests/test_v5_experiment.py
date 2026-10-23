import contextlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch, Mock
from types import SimpleNamespace

import yaml

from training import run_v5_experiment as workflow
from training.run_lora_inference import parse_args


class V5ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.no_model_check = lambda revision: None
        self.data = self.root/'training/data/v5'; self.data.mkdir(parents=True)
        for name in workflow.PROTOCOL_FILES:
            path = self.root/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text('fixture protocol')
        for relative in workflow.PROFILES.values():
            (self.root/relative).write_bytes((workflow.ROOT/relative).read_bytes())
        source = self.root/'source.jsonl'; source.write_text('frozen')
        for split,filename in workflow.FILES.items():
            rows = [{'instruction':'Restore the formula only', 'input':f'input {split}', 'output':f'x_{{{len(split)}}}',
                     'metadata': {'data_version':'v5', 'evaluation_role':'main',
                                  'formula_group_id':f'group-{split}', 'source_id':f'source-{split}',
                                  'split':'eval' if split=='eval_clean' else split}}]
            (self.data/filename).write_text(json.dumps(rows[0])+'\n')
        workflow.write_json(self.data/'dataset_info.json', {f'latex_formula_{k}':{'file_name':v} for k,v in workflow.FILES.items()})
        self.summary = {'data_version':'v5', 'review_rule_sha256':'rule',
                        'source_artifacts_sha256':{'source.jsonl':workflow.sha(source)},
                        'source_code_sha256':{name:workflow.sha(self.root/name) for name in workflow.PROTOCOL_FILES},
                        **{s:{'total':1} for s in workflow.FILES}}
        self.rehash()

    def rehash(self):
        self.summary['export_files_sha256'] = {name:workflow.sha(self.data/name) for name in (*workflow.FILES.values(),'dataset_info.json')}
        workflow.write_json(self.data/'dataset_summary.json', self.summary)

    def fake_train(self, command, **kwargs):
        config = yaml.safe_load(Path(command[-1]).read_text())
        for step in (10,2):
            path = Path(config['output_dir'])/f'checkpoint-{step}'; path.mkdir(parents=True)
            workflow.write_json(path/'adapter_config.json', {'base_model_name_or_path':workflow.MODEL})
            (path/'adapter_model.safetensors').write_bytes(b'fake weights, not a usable model')
        return subprocess.CompletedProcess(command,0)

    def trained(self):
        plan = workflow.training_plan(self.root,'sft')
        workflow.train(plan,self.root,runner=self.fake_train,resolver=lambda:'a'*40,model_check=self.no_model_check)
        return Path(plan['run_dir'])

    def fake_inference(self, command, **kwargs):
        source = Path(command[command.index('--eval-file')+1]); out = Path(command[command.index('--out')+1])
        self.assertEqual(command[-2:], ['--revision','a'*40])
        rows = [json.loads(line) for line in source.read_text().splitlines()]
        predictions = []
        for row in rows:
            prediction = row['output'] if 'checkpoint-2' in str(out) else 'z'
            predictions.append({'input':row['input'], 'expected':row['output'], 'prediction':prediction,
                                'raw_prediction':prediction, 'metadata':row['metadata']})
        out.write_text(''.join(json.dumps(r)+'\n' for r in predictions))
        return subprocess.CompletedProcess(command,0)

    def test_training_projects_heterogeneous_audit_metadata_without_mutating_sources(self):
        source = self.data/workflow.FILES['train']
        row = json.loads(source.read_text())
        row['metadata']['signature_evidence'] = [{'structural_payload': ['symbol', 'x', []]}]
        other = {**row, 'input': 'second input', 'metadata': {**row['metadata'],
                 'source_id': 'second-source', 'signature_evidence': [{'structural_payload': [['nested'], ['array']]}]}}
        source.write_text(json.dumps(row)+'\n'+json.dumps(other)+'\n')
        self.summary['train']['total'] = 2
        self.rehash()
        original = source.read_bytes()
        run = self.trained()
        effective = yaml.safe_load((run/'effective_config.yaml').read_text())
        self.assertEqual(Path(effective['dataset_dir']), run/'training_data')
        rows = workflow.load_jsonl(run/'training_data'/workflow.FILES['train'])
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(set(record) == {'instruction', 'input', 'output'} for record in rows))
        self.assertEqual(source.read_bytes(), original)
        manifest = json.loads((run/'run_manifest.json').read_text())
        projection = manifest['training_projection']
        workflow.verify_training_projection(projection)
        mapping = workflow.load_jsonl(run/'training_data'/'source_map.jsonl')
        self.assertEqual([r['source_id'] for r in mapping[:2]], ['source-train', 'second-source'])
        self.assertEqual([r['source_line'] for r in mapping[:2]], [1, 2])
        self.assertIn('source_map.jsonl', projection['files_sha256'])

    def test_projection_tampering_during_training_marks_run_failed(self):
        plan = workflow.training_plan(self.root, 'smoke')
        def tamper(command, **kwargs):
            config = yaml.safe_load(Path(command[-1]).read_text())
            target = Path(config['dataset_dir'])/workflow.FILES['train']
            target.write_text(target.read_text()+' ')  # valid JSON, changed bound bytes
            return self.fake_train(command, **kwargs)
        with self.assertRaisesRegex(ValueError, 'Training projection changed'):
            workflow.train(plan, self.root, runner=tamper, resolver=lambda: 'a'*40, model_check=self.no_model_check)
        manifest = json.loads((Path(plan['run_dir'])/'run_manifest.json').read_text())
        self.assertEqual(manifest['status'], 'failed')

    def test_projection_tampering_after_training_blocks_checkpoint_comparison(self):
        run = self.trained()
        target = run/'training_data'/workflow.FILES['eval_clean']
        target.write_text(target.read_text()+' ')
        with self.assertRaisesRegex(ValueError, 'Training projection changed'):
            workflow.evaluation_plan(self.root, run)

    def test_dataset_tampering_and_cross_split_overlap_fail_closed(self):
        workflow.verify_dataset(self.root,self.data)
        target = self.data/workflow.FILES['eval_clean']
        target.write_text(target.read_text()+'\n')
        with self.assertRaisesRegex(ValueError,'Hash mismatch'): workflow.verify_dataset(self.root,self.data)
        row = json.loads(target.read_text()); row['metadata']['formula_group_id']='group-train'
        target.write_text(json.dumps(row)+'\n'); self.rehash()
        with self.assertRaisesRegex(ValueError,'leakage'): workflow.verify_dataset(self.root,self.data)

    def test_default_cli_plans_do_not_launch_or_write(self):
        with patch.object(workflow,'ROOT',self.root), patch.object(workflow,'train') as train, patch.object(workflow,'evaluate') as evaluate, patch('builtins.print'):
            workflow.main(['train'])
            workflow.main(['evaluate','--baseline-only'])
            train.assert_not_called(); evaluate.assert_not_called()
        self.assertFalse((self.root/'saves').exists()); self.assertFalse((self.root/'reports').exists())
        with patch('sys.argv',['inference']):
            self.assertEqual(parse_args().eval_file,Path('training/data/v5/latex_formula_eval_clean.jsonl'))

    def test_baseline_and_numeric_checkpoint_order_with_bound_revision(self):
        run = self.trained()
        plan = workflow.evaluation_plan(self.root,run)
        self.assertEqual([c['name'] for c in plan['candidates']],['base','checkpoint-2','checkpoint-10'])
        self.assertEqual(plan['model_revision'],'a'*40)
        for c in plan['candidates']:
            self.assertIn(str(self.data/workflow.FILES['eval_clean']),c['command'])
            self.assertNotIn(str(self.data/workflow.FILES['test']),c['command'])
        workflow.evaluate(plan,self.root,runner=self.fake_inference,model_check=self.no_model_check)
        comparison = json.loads((Path(plan['output'])/'comparison.json').read_text())
        self.assertEqual(comparison['recommended_model'],'checkpoint-2')
        self.assertEqual(comparison['results'][1]['raw']['grouped_coverage'],1.0)
        self.assertTrue((Path(plan['output'])/'checkpoint-2/report.md').is_file())
        with self.assertRaises(FileExistsError): workflow.evaluate(plan,self.root,runner=self.fake_inference,model_check=self.no_model_check)

    def test_baseline_needs_no_training_and_has_no_selection(self):
        plan=workflow.evaluation_plan(self.root,baseline_only=True)
        workflow.evaluate(plan,self.root,runner=self.fake_inference,resolver=lambda:'a'*40,model_check=self.no_model_check)
        result=json.loads((Path(plan['output'])/'comparison.json').read_text())
        self.assertIsNone(result['recommended_model']); self.assertEqual(len(result['results']),1)

    def test_failed_training_is_recorded_and_outputs_are_not_overwritten(self):
        plan=workflow.training_plan(self.root,'sft')
        def fail(*args,**kwargs): raise subprocess.CalledProcessError(1,args[0])
        with self.assertRaises(subprocess.CalledProcessError):workflow.train(plan,self.root,runner=fail,resolver=lambda:'a'*40,model_check=self.no_model_check)
        manifest=json.loads((Path(plan['run_dir'])/'run_manifest.json').read_text())
        self.assertEqual(manifest['status'],'failed')
        with self.assertRaises(FileExistsError):workflow.train(plan,self.root,runner=self.fake_train)
        with self.assertRaisesRegex(ValueError,'completed'):workflow.evaluation_plan(self.root,Path(plan['run_dir']))

    def test_checkpoint_corruption_and_changed_training_binding_are_rejected(self):
        run=self.trained()
        (run/'checkpoints/checkpoint-2/adapter_model.safetensors').write_bytes(b'')
        with self.assertRaisesRegex(ValueError,'Incomplete'):workflow.evaluation_plan(self.root,run)
        (run/'checkpoints/checkpoint-2/adapter_model.safetensors').write_bytes(b'fake')
        (run/'effective_config.yaml').write_text('changed')
        with self.assertRaisesRegex(ValueError,'configuration changed'):workflow.evaluation_plan(self.root,run)

    def test_incomplete_or_wrong_prediction_coverage_never_selects_checkpoint(self):
        plan=workflow.evaluation_plan(self.root,baseline_only=True)
        def incomplete(command,**kwargs):
            Path(command[command.index('--out')+1]).write_text('')
        with self.assertRaisesRegex(ValueError,'Incomplete prediction'):workflow.evaluate(plan,self.root,runner=incomplete,resolver=lambda:'a'*40,model_check=self.no_model_check)
        self.assertFalse((Path(plan['output'])/'comparison.json').exists())
        self.assertEqual(json.loads((Path(plan['output'])/'evaluation_manifest.json').read_text())['status'],'failed')
        expected=[json.loads((self.data/workflow.FILES['eval_clean']).read_text())]
        bad=[{'input':expected[0]['input'],'expected':expected[0]['output'],'prediction':'x','raw_prediction':'x','metadata':{}}]
        with self.assertRaisesRegex(ValueError,'membership'):workflow.validate_predictions(bad,expected)

    def test_cached_model_preflight_never_downloads_missing_weights(self):
        snapshot=self.root/'snapshot'; snapshot.mkdir()
        download=Mock(return_value=str(snapshot))
        with patch.dict('sys.modules', {'huggingface_hub':SimpleNamespace(snapshot_download=download)}):
            with self.assertRaisesRegex(ValueError,'Download manually'):
                workflow.ensure_cached_model('a'*40)
            workflow.write_json(snapshot/'model.safetensors.index.json', {'weight_map':{'x':'model-1.safetensors','y':'model-2.safetensors'}})
            (snapshot/'model-1.safetensors').write_bytes(b'first')
            with self.assertRaisesRegex(ValueError,'incomplete'):
                workflow.ensure_cached_model('a'*40)
            (snapshot/'model-2.safetensors').write_bytes(b'second')
            self.assertEqual(workflow.ensure_cached_model('a'*40),str(snapshot))
            self.assertTrue(all(call.kwargs['local_files_only'] for call in download.call_args_list))

    def test_changed_weights_are_rejected_even_if_adapter_is_well_formed(self):
        run=self.trained()
        (run/'checkpoints/checkpoint-2/adapter_model.safetensors').write_bytes(b'different nonempty model')
        with self.assertRaisesRegex(ValueError,'checkpoints changed'):
            workflow.evaluation_plan(self.root,run)

    def test_inference_pins_revision_and_always_preserves_raw_output(self):
        from training import run_lora_inference as inference
        class Inputs(dict):
            def to(self, device): return self
        tokenizer=Mock()
        tokenizer.apply_chat_template.return_value='prompt'
        tokenizer.return_value=Inputs(input_ids=SimpleNamespace(shape=(1,1)))
        tokenizer.decode.return_value='x'
        model=Mock(device='cpu')
        model.generate.return_value=[[0,1,2]]
        tokenizer_loader=Mock(return_value=tokenizer); model_loader=Mock(return_value=model)
        modules={'transformers':SimpleNamespace(AutoTokenizer=SimpleNamespace(from_pretrained=tokenizer_loader),
                                               AutoModelForCausalLM=SimpleNamespace(from_pretrained=model_loader)),
                 'torch':SimpleNamespace(bfloat16='bf16',no_grad=contextlib.nullcontext),
                 'peft':SimpleNamespace(PeftModel=Mock())}
        output=self.root/'predictions.jsonl'
        args=SimpleNamespace(model=workflow.MODEL,revision='a'*40,adapter=None,
                             out=output,eval_file=self.data/workflow.FILES['eval_clean'],limit=None,
                             max_new_tokens=2,no_postprocess=False)
        with patch.dict('sys.modules', modules), patch.object(inference,'parse_args',return_value=args):
            inference.main()
            row=json.loads(output.read_text())
            self.assertEqual(row['raw_prediction'],'x')
            self.assertEqual(row['prediction'],'x')
            self.assertEqual(row['generated_tokens'],2)
            self.assertTrue(row['hit_token_limit'])
            self.assertEqual(tokenizer_loader.call_args.kwargs['revision'],'a'*40)
            self.assertEqual(model_loader.call_args.kwargs['revision'],'a'*40)
            with self.assertRaises(FileExistsError):inference.main()

    def test_old_adapters_resume_and_tokenized_cache_cannot_bypass_v5(self):
        path=self.root/workflow.PROFILES['sft']
        original=yaml.safe_load(path.read_text())
        for key in ('adapter_name_or_path','resume_from_checkpoint','tokenized_path'):
            config={**original,key:'old-v3-artifact'}
            path.write_text(yaml.safe_dump(config))
            with self.subTest(key=key), self.assertRaisesRegex(ValueError,'source override'):
                workflow.training_plan(self.root,'sft')
        path.write_text(yaml.safe_dump(original))

    def test_changed_data_between_plan_and_execution_is_rejected(self):
        plan=workflow.evaluation_plan(self.root,baseline_only=True)
        target=self.data/workflow.FILES['eval_clean']
        target.write_text(target.read_text()+' ')
        runner=Mock()
        with self.assertRaisesRegex(ValueError,'Hash mismatch'):
            workflow.evaluate(plan,self.root,runner=runner,resolver=lambda:'a'*40,model_check=self.no_model_check)
        runner.assert_not_called()


if __name__=='__main__': unittest.main()
