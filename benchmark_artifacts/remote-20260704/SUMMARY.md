# Remote Benchmark Artifacts - 2026-07-04

Source remote: `miku@100.66.104.25:/mnt/RC10/qwen-latex/Qwen-Desktop-Assistant-Classic`

Full result JSON: `/home/miku/Qwen-Desktop-Assistant-Classic/benchmark_artifacts/remote-20260704/reports/lm-eval-full-sft-v3-4bench/saves__qwen3-4b-latex-correction__merged__sft-v3-bf16/results_2026-07-04T08-04-03.943198.json`
Full run log: `/home/miku/Qwen-Desktop-Assistant-Classic/benchmark_artifacts/remote-20260704/reports/lm-eval-full-sft-v3-4bench-20260704-000729.log`
Evaluation elapsed: `sft_elapsed=7:56:35`

## Model

`saves/qwen3-4b-latex-correction/merged/sft-v3-bf16`

## Full 4-Benchmark Results

| Benchmark | Metric | Value | Samples |
| --- | --- | ---: | ---: |
| GSM8K | strict exact_match | 0.681577 | 1319 |
| GSM8K | flexible exact_match | 0.813495 | 1319 |
| MATH / hendrycks_math | exact_match | 0.000600 | 5000 |
| MMLU | acc | 0.706808 | 14042 |
| HumanEval | pass@1 | 0.719512 | 164 |

## MMLU Breakdown

| Group | Accuracy |
| --- | ---: |
| Humanities | 0.608714 |
| Other | 0.747023 |
| Social sciences | 0.805005 |
| STEM | 0.717729 |

## Notes

- Full Base run was intentionally stopped per user request; only SFT v3 full results are present.
- Smoke results for Base and SFT v3 are included under `reports/lm-eval-smoke-*`.
- HumanEval required `HF_ALLOW_CODE_EVAL=1` and `--confirm_run_unsafe_code`.
