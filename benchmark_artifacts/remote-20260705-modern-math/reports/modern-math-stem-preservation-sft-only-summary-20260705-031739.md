# SFT v3 Modern Math/STEM Preservation Check

Generated: 2026-07-05T03:17:39+08:00
Remote project: `/mnt/RC10/qwen-latex/Qwen-Desktop-Assistant-Classic`
Git HEAD: `c3060b1`
GPU: `NVIDIA GeForce RTX 3090, 24576 MiB, 595.71.05`
lm-eval version: `0.4.12`

This is a conservative SFT v3 preservation check. Base comparison is intentionally omitted in this rerun because existing Base data is being reused externally. This is not a leaderboard claim; the primary project success criterion remains the LaTeX correction clean evaluation.

## Runs

| label | model | tasks | rc | log | output | result json |
| --- | --- | --- | ---: | --- | --- | --- |
| sft_v3 | `saves/qwen3-4b-latex-correction/merged/sft-v3-bf16` | `hendrycks_math500,aime25` | `0` | `reports/lm-eval-modern-math-sft-v3-20260704-192355.log` | `reports/lm-eval-modern-math-sft-v3-20260704-192355` | `reports/lm-eval-modern-math-sft-v3-20260704-192355/saves__qwen3-4b-latex-correction__merged__sft-v3-bf16/results_2026-07-05T03-00-06.782752.json` |
| sft_v3_gpqa | `saves/qwen3-4b-latex-correction/merged/sft-v3-bf16` | `gpqa_diamond_cot_zeroshot` | `0` | `reports/lm-eval-modern-math-sft-v3-gpqa-20260705-030007.log` | `reports/lm-eval-modern-math-sft-v3-gpqa-20260705-030007` | `reports/lm-eval-modern-math-sft-v3-gpqa-20260705-030007/saves__qwen3-4b-latex-correction__merged__sft-v3-bf16/results_2026-07-05T03-17-38.120931.json` |

## SFT v3 Results

| task | metric | value |
| --- | --- | ---: |
| `hendrycks_math500` | `exact_match,none` | 0.002000 |
| `aime25` | `exact_match,none` | 0.366667 |
| `gpqa_diamond_cot_zeroshot` | `exact_match,flexible-extract` | 0.085859 |

## Notes

- Task names were detected previously with `lm-eval ls tasks` and prioritized as `hendrycks_math500`, `aime25`, and `gpqa_diamond_cot_zeroshot`.
- Runs use `dtype=bfloat16` and `batch_size=auto`.
- GPQA access was previously verified with the active HuggingFace token.
