# v5.2 reviewed-data SFT — 2026-10-23

The fresh Qwen3-4B LoRA run completed 2 epochs / 60 optimizer steps on an A100 40GB. Both epoch adapters and all development predictions/reports are archived in the private [Hugging Face repository](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v5-2/tree/3721b25f40f3e9383d99b2991ba9dd0e4749dc86). Colab was released; server inventory returned zero active assignments and usage 0.00/hr. Observed balance changed from 395.41 to 393.54 CU (1.87 CU).

## Results on the same 56 reviewed development records

| Model | Correct | Raw / postprocessed formula accuracy | Group macro accuracy | Output protocol compliance |
| --- | ---: | ---: | ---: | ---: |
| Original base | 33/56 | 58.93% / 58.93% | 77.22% | 96.43% |
| checkpoint-30, epoch 1 | 48/56 | 85.71% / 85.71% | 92.12% | 98.21% |
| checkpoint-60, epoch 2 | 48/56 | 85.71% / 85.71% | 92.12% | 98.21% |

Select **checkpoint-30**, following the frozen rule: postprocessed macro accuracy, then micro accuracy, then base/earlier checkpoint on a tie. This improves formula accuracy by 26.79 percentage points over the same-run base. The second epoch provides no additional measured formula-accuracy gain. Development loss decreases from 0.0403756 to 0.0376032; these two checkpoints do not establish an overfitting diagnosis.

| Development group | Records | Base correct | cp30 correct | cp60 correct |
| --- | ---: | ---: | ---: | ---: |
| Quadratic Formula | 2 | 2 | 2 | 2 |
| Linear activation / RNN / ReLU | 21 | 12 | 18 | 18 |
| Coulomb / universal gravitation | 4 | 4 | 4 | 4 |
| Block / ellipsis matrix layouts | 29 | 15 | 24 | 24 |

The development set has only four groups, including groups of two and four records, and lacks calculus. These are development-selection results, not final-test or broad OOD results. The 56 test records were checked for membership/isolation but never used for inference, scoring or model selection. The remaining eight unverified outputs are not automatically counted correct. Labels and the scorer were frozen before this run; no prediction-driven label changes were made.

## Run and saved artifacts

- Run ID: `v52-20261023T073851Z-d239b61a`; source commit `62bc915db68a2cfc3fd0977d4194c7fd3679a1ad`.
- Data: `v5.2-reviewed-all-splits`, 476 training / 56 development / 56 test records, preserving reviewed split membership and grouped isolation.
- Original base: `Qwen/Qwen3-4B-Instruct-2507`, revision `cdbee75f17c01a7cc42f958dc650907174af0554`; no prior adapter/resume input.
- LoRA rank 64 / alpha 128 / dropout 0.05, all linear targets, LR 1.5e-5, BF16, SDPA; effective config and trainer states are retained in `training/`.
- [Development comparison](development/comparison.md), [machine-readable comparison](development/comparison.json), per-model predictions, metrics and environment/protocol manifest are retained under `development/`.
- [Selected cp30 adapter](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v5-2/tree/3721b25f40f3e9383d99b2991ba9dd0e4749dc86/runs/v52-20261023T073851Z-d239b61a/sft/checkpoint-30) and [cp60 adapter](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v5-2/tree/3721b25f40f3e9383d99b2991ba9dd0e4749dc86/runs/v52-20261023T073851Z-d239b61a/sft/checkpoint-60) each include LoRA weights, adapter config and trainer state. Optimizer/scheduler/RNG state is excluded; this is not an exact trainer-resume archive.
- Final reports/provenance commit: `6ac55090f0581d475dab44a6f6ef0c2e4169c534`; model-card commit: `3721b25f40f3e9383d99b2991ba9dd0e4749dc86`. Upload and shutdown receipts are in `receipts/`.

## Execution note

An initial allocation was released during setup because the agent misread sandbox PID visibility and created a duplicate local supervisor. A single-instance lock was then added and the actual run completed in a new session. The automated five-step smoke also completed before the user's cancellation was applied; it did not initialize or resume the formal SFT. This was an operational mistake, not an approved prerequisite for future runs. Future Colab operations should use direct CLI commands without additional Python orchestration or unsolicited smoke runs. No further training was launched after the two-epoch run.

The Git Markdown reports trim trailing whitespace for display. Exact raw outputs remain unchanged in predictions JSONL and the immutable HF archive.
