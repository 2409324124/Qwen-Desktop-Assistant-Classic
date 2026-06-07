# Qwen3 4B LaTeX Correction Training

This workflow trains a LoRA adapter for Simplified-Chinese LaTeX formula correction using the frozen phase-1 datasets.

## 1. Canonicalize Ground Truth

The source JSONL files retain their original `output` and add a deterministic `canonical_output` used for training.

```bash
python -m training.canonicalize_dataset --write
python -m training.canonicalize_dataset --check
```

The audit is written to `training/canonicalization_audit.json`. The check fails if a canonical field is stale or a Ground Truth formula cannot be parsed into the local AST.

## 2. Prepare Data

From the repository root:

```bash
python -m training.prepare_dataset
```

Generated files:

- `training/data/latex_formula_train.jsonl`
- `training/data/latex_formula_eval.jsonl`
- `training/data/dataset_summary.json`
- `training/data/dataset_info.json`

## 3. Remote 3090 Environment

On the 3090 host, create or activate an isolated environment, then install LLaMA-Factory and its training dependencies.

```bash
conda create -n latex-sft python=3.11 -y
conda activate latex-sft
git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e ".[torch,metrics]"
```

Copy this repository to the remote host, or run these commands from a checkout that contains this `training/` directory.

## 4. Smoke Test

```bash
llamafactory-cli train training/qwen3_4b_lora_smoke.yaml
```

If the 3090 runs out of memory, set `per_device_train_batch_size: 1` in both YAML files and rerun the smoke test.

## 5. Full Training

```bash
llamafactory-cli train training/qwen3_4b_lora_sft.yaml
```

Primary output:

```text
saves/qwen3-4b-latex-correction/lora/sft
```

## 6. Evaluation

Run a base-model baseline over the fixed eval split:

```bash
python -m training.run_lora_inference \
  --out reports/qwen3-4b-latex-correction-base-predictions.jsonl
```

Run the trained LoRA adapter over the same split:

```bash
python -m training.run_lora_inference \
  --adapter saves/qwen3-4b-latex-correction/lora/sft \
  --out reports/qwen3-4b-latex-correction-lora-predictions.jsonl
```

Generate the report:

```bash
python -m training.evaluate_latex \
  --predictions reports/qwen3-4b-latex-correction-lora-predictions.jsonl \
  --report reports/qwen3-4b-latex-correction-eval.md \
  --json reports/qwen3-4b-latex-correction-eval.json
```

`semantic_accuracy` is the primary metric. The report also retains:

- exact and canonical accuracy
- symbol-fidelity accuracy
- AST parse coverage
- per-layer and per-formula-family accuracy
- match-level counts such as `style_only`, `commutative_reorder`, `alpha_rename`, and `true_mismatch`

The semantic matcher permits consistent formula-template variable renaming and scalar commutative reordering. Matrix multiplication order remains strict for matrix-sensitive formula families.
