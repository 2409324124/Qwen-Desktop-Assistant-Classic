# Qwen3 4B LaTeX Correction Training

This workflow trains and evaluates a LoRA adapter for LaTeX formula correction. The source data is frozen under `data/frozen/phase1/`; historical generated dataset directories are generally ignored by Git. The reviewed `training/data/v5.2/` exports and their frozen review sources are tracked for reproducibility. See [the v5 grouping protocol](DATA_V5.md) and [historical v4 audit](DATA_V4.md); v5 has separate training configurations and a version-bound experiment entry point. Existing v3 configs and `training/data/*.jsonl` remain historical.

## Release Artifacts

The historical v5 run is archived in the private Hugging Face repository [xu2409324124/qwen3-4b-latex-correction-v5](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v5/tree/4dabecb3990e7dedd718afaa8696249fb82c0fa7). All three LoRA checkpoints (33, 66, 99) were uploaded and their remote weight contents verified. These are adapters trained on the original v5 data, not reviewed v5.2 models; load them with the original Qwen base. The archive includes adapter configuration and trainer state but excludes optimizer/scheduler state, so it is not an exact training-resume archive. See [the upload receipt](../reports/v5-hf-archive-20261023.json).

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

Frozen and targeted records share review, normalization and connected source/structure/template/near-family grouping. The explicit registry covers all 58 templates; unknown families or unverified signatures are quarantined. With seed 42 allocation targets 80/10/10 samples using whole connected groups. The allocator prioritizes sample-count deviation, then category coverage, group-count deviation and category-count deviation; it does not split groups to force every category into every set. Targeted records follow their group. Symbol Boundary records are diagnostic only. Output also includes `latex_formula_test.jsonl`, `latex_formula_diagnostic.jsonl`, `review_manifest.jsonl`, `group_manifest.jsonl`, `group_connections.jsonl` and `group_audit.md`; `eval_clean` aliases development. Per-sample and group-macro scoring are available for future predictions with group metadata.

Historical v4 offline re-evaluation command (the saved results predate v5 parser changes; rerunning uses current scoring code). This is not an unseen v5 evaluation:

```bash
python -m training.reevaluate_offline --dataset-dir training/data/v4 --output-dir reports/offline-v4
```

`LaTeXC` / `LaTeX-130K` source attribution has not been verified; their generic conversion script does not establish provenance. They are not primary evidence for this re-evaluation.

## 3. v5 Training and Development Evaluation

Use `training.run_v5_experiment` from the repository root. The default remains historical v5; select the reviewed dataset explicitly with `--data-version v5.2` on both training and evaluation commands. It verifies the selected source, rule, export and split identities before constructing a plan. The commands in this section without a version flag reproduce the historical v5 interface. **Without `--execute`, commands only validate local artifacts and print a plan; they do not contact Hugging Face or launch training/inference.** Prepare the data first so provenance hashes match the checked-out code:

```bash
python3 -B -m training.prepare_dataset --out-dir training/data/v5 --seed 42
python3 -B -m training.run_v5_experiment train --profile smoke
python3 -B -m training.run_v5_experiment train --profile sft
python3 -B -m training.run_v5_experiment evaluate --baseline-only
```

The dedicated [SFT configuration](qwen3_4b_lora_sft_v5.yaml) and [smoke configuration](qwen3_4b_lora_smoke_v5.yaml) use `training/data/v5`, LoRA rank 64 / alpha 128 / dropout 0.05, target `all`, learning rate `1.5e-5`, and the non-thinking Qwen3 template. They default to **SDPA and BF16**. SDPA avoids requiring the separate FlashAttention-2 extension; compatible PyTorch, Transformers, PEFT and LLaMA-Factory packages are still required. A real training execution checks that a CUDA GPU with BF16 support is available. At execution, the entry point creates `run_dir/training_data` with only string `instruction/input/output` columns for train and development. This avoids Arrow failures on heterogeneous AST audit metadata; original v5 exports remain unchanged, and a separate source map plus the run manifest bind every projected row to its audited source. Projection integrity is checked before and after training and before checkpoint comparison.

