# Qwen3 4B LaTeX Correction Training

This workflow trains and evaluates a LoRA adapter for LaTeX formula correction. The source data is frozen under `data/frozen/phase1/`; versioned LLaMA-Factory datasets are written to `training/data/v5/` and ignored by Git. See [the v5 grouping protocol](DATA_V5.md) and [historical v4 audit](DATA_V4.md); existing v3 configs and `training/data/*.jsonl` are historical and are not switched to v5 automatically.

## Release Artifacts

The v3 release is published as separate Hugging Face repositories by runtime format:

- Full BF16 merged model: [xu2409324124/qwen3-4b-latex-correction-v3-bf16](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v3-bf16)
- GGUF Q4_K_M model: [xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m)

Keep BF16 safetensors and GGUF quantizations in separate repositories. The BF16 repository is the canonical merged checkpoint for Transformers-compatible workflows; the GGUF repository is the deployment-oriented local inference package.

## 1. Canonicalize Ground Truth

Frozen JSONL sources must remain unchanged. The v5 preparation workflow rebuilds safe canonical targets in its versioned output directory; old cached canonical fields are retained only for provenance. The legacy read-only checker can diagnose those caches:

```bash
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

- `training/data/v5/latex_formula_train.jsonl`
- `training/data/v5/latex_formula_eval.jsonl`
- `training/data/v5/latex_formula_eval_clean.jsonl`
- `training/data/v5/dataset_summary.json`
- `training/data/v5/dataset_info.json`
- `training/data/v5/latex_formula_quarantine.jsonl`

Frozen and targeted records share review, normalization and connected source/structure/template/near-family grouping. The explicit registry covers all 58 templates; unknown families or unverified signatures are quarantined. With seed 42 allocation targets 80/10/10 groups globally, without category stratification. Targeted records follow their group. Symbol Boundary records are diagnostic only. Output also includes `latex_formula_test.jsonl`, `latex_formula_diagnostic.jsonl`, `review_manifest.jsonl`, `group_manifest.jsonl`, `group_connections.jsonl` and `group_audit.md`; `eval_clean` aliases development. Per-sample and group-macro scoring are available for future predictions with group metadata.

Historical v4 offline re-evaluation command (the saved results predate v5 parser changes; rerunning uses current scoring code). This is not an unseen v5 evaluation:

```bash
python -m training.reevaluate_offline --dataset-dir training/data/v4 --output-dir reports/offline-v4
```

`LaTeXC` / `LaTeX-130K` source attribution has not been verified; their generic conversion script does not establish provenance. They are not primary evidence for this re-evaluation.

## 3. LLaMA-Factory Training

Use an isolated Python 3.11 environment with LLaMA-Factory and its training dependencies installed. The 3090 profile uses BF16 and FlashAttention-2.

Final v3 LoRA configuration:

| item | value |
| --- | --- |
| Base checkpoint | `Qwen/Qwen3-4B-Instruct-2507` |
| LoRA rank / alpha / dropout | `r=64`, `alpha=128`, `dropout=0.05` |
| LoRA target modules | `all` linear layers |
| Epochs / optimizer steps | 3.0 epochs, 495 optimizer steps |
| Batch shape | per-device batch 4, gradient accumulation 4, effective batch 16 |
| Precision / attention | BF16, FlashAttention-2 |
| Learning rate schedule | `1.5e-5`, cosine decay, warmup ratio `0.05` |
| Eval / save cadence | eval every 100 steps, save every 100 steps |
| Best checkpoint | `checkpoint-495`, selected by `eval_loss=0.03259` |

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

`run_lora_inference` still defaults to the historical `training/data/latex_formula_eval_clean.jsonl`; use `--eval-file training/data/v5/latex_formula_eval_clean.jsonl` explicitly for a future v5 run. `math_accuracy` is the primary metric. It counts mathematically equivalent formulas even when harmless layout choices differ, while still rejecting variable drift when the user input explicitly names variables. `format_compliance_accuracy` is reported separately for exact canonical-dialect adherence. The report also retains exact, canonical, symbol-fidelity, legacy semantic, parse-coverage, per-layer, and per-formula-family metrics.

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

## 6. External Benchmarks

External benchmark data and reports are generated under ignored directories (`benchmarks/` and `reports/`). Downloading datasets and installing benchmark packages are manual steps.

### LaTeXC / LaTeX-130K

Prepare the data manually, then convert it into the repository's JSONL inference format:

```bash
python -m training.prepare_latexc_benchmark \
  --input /path/to/LaTeXC/data \
  --output benchmarks/latexc_eval.jsonl
```

If automatic field detection fails, rerun with explicit field names:

```bash
python -m training.prepare_latexc_benchmark \
  --input /path/to/LaTeXC/data \
  --output benchmarks/latexc_eval.jsonl \
  --source-field noisy \
  --target-field corrected
```

Smoke inference first:

```bash
python -m training.run_lora_inference \
  --adapter saves/qwen3-4b-latex-correction/lora/sft-v3 \
  --eval-file benchmarks/latexc_eval.jsonl \
  --out reports/latexc-v3-smoke-predictions.jsonl \
  --limit 100
```

Evaluate the smoke run with the paper-style correction metrics:

```bash
python -m training.evaluate_text_correction \
  --predictions reports/latexc-v3-smoke-predictions.jsonl \
  --report reports/latexc-v3-smoke-eval.md \
  --json reports/latexc-v3-smoke-eval.json
```

For the full LaTeXC run, remove `--limit` and write to `reports/latexc-v3-predictions.jsonl`. `evaluate_text_correction` reports Exact Match, normalized Exact Match, character-level BLEU-4, and whitespace-insensitive CER.

### GSM8K and Hendrycks MATH

Use `lm-evaluation-harness` against both the base model and the merged BF16 SFT model to check whether the LoRA damaged general math reasoning. Keep prompts and harness settings identical between the two runs.

```bash
lm_eval --model hf \
  --model_args pretrained=Qwen/Qwen3-4B-Instruct-2507,trust_remote_code=True \
  --tasks gsm8k \
  --batch_size auto \
  --output_path reports/lm-eval-qwen3-4b-base-gsm8k.json
```

```bash
lm_eval --model hf \
  --model_args pretrained=saves/qwen3-4b-latex-correction/merged/sft-v3-bf16,trust_remote_code=True \
  --tasks gsm8k \
  --batch_size auto \
  --output_path reports/lm-eval-qwen3-4b-sft-v3-gsm8k.json
```

```bash
lm_eval --model hf \
  --model_args pretrained=Qwen/Qwen3-4B-Instruct-2507,trust_remote_code=True \
  --tasks hendrycks_math \
  --batch_size auto \
  --output_path reports/lm-eval-qwen3-4b-base-hendrycks-math.json
```

```bash
lm_eval --model hf \
  --model_args pretrained=saves/qwen3-4b-latex-correction/merged/sft-v3-bf16,trust_remote_code=True \
  --tasks hendrycks_math \
  --batch_size auto \
  --output_path reports/lm-eval-qwen3-4b-sft-v3-hendrycks-math.json
```
