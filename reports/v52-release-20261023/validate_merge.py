"""CPU validation of released tensors against cached base + checkpoint-30."""
import json
from pathlib import Path
import torch
from safetensors import safe_open
from transformers import AutoTokenizer
root = Path('/mnt/RC10/qwen-latex/releases/v52-20261023')
base = Path('/home/miku/.cache/huggingface/hub/models--Qwen--Qwen3-4B-Instruct-2507/snapshots/cdbee75f17c01a7cc42f958dc650907174af0554')
adapter = Path('/mnt/RC10/qwen-latex/model-archives/v52-checkpoint30/runs/v52-20261023T073851Z-d239b61a/sft/checkpoint-30')
torch.set_num_threads(8)
def tensors(path):
    return {k: f.get_tensor(k) for p in path.glob('*.safetensors') for f in [safe_open(p, framework='pt')] for k in f.keys()}
b, m, a = tensors(base), tensors(root/'bf16'), tensors(adapter)
assert set(b) == set(m), (set(b)-set(m), set(m)-set(b))
changed, untouched, parameter_count = [], 0, 0
for key, tensor in m.items():
    assert tensor.dtype == torch.bfloat16 and tensor.shape == b[key].shape and torch.isfinite(tensor).all(), key
    parameter_count += tensor.numel()
    stem = 'base_model.model.' + key.removesuffix('.weight')
    if stem + '.lora_A.weight' in a:
        delta = (a[stem+'.lora_B.weight'].float() @ a[stem+'.lora_A.weight'].float()) * 2
        expected = (b[key].float() + delta).bfloat16()
        assert torch.equal(tensor, expected), (key, float((tensor.float()-expected.float()).abs().max()))
        assert not torch.equal(tensor, b[key]), key
        changed.append(key)
    else:
        assert torch.equal(tensor, b[key]), key
        untouched += 1
assert len(changed) == 252
original, released = AutoTokenizer.from_pretrained(base), AutoTokenizer.from_pretrained(root/'bf16')
messages = [{'role':'system','content':'Convert to LaTeX.'},{'role':'user','content':'x平方加y平方'}]
assert original.get_vocab() == released.get_vocab()
assert original.apply_chat_template(messages, add_generation_prompt=True) == released.apply_chat_template(messages, add_generation_prompt=True)
report = {'status':'passed','tensors':len(m),'parameters':parameter_count,'dtype':'bfloat16','adapter_targets_exactly_verified':len(changed),'unchanged_tensors_verified':untouched,'tokenizer_vocab_and_chat_tokens_match_base':True}
(root/'merge-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