| Profile | Duration | Eval / save cadence | Experiment root |
| --- | --- | --- | --- |
| smoke | 5 optimizer steps, at most 64 source samples | every 5 steps | `saves/qwen3-4b-latex-correction/lora/smoke-v5` |
| sft | 3 epochs | every epoch; retain all 3 epoch checkpoints | `saves/qwen3-4b-latex-correction/lora/sft-v5` |

`load_best_model_at_end` is false: development `eval_loss` is a training diagnostic, not the final model-selection rule. `--run-dir` changes the experiment root. The entry point writes `effective_config.yaml` and `run_manifest.json` at that root and sets the effective HF output directory to its `checkpoints/` subdirectory:

```text
saves/qwen3-4b-latex-correction/lora/sft-v5/
  effective_config.yaml
  run_manifest.json
  checkpoints/
    checkpoint-N/
    ...
```

Training execution refuses an existing experiment root. Use a fresh `--run-dir` for another run; this entry point does not automatically resume a failed or partial run. These are commands for a future real GPU run, **not actions performed during this implementation**:

```bash
python3 -B -m training.run_v5_experiment train --profile smoke --execute
# Run only after the smoke run has checked real GPU and dependency compatibility.
python3 -B -m training.run_v5_experiment train --profile sft --execute
```

For a baseline plan and, later, an explicitly executed baseline:

```bash
python3 -B -m training.run_v5_experiment evaluate --baseline-only
python3 -B -m training.run_v5_experiment evaluate --baseline-only --execute
```

The default baseline results root is `reports/v5/base-development`. Use `--output reports/v5/base-development-run2` for a fresh result location; execution refuses an existing results root.

After a **completed SFT run**, inspect the comparison plan before executing it:

```bash
python3 -B -m training.run_v5_experiment evaluate \
  --run-dir saves/qwen3-4b-latex-correction/lora/sft-v5
python3 -B -m training.run_v5_experiment evaluate \
  --run-dir saves/qwen3-4b-latex-correction/lora/sft-v5 --execute
```

This evaluates the unchanged base model plus every saved `checkpoints/checkpoint-N`, sorted by optimizer step, on the same v5 development file. It rejects smoke runs, failed or partial SFT runs, missing adapter files and changed training configuration, data or evaluation protocol. A checkpoint comparison plan therefore requires real completed-run artifacts, even when `--execute` is omitted. The default comparison results root is `reports/v5/checkpoint-development`; `--output` selects a fresh alternative.

### Reviewed v5.2 training and evaluation

The [v5.2 SFT configuration](qwen3_4b_lora_sft_v5_2.yaml) uses the original public base `Qwen/Qwen3-4B-Instruct-2507`, **2 epochs**, epoch evaluation/saving and retention of both epoch checkpoints. The [v5.2 smoke configuration](qwen3_4b_lora_smoke_v5_2.yaml) uses **5 optimizer steps**, at most 64 source samples, and its own output root. Both retain the v5 LoRA settings, `1.5e-5` learning rate, SDPA and BF16. Adapter, resume and tokenized-source overrides are forbidden: each run starts from the original base.

Validate and print plans from the repository root:

```bash
python3 -B -m training.run_v5_experiment train --data-version v5.2 --profile smoke
python3 -B -m training.run_v5_experiment train --data-version v5.2 --profile sft
python3 -B -m training.run_v5_experiment evaluate --data-version v5.2 --baseline-only
```

After preparing the immutable base-model cache in the GPU environment, execute the selected plans:

```bash
# Direct formal training; optional smoke is not a prerequisite.
python3 -B -m training.run_v5_experiment train --data-version v5.2 --profile sft --execute
python3 -B -m training.run_v5_experiment evaluate --data-version v5.2 --baseline-only --execute
```

Only after the v5.2 SFT run completes, print and execute the base/checkpoint development comparison:

