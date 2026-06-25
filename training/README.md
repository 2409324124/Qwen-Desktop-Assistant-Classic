# Qwen3 4B LaTeX Correction Training

This workflow trains and evaluates a LoRA adapter for LaTeX formula correction. The source data is frozen under `data/frozen/phase1/`; generated LLaMA-Factory datasets are written to `training/data/` and ignored by Git.

## Release Artifacts

The v3 release is published as separate Hugging Face repositories by runtime format:

- Full BF16 merged model: [xu2409324124/qwen3-4b-latex-correction-v3-bf16](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v3-bf16)
- GGUF Q4_K_M model: [xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m)

Keep BF16 safetensors and GGUF quantizations in separate repositories. The BF16 repository is the canonical merged checkpoint for Transformers-compatible workflows; the GGUF repository is the deployment-oriented local inference package.

## 1. Canonicalize Ground Truth

The source JSONL files retain their original `output` and add a deterministic `canonical_output` used for training.

```bash
python -m training.canonicalize_dataset --write
python -m training.canonicalize_dataset --check
```

The default sources are:

- `data/frozen/phase1/train_clean_v1_500.jsonl`
- `data/frozen/phase1/train_noisy_v4_900.jsonl`
- `data/frozen/phase1/train_hard_v5_600.jsonl`

The audit is written to `training/canonicalization_audit.json`. The check fails if a canonical field is stale or a Ground Truth formula cannot be parsed into the local AST.

## 2. Prepare Data

From the repository root:

```bash
python -m training.prepare_dataset
```

Generated files:

- `training/data/latex_formula_train.jsonl`
- `training/data/latex_formula_eval.jsonl`
- `training/data/latex_formula_eval_clean.jsonl`
- `training/data/dataset_summary.json`
- `training/data/dataset_info.json`
- `training/data/latex_formula_quarantine.jsonl`

The reviewed decisions in `training/dataset_quality_overrides.json` and the automatic low-information prompt filter are applied before deduplication and splitting. The v3 targeted records in `training/targeted_v3_train.jsonl` are train-only and never enter the fixed eval split.

## 3. LLaMA-Factory Training

Use an isolated Python 3.11 environment with LLaMA-Factory and its training dependencies installed. The 3090 profile uses BF16 and FlashAttention-2.

Smoke test:

```bash
llamafactory-cli train training/qwen3_4b_lora_smoke.yaml
```

Full v3 training:

```bash
llamafactory-cli train training/qwen3_4b_lora_sft_v3.yaml
```

Primary adapter output:

```text
saves/qwen3-4b-latex-correction/lora/sft-v3
```

The full config evaluates the fixed `latex_formula_eval_clean` dataset every 100 optimizer steps and reloads the checkpoint with the lowest `eval_loss`.

## 4. Evaluation

Long-running inference and evaluation commands display progress bars. Inference flushes every prediction to disk, so `wc -l` reflects current progress. Inference applies deterministic LaTeX boundary postprocessing by default and records `raw_prediction` only when the final `prediction` changes.

Base-model baseline:

```bash
python -m training.run_lora_inference \
  --out reports/qwen3-4b-latex-correction-base-predictions.jsonl
```

v3 adapter:

```bash
python -m training.run_lora_inference \
  --adapter saves/qwen3-4b-latex-correction/lora/sft-v3 \
  --out reports/qwen3-4b-latex-correction-lora-v3-predictions.jsonl
```

Report:

```bash
python -m training.evaluate_latex \
  --predictions reports/qwen3-4b-latex-correction-lora-v3-predictions.jsonl \
  --report reports/qwen3-4b-latex-correction-v3-eval.md \
  --json reports/qwen3-4b-latex-correction-v3-eval.json
```

`run_lora_inference` defaults to `training/data/latex_formula_eval_clean.jsonl`. `math_accuracy` is the primary metric. It counts mathematically equivalent formulas even when harmless layout choices differ, while still rejecting variable drift when the user input explicitly names variables. `format_compliance_accuracy` is reported separately for exact canonical-dialect adherence. The report also retains exact, canonical, symbol-fidelity, legacy semantic, parse-coverage, per-layer, and per-formula-family metrics.

Current clean-eval results:

| model | math accuracy | format compliance | exact accuracy | parse coverage |
| --- | ---: | ---: | ---: | ---: |
| Base Qwen3-4B-Instruct-2507 | 13.36% | 2.40% | 2.40% | 36.99% |
| DeepSeek V4 Pro baseline | 69.86% | 41.78% | 21.23% | 97.95% |
| Qwen3-4B LaTeX Correction LoRA v3 | 98.97% | 83.22% | 83.22% | 100.00% |

## 5. Export

Export the merged BF16 model:

```bash
llamafactory-cli export training/qwen3_4b_lora_export_v3.yaml
```

The export config writes the merged model to:

```text
saves/qwen3-4b-latex-correction/merged/sft-v3-bf16
```

Use llama.cpp tooling to convert the BF16 export to GGUF and quantize it for local inference. The published release keeps BF16 and GGUF artifacts in separate Hugging Face repositories.
