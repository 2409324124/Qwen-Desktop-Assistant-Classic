# Remote Modern Math/STEM Benchmark Artifacts - 2026-07-05

Source remote: `miku@100.66.104.25:/mnt/RC10/qwen-latex/Qwen-Desktop-Assistant-Classic`

Model: `saves/qwen3-4b-latex-correction/merged/sft-v3-bf16`

Generated summary: `reports/modern-math-stem-preservation-sft-only-summary-20260705-031739.md`

## Result Files

| Task group | Result JSON | Log |
| --- | --- | --- |
| `hendrycks_math500,aime25` | `reports/lm-eval-modern-math-sft-v3-20260704-192355/saves__qwen3-4b-latex-correction__merged__sft-v3-bf16/results_2026-07-05T03-00-06.782752.json` | `reports/lm-eval-modern-math-sft-v3-20260704-192355.log` |
| `gpqa_diamond_cot_zeroshot` | `reports/lm-eval-modern-math-sft-v3-gpqa-20260705-030007/saves__qwen3-4b-latex-correction__merged__sft-v3-bf16/results_2026-07-05T03-17-38.120931.json` | `reports/lm-eval-modern-math-sft-v3-gpqa-20260705-030007.log` |

## Metrics

| Benchmark | Metric | Value | Samples |
| --- | --- | ---: | ---: |
| `hendrycks_math500` | `exact_match,none` | 0.002000 | 500 |
| `aime25` | `exact_match,none` | 0.366667 | 30 |
| `gpqa_diamond_cot_zeroshot` | `exact_match,flexible-extract` | 0.085859 | 198 |
| `gpqa_diamond_cot_zeroshot` | `exact_match,strict-match` | 0.000000 | 198 |

## Notes

- This is an SFT-only preservation run. The Base run was intentionally not continued because the user requested using existing Base/reference data instead.
- These numbers are not leaderboard claims. They are local preservation checks for the LaTeX Correction LoRA v3 model.
- The low MATH-500 and GPQA scores need prompt/extraction follow-up before being interpreted as model capability limits.