```bash
python3 -B -m training.run_v5_experiment evaluate --data-version v5.2 \
  --run-dir saves/qwen3-4b-latex-correction/lora/sft-v5.2
python3 -B -m training.run_v5_experiment evaluate --data-version v5.2 \
  --run-dir saves/qwen3-4b-latex-correction/lora/sft-v5.2 --execute
```

The default roots are `saves/qwen3-4b-latex-correction/lora/smoke-v5.2`, `saves/qwen3-4b-latex-correction/lora/sft-v5.2`, `reports/v5.2/base-development` and `reports/v5.2/checkpoint-development`. Use fresh `--run-dir` or `--output` paths for repeat executions. Historical v5 defaults remain unchanged.

The v5.2 verifier checks frozen source hashes under `training/reviews/v5_source`, review hashes under `training/reviews`, cleaning-code hashes under `training`, and export hashes under `training/data/v5.2`. It checks every accepted row against its original split, source and reviewed label, and checks all cross-split group keys. Training projections, manifests, checkpoint discovery and evaluation commands bind the same absolute data directory; development inference uses the repaired v5.2 labels. Test membership is verified, while test inference remains a separate final evaluation.

All 154 local tests passed. The v5.2 run has now completed: both epoch checkpoints scored 48/56 (85.71%), compared with the base at 33/56 (58.93%). The tie selects checkpoint-30. Weights and reports are saved in HF and Colab is released; see [the run report](../reports/v5.2-colab-sft-20261023/README.md). Future Colab operations use direct CLI commands, with no unsolicited smoke runs or additional Python orchestration.

## 4. v5 Metrics, Provenance and Current Validation

At execution, the entry point resolves an immutable Hugging Face base-model revision, then checks the local cache for all safetensors shards at that revision. Missing or incomplete model weights stop execution and print the exact `hf download MODEL --revision SHA` command for the user; the entry point does not automatically download the base model. Training records it in the effective configuration and manifest; checkpoint comparison reuses that training revision for both the base model and all adapters. An independent baseline-only execution records its own resolved revision, so a later checkpoint comparison runs the base again under the training revision rather than silently combining potentially different baselines.

For each candidate, the result directory contains `predictions.jsonl`, `metrics.json` and `report.md`. Predictions include the complete raw output, postprocessed output and source/group metadata. Raw and postprocessed metrics are reported separately, including sample micro accuracy, equal-weight group macro accuracy, per-group results, parsing coverage and independent output-protocol compliance. `format_compliance_accuracy` is the compatibility metric for **correct formula plus structural-format match**; it is not the independent `output_protocol_compliance_accuracy` syntax/output-form check. The current faithful math metric preserves free variables, constants, operator types and scope; unsupported equivalence is unverified, not scored correct.

`evaluation_manifest.json`, `comparison.json` and `comparison.md` record the comparison and selection. The training manifest locks the completed checkpoint set and its adapter config, weights and available `trainer_state.json` hashes. Evaluation rejects changed checkpoint artifacts. The manifests and comparison files bind the model revision, environment package versions, data/export identities, effective training configuration, adapter hashes, prediction SHA256 and evaluation-protocol hashes. Selection uses **postprocessed development macro math accuracy, then development micro accuracy**. A tie favors the base model, then the earlier checkpoint. If the base wins, the recommendation can be `base`; no SFT improvement is assumed. `--baseline-only` makes no checkpoint recommendation.

This workflow uses **development only** for selection. It verifies test membership/leakage metadata but does not run test inference or report test scores. The test set remains reserved for a separately specified final evaluation. The current development and test sets each contain only four groups and no calculus; see [DATA_V5.md](DATA_V5.md) for their composition and limits.

