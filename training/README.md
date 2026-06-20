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

The generated train and eval records use the strict canonical-dialect system prompt from `training/prompts.py`. The original source instructions remain untouched. The v3 targeted records in `training/targeted_v3_train.jsonl` are train-only and never enter the fixed eval split.

Generated files:

- `training/data/latex_formula_train.jsonl`
- `training/data/latex_formula_eval.jsonl`
- `training/data/latex_formula_eval_clean.jsonl`
- `training/data/dataset_summary.json`
- `training/data/dataset_info.json`
- `training/data/latex_formula_quarantine.jsonl`

The reviewed decisions in `training/dataset_quality_overrides.json` and the automatic low-information prompt filter are applied before deduplication and splitting. Excluded records are retained in the quarantine file for auditability; repaired targets record their review reason in metadata. Ground Truth formulas are passed through the same LaTeX boundary postprocessor used for inference, so train, eval, and prediction strings share the same display dialect.

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

The 3090 profile uses BF16 and FlashAttention-2. Verify the existing environment before the smoke test:

```bash
python -c 'import flash_attn; print(flash_attn.__version__)'
```

## 4. Smoke Test

```bash
llamafactory-cli train training/qwen3_4b_lora_smoke.yaml
```

If the 3090 runs out of memory, set `per_device_train_batch_size: 1` in both YAML files and rerun the smoke test.

## 5. Full Training

```bash
llamafactory-cli train training/qwen3_4b_lora_sft.yaml
```

The full config evaluates the fixed `latex_formula_eval_clean` dataset every 100 optimizer steps and reloads the checkpoint with the lowest `eval_loss` at the end.

Primary output:

```text
saves/qwen3-4b-latex-correction/lora/sft
```

The v3 targeted run keeps the same 3090 profile but writes to a separate adapter directory:

```bash
llamafactory-cli train training/qwen3_4b_lora_sft_v3.yaml
```

```text
saves/qwen3-4b-latex-correction/lora/sft-v3
```

## 6. Evaluation

Long-running inference and evaluation commands display progress bars. Inference also flushes every prediction to disk, so `wc -l` reflects current progress. Inference applies deterministic LaTeX boundary postprocessing by default and records `raw_prediction` only when the final `prediction` changes; pass `--no-postprocess` for raw model output.

Run a base-model baseline over the fixed clean eval split:

```bash
python -m training.run_lora_inference \
  --out reports/qwen3-4b-latex-correction-base-predictions.jsonl
```

Run the trained LoRA adapter over the same clean split:

```bash
python -m training.run_lora_inference \
  --adapter saves/qwen3-4b-latex-correction/lora/sft \
  --out reports/qwen3-4b-latex-correction-lora-predictions.jsonl
```

Run the v3 adapter over the same clean split:

```bash
python -m training.run_lora_inference \
  --adapter saves/qwen3-4b-latex-correction/lora/sft-v3 \
  --out reports/qwen3-4b-latex-correction-lora-v3-predictions.jsonl
```

Generate the report:

```bash
python -m training.evaluate_latex \
  --predictions reports/qwen3-4b-latex-correction-lora-predictions.jsonl \
  --report reports/qwen3-4b-latex-correction-eval.md \
  --json reports/qwen3-4b-latex-correction-eval.json
```

`run_lora_inference` defaults to `training/data/latex_formula_eval_clean.jsonl`. Before scoring an older 300-row prediction file generated from `latex_formula_eval.jsonl`, apply the reviewed quality decisions without rerunning inference:

```bash
python -m training.clean_evaluation --input reports/qwen3-4b-latex-correction-lora-v2-predictions.jsonl --output reports/qwen3-4b-latex-correction-lora-v2-clean-predictions.jsonl --quarantine reports/qwen3-4b-latex-correction-v2-quarantine.jsonl --audit reports/qwen3-4b-latex-correction-v2-quality-audit.json
```

Then evaluate the clean prediction file. New predictions against `latex_formula_eval_clean.jsonl` can be evaluated directly.

`semantic_accuracy` is the primary metric. The report also retains:

- exact and canonical accuracy
- symbol-fidelity accuracy
- AST parse coverage
- per-layer and per-formula-family accuracy
- match-level counts such as `style_only`, `commutative_reorder`, `alpha_rename`, and `true_mismatch`

The semantic matcher permits consistent formula-template variable renaming and scalar commutative reordering. Matrix multiplication order remains strict for matrix-sensitive formula families.
