# v5 Colab smoke — 2026-10-23

Passed on an A100 40GB using the public original `Qwen/Qwen3-4B-Instruct-2507` base. Five optimizer steps completed in 21.985 seconds; the saved checkpoint reloaded and generated two development predictions. Training mean loss was 0.663286; development loss was 0.270646 on 64 examples. These are execution checks, not formula accuracy or evidence of generalization. No full SFT or baseline/checkpoint comparison was launched.

The first attempt stopped before training: Arrow could not represent heterogeneous AST arrays under `metadata.signature_evidence`. The entry point now creates a per-run flat dataset containing `instruction/input/output`, with a separate source map and unchanged audited source exports. Both the train and development registry preserve the system/prompt/response mapping. The retry used the same original model and smoke configuration.

The working stack was Python 3.13.15, PyTorch 2.11.0+cu130, LLaMA-Factory 0.9.5, Transformers 4.57.6, PEFT 0.18.1, Accelerate 1.11.0 and Datasets 4.0.0. A separate venv reused Colab's CUDA PyTorch; the existing Transformers 5 environment was not used for training.

Logs, metrics and reload predictions were downloaded before terminating the runtime. Smoke adapter weights were temporary and were not retained as a release. Colab confirmed **0 active assignments**, **0.00 units/hour**, and **398.27 units remaining** after termination. The temporary five-minute progress reminder was removed. All 127 local tests passed.

See [machine-readable results](result.json) for model revision, runtime versions, training steps and metrics. Full development baseline and SFT checkpoint evaluation remain future work.