**The [2026-10-23 Colab smoke](../reports/v5-colab-smoke-20261023/README.md) passed on an A100 40GB:** five optimizer steps completed in 21.985 seconds, and the saved checkpoint reloaded for two development predictions. The runtime was terminated after result collection. All 127 local tests passed. The subsequent 3-epoch / 99-step formal run completed: frozen development scores were 25/64 for Base and 41/64 for cp66/cp99. Extra diagnostics and final test remain incomplete. The GPU was released. See [the complete training-data review and scorer-only reassessment](DATA_V5.md#v51-全量训练审查与已有预测复评2026-10-23): 476 reviewed training rows remain; no new training was run during that cleanup stage. The later v5.2 run is reported below.

The subsequent **v5.2 input/gold-only review** is complete: 476 training, 56 development and 56 test records remain, with 55 records quarantined across the three original splits. Both holdouts received two independent reviews without model predictions or scores. Original split ownership and historical grouping connections are preserved; all registered cross-split overlap checks are zero. See [DATA_V5.md](DATA_V5.md) and [the exported summary](data/v5.2/dataset_summary.json). During the cleanup stage, no inference, checkpoint selection or Colab training was run. The entry point now supports explicit `--data-version v5.2` for both training and evaluation; the default remains historical v5. The completed v5.2 run and saved artifacts are documented in [the run report](../reports/v5.2-colab-sft-20261023/README.md).

### Manual remote model prefetch

Only on SSH host `home-ms03`, the user downloads files of 1 GB or more manually. This restriction does not apply to Colab or other environments; authorized downloads there may be automated. The current experiment entry point still requires the immutable model to be prefetched. Account for network timeouts, proxies and cache location before execution. Prefetch the immutable model commit into the same Hugging Face cache used by the training/inference environment, for example:

```bash
# Replace the placeholder with the full immutable model commit, not a branch name.
hf download Qwen/Qwen3-4B-Instruct-2507 --revision "REPLACE_WITH_IMMUTABLE_COMMIT_SHA"
```

Alternatively, use the exact manual-download command printed by the first execution when its cache check fails, then retry with the same cached revision. Dry runs do not resolve a remote revision or download files. The entry point resolves the model revision when an execution starts. Confirm that revision is already cached; if the remote repository revision has changed since prefetch, manually fetch the newly resolved commit before running. The recorded revision, rather than a moving model name, identifies the run. The commands above do not claim that a model was downloaded in this implementation.

### Historical v3 recipe and evaluation

The preserved v3 configs use the old `training/data` split, BF16 / FlashAttention-2, 3 epochs / 495 optimizer steps, eval/save every 100 steps and historical `eval_loss` selection (`checkpoint-495`, `eval_loss=0.03259`). They do not define the v5 experiment:

```bash
llamafactory-cli train training/qwen3_4b_lora_smoke.yaml
llamafactory-cli train training/qwen3_4b_lora_sft_v3.yaml
```

New `run_lora_inference` invocations default to v5 development. Historical v3 commands must name their old evaluation file explicitly:

```bash
python3 -B -m training.run_lora_inference \
  --eval-file training/data/latex_formula_eval_clean.jsonl \
  --out reports/qwen3-4b-latex-correction-base-historical-predictions.jsonl
python3 -B -m training.run_lora_inference \
  --adapter saves/qwen3-4b-latex-correction/lora/sft-v3 \
  --eval-file training/data/latex_formula_eval_clean.jsonl \
  --out reports/qwen3-4b-latex-correction-lora-v3-historical-predictions.jsonl
```

The following values are archived **old-split, old-permissive-evaluator** results. Label errors, leakage and permissive variable renaming prevent interpreting them as v5 results or independent generalization evidence. Rerunning historical predictions with today's scorer may produce different values.

| model | historical math | historical combined format | historical exact | historical parse coverage |
| --- | ---: | ---: | ---: | ---: |
| Base Qwen3-4B-Instruct-2507 | 13.36% | 2.40% | 2.40% | 36.99% |
| DeepSeek V4 Pro baseline | 69.86% | 41.78% | 21.23% | 97.95% |
| Qwen3-4B LaTeX Correction LoRA v3 | 98.97% | 83.22% | 83.22% | 100.00% |

## 5. Historical v3 Export

This preserved config exports the historical v3 adapter; there is no automatically selected or exported v5 release. Export the v3 merged BF16 model:

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
