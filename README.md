# Qwen3 4B LaTeX Correction SFT

This repository contains a reproducible Qwen3 4B SFT workflow for restoring noisy, colloquial, or pseudocode-like math descriptions into canonical LaTeX formulas. It also keeps the original local desktop assistant that started the project.

## Historical v3 Release

| item | value |
| --- | --- |
| Base model | `Qwen/Qwen3-4B-Instruct-2507` |
| Fine-tuning method | LoRA SFT, `r=64`, `alpha=128`, `dropout=0.05`, target `all` linear layers |
| Training length | 3.0 epochs, 495 optimizer steps |
| Training framework | LLaMA-Factory |
| Historical evaluation split | old `training/data/latex_formula_eval_clean.jsonl`, 292 examples |
| Historical metric | Old permissive local LaTeX AST score; not the current v5 protocol |
| Release models | BF16: [`xu2409324124/qwen3-4b-latex-correction-v3-bf16`](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v3-bf16); GGUF Q4_K_M: [`xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m`](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m) |

### Historical v3 Training Recipe

| item | value |
| --- | --- |
| Base checkpoint | `Qwen/Qwen3-4B-Instruct-2507` |
| LoRA rank / alpha / dropout | `r=64`, `alpha=128`, `dropout=0.05` |
| LoRA target modules | `all` linear layers |
| Precision / attention | BF16, FlashAttention-2 |
| Epochs / global steps | 3.0 epochs, 495 optimizer steps |
| Batch shape | per-device batch 4, gradient accumulation 4, effective batch 16 |
| Sequence length | `cutoff_len=1024` |
| Learning rate schedule | `1.5e-5`, cosine decay, warmup ratio `0.05` |
| Eval / save cadence | eval every 100 steps, save every 100 steps, keep best by `eval_loss` |
| Best checkpoint | `checkpoint-495`, `eval_loss=0.03259` |
| Final train metrics | `train_loss=0.1066`, runtime 26m15s |

These are archived old-split scores from the old permissive evaluator. Label errors and leakage prevent treating them as v5 accuracy or independent generalization evidence. No measured v5 accuracy is available.

| model | historical math | historical combined format | historical exact | historical parse coverage |
| --- | ---: | ---: | ---: | ---: |
| Base Qwen3-4B-Instruct-2507 | 13.36% | 2.40% | 2.40% | 36.99% |
| DeepSeek V4 Pro baseline | 69.86% | 41.78% | 21.23% | 97.95% |
| Qwen3-4B LaTeX Correction LoRA v3 | 98.97% | 83.22% | 83.22% | 100.00% |

The SFT model is trained to return formula-only output in the repository's canonical LaTeX dialect: standard fractions, `bmatrix` matrices, and braced superscripts/subscripts. The current inference prompt uses a two-section system message with a role definition followed by concrete formatting examples.

The current v5 `math_accuracy` preserves free variables, constants, operator types and scope while allowing supported presentation differences. `output_protocol_compliance_accuracy` independently checks output form. The compatibility field `format_compliance_accuracy` combines mathematical correctness with a structural-format match. These revised metrics do not retroactively validate the historical table.

## v5 formula structure and related-family isolation

The current preparation pipeline uses full structural/template signatures and an explicit registry covering all 58 source templates. Related formulas are assigned together; Symbol Boundary is a separate diagnostic. v4's zero-overlap checks covered only its registered names, source and text keys, and did not establish absence of related-formula leakage. See [v5 protocol and limits](training/DATA_V5.md) and [the generated group audit](training/data/v5/group_audit.md). The allocator targets 80/10/10 samples with intact connected groups and category soft objectives; it does not row-shuffle formulas. Current validation covers CPU planning and mocked subprocesses only: no real v5 training, inference or Colab session has run. The new [v5 experiment workflow](training/README.md#3-v5-training-and-development-evaluation) defaults to dry-run plans, has a separate 5-step smoke profile and compares the base plus every completed SFT checkpoint on development only. GPU/dependency compatibility and model accuracy remain unverified.

## v4 data audit and offline re-evaluation

The figures above are historical permissive scores, not independent generalization evidence. The 2026-10 audit found incorrect BCE labels, ambiguous/colliding symbols, formula leakage, and permissive free-variable renaming. See [the v4 protocol](training/DATA_V4.md) and the generated [paired offline report](reports/offline-v4/comparison.md). Frozen sources and historical predictions are retained.

## Result Interpretation (historical scores)

### 1. Did the SFT work?

The original report recorded the following results on the old fixed split with the old permissive evaluator. Label errors and train/eval leakage prevent interpreting them as independent reliability evidence:

- Base Qwen3-4B-Instruct-2507: 13.36% math accuracy, 2.40% exact accuracy.
- DeepSeek V4 Pro API baseline: 69.86% math accuracy, 21.23% exact accuracy.
- Qwen3-4B LaTeX Correction LoRA v3: 98.97% math accuracy, 83.22% exact accuracy.

The revised evaluator preserves free symbols, operator types and scope. Historical scores alone do not establish whether the model learned transferable formula restoration.

### 2. What changed versus the base model?

The historical local LaTeX evaluation used the same 292-example `latex_formula_eval_clean` split with the same evaluator. General benchmark rows use the SFT v3 `lm-eval` run and published Qwen model-card numbers for the base model, so they are reference comparisons rather than same-harness A/B tests.

| Area | Base Qwen3-4B-Instruct-2507 | SFT v3 | Delta / interpretation |
| --- | ---: | ---: | --- |
| Local LaTeX math accuracy | 13.36% | 98.97% | Historical permissive score; leakage and label errors require revised evaluation |
| Local exact / format accuracy | 2.40% | 83.22% | Historical change on the old split; not v5 validation |
| Local parse coverage | 36.99% | 100.00% | Outputs became consistently parseable by the project evaluator |
| MMLU-Pro | 69.6% published | 63.54% measured | About 6.1 points lower, but broad STEM/reasoning did not collapse |
| IFEval | 83.4% published | 80.96% strict / 83.73% loose | Instruction following is broadly preserved |
| GPQA | 62.0% published | 29.19% measured | Weaker in this run or not harness-comparable; not a science-QA release |
| MATH-500 | not listed on base card | 0.00% measured | Extraction-sensitive diagnostic; audit required before interpreting math ability |

The runs suggest a task-specific change in behavior, but unmatched benchmark protocols and extraction failures do not establish a causal capability tradeoff. Training overfitting or forgetting requires comparable independent evaluations across checkpoints.

### 3. What happened to general abilities?

The merged BF16 SFT v3 model was evaluated with external `lm-eval` benchmarks on an RTX 3090. The table below retains completed historical runs, plus an extraction-sensitive MATH-500 diagnostic. Without matched base-model runs, these results do not independently establish capability preservation.

| Benchmark | Metric | SFT v3 result | Samples | Status |
| --- | --- | ---: | ---: | --- |
| IFEval | prompt-level strict / loose | 80.96% / 83.73% | 541 | full official run |
| IFEval | instruction-level strict / loose | 86.93% / 88.85% | 541 | full official run |
| GPQA | `acc_norm` | 29.19% | 448 | full official run |
| MuSR | `acc_norm` | 41.01% | 756 | full official run |
| MMLU-Pro | `exact_match`, custom extract, 5-shot | 63.54% ± 0.42% | 12,032 | vLLM full official run |
| BBH CoT zeroshot | `exact_match`, flexible extract | 49.09% ± 0.51% | 6,511 | vLLM full official run |
| MATH-500 / `hendrycks_math500` | `exact_match` | 0.00% | 500 | vLLM full run; needs sample audit before capability interpretation |

These results show that the LaTeX SFT did not simply turn the base model into a brittle formatter: instruction following remains strong, and multi-choice science/reasoning benchmarks still produce meaningful non-random scores. They should not be read as a claim that this LoRA is a general reasoning model; it is a formula-restoration model with preservation checks.

The following runs are diagnostic only. They used earlier harnesses, limited sample counts, or prompt/extraction settings that are not yet paper-grade comparable:

| Benchmark | Diagnostic result | Samples | Why diagnostic |
| --- | ---: | ---: | --- |
| GSM8K | 81.35% flexible / 68.16% strict | 1,319 | earlier HF backend run; useful retention signal, not current vLLM protocol |
| MMLU | 70.68% | 14,042 | earlier preservation run; keep as diagnostic until the vLLM protocol is rerun/reported |
| HumanEval | 71.95% pass@1 | 164 | earlier preservation run; useful but outside current vLLM benchmark set |
| AIME25 | 36.67% exact match | 30 | small benchmark; sensitive to prompt and extraction |
| Hendrycks MATH | 0.06% exact match | 5,000 | known prompt/extraction mismatch for this release |
| MMLU-Pro | 54.14% | 50 | pilot limit run only |
| BBH | 80.19% flexible extract | 20 | pilot limit run only |

The vLLM full run was launched with `--log_samples`, so failure cases can be audited after the headline metrics. The first priority is MATH-500: a 0% official exact-match score is almost certainly not enough evidence by itself to distinguish mathematical failure from final-answer extraction or formatting failure.

MMLU-Pro strongest areas:

| area | score | samples |
| --- | ---: | ---: |
| math | 84.23% | 1,351 |
| biology | 82.01% | 717 |
| economics | 75.71% | 844 |
| chemistry | 70.85% | 1,132 |
| physics | 70.28% | 1,299 |

MMLU-Pro weakest areas:

| area | score | samples |
| --- | ---: | ---: |
| law | 32.24% | 1,101 |
| engineering | 40.56% | 969 |
| history | 48.82% | 381 |
| philosophy | 52.71% | 499 |
| other | 54.00% | 924 |

BBH strongest areas:

| area | score | samples |
| --- | ---: | ---: |
| boolean expressions | 95.60% | 250 |
| tracking shuffled objects, 3 objects | 92.40% | 250 |
| reasoning about colored objects | 90.40% | 250 |
| penguins in a table | 87.67% | 146 |
| object counting | 86.80% | 250 |

BBH weakest areas:

| area | score | samples |
| --- | ---: | ---: |
| Dyck languages | 0.00% | 250 |
| tracking shuffled objects, 7 objects | 10.80% | 250 |
| temporal sequences | 11.20% | 250 |
| geometric shapes | 12.80% | 250 |
| tracking shuffled objects, 5 objects | 21.20% | 250 |

Remote artifact roots for follow-up analysis:

- `/mnt/RC10/qwen-latex/Qwen-Desktop-Assistant-Classic/reports/sft-v3-split-20260706-003415`
- `/mnt/RC10/qwen-latex/Qwen-Desktop-Assistant-Classic/reports/sft-v3-split-resume-20260706-011507`
- `/mnt/RC10/qwen-latex/Qwen-Desktop-Assistant-Classic/reports/sft-v3-vllm-formal-20260706-110320`

### 4. Current data and evaluation protocol

Frozen clean/noisy/hard and targeted source layers share quality review and versioned safe normalization. Connected source, structural, parameter-template and explicit related-family identities determine whole groups before splitting. Unknown families and unverified scopes are held for review; Symbol Boundary samples remain a separate diagnostic. Canonical targets retain determinant environments, meaningful fonts, operators and symbol identity while normalizing fractions and braced scripts.

The v5 LoRA recipe retains rank 64 / alpha 128 and learning rate `1.5e-5`, switches to SDPA with BF16, and saves all three epoch checkpoints. The development comparison reports raw and postprocessed micro/group-macro scores and independent protocol compliance. It ranks by postprocessed macro, then micro, and can recommend the unchanged base model. Test inference is reserved. This defines how a future measured improvement will be assessed; it is not evidence that a new model has already improved.

### 5. External small-model context

These figures are context, not a single leaderboard: benchmark variants, prompts, chat templates, answer extraction, reasoning budget, and tool access differ. Our release should be judged primarily by its local LaTeX restoration task, then by preservation checks.

The control rows below use published model-card or vendor benchmark numbers only. No extra control model was downloaded or run locally for this comparison.

| Model / source | Size / type | Strength | Weakness vs this release | Best use |
| --- | --- | --- | --- | --- |
| Qwen3-4B LaTeX Correction LoRA v3 | 4B non-thinking LoRA | Historical old-evaluator LaTeX math 98.97%, exact 83.22%; historical MMLU-Pro 63.54% | GPQA and MATH-500 are not strengths in the current run | Canonical LaTeX formula restoration for the desktop assistant |
| [Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) | 4B non-thinking base | More general: MMLU-Pro 69.6, GPQA 62.0, AIME25 47.4 | Historical old-evaluator formula scores: 13.36% math, 2.40% exact | General small-model assistant |
| [Qwen3-4B-Thinking-2507](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507) | 4B thinking model | Strong reasoning: AIME25 81.3, GPQA 65.8, MMLU-Pro 74.0 | Thinking output is longer and not trained for this canonical formula dialect | Compact reasoning tasks |
| [DeepSeek-R1-Distill-Qwen-7B](https://huggingface.co/deepseek-ai/DeepSeek-R1) | 7B reasoning distill | MATH-500 92.8, AIME2024 55.5, GPQA Diamond 49.1 | Larger and not a LaTeX-correction model | Math reasoning when format control is secondary |
| [DeepSeek-R1-Distill-Llama-8B](https://huggingface.co/deepseek-ai/DeepSeek-R1) | 8B reasoning distill | MATH-500 89.1, AIME2024 50.4, GPQA Diamond 49.0 | Larger and outside the Qwen ecosystem | Open reasoning baseline |

The release targets 4B formula restoration and formula-only output. This table does not establish current v5 task reliability or a causal capability tradeoff; those require matched independent evaluations.

#### Larger open-weight and frontier controls

| Model / source | Scale | AIME | MATH-500 | GPQA Diamond / GPQA | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| [DeepSeek-R1-Distill-Qwen-32B](https://huggingface.co/deepseek-ai/DeepSeek-R1) | 32B | AIME2024 72.6 | 94.3 | 62.1 | Open dense distilled reasoning model |
| [DeepSeek-R1](https://huggingface.co/deepseek-ai/DeepSeek-R1) | 671B total / 37B active | AIME2024 79.8 | 97.3 | 71.5 | Open MoE reasoning model; DeepSeek reports 32,768 max generation tokens |
| [Qwen3-235B-A22B-Thinking-2507 official card](https://huggingface.co/Qwen/Qwen3-235B-A22B-Thinking-2507) | 235B total / 22B active | AIME25 92.3 | - | GPQA 81.1 | Large open-weight thinking model |
| [OpenAI o4-mini](https://openai.com/index/introducing-o3-and-o4-mini/) / Qwen reference table | closed | AIME25 92.7; 99.5 with Python tool access | - | GPQA 81.4 | Tool-access AIME numbers are explicitly not comparable to no-tool local runs |
| OpenAI o3 / Qwen reference table | closed | AIME25 88.9 | - | GPQA 83.3 | Frontier reasoning context |
| Gemini 2.5 Pro / Qwen reference table | closed | AIME25 88.0 | - | GPQA 86.4 | Frontier reasoning context |
| Claude 4 Opus Thinking / Qwen reference table | closed | AIME25 75.5 | - | GPQA 79.6 | Frontier reasoning context |

### 6. Capability tradeoffs and caveats

The benchmark story is mixed in a useful way:

- Historical: the old evaluator reported 13.36% to 98.97% math accuracy and 2.40% to 83.22% exact accuracy. These are retained for comparison; the v4 audit invalidates a claim that the task was solved.
- Improved: formula-only output is much more stable, parse coverage reaches 100%, and the model follows the repository's canonical fraction, matrix, and superscript/subscript rules.
- Preserved: IFEval strict 80.96% / loose 83.73% shows strong instruction-following retention after a narrow LaTeX SFT.
- Preserved: MMLU-Pro 63.54% is a useful broad STEM/reasoning preservation signal for a 4B non-thinking formula SFT, especially with math at 84.23%.
- Mixed: BBH CoT zeroshot 49.09% is uneven; symbolic/simple reasoning tasks are strong, while Dyck languages and longer tracking tasks are weak.
- Regressed or unclear: GPQA `acc_norm` 29.19% is far below the base model's published GPQA reference and should not be marketed as a strength.
- Unclear: MATH-500 exact-match remains unusable as a capability estimate until sample audit separates mathematical errors from final-answer extraction or formatting failures.
- Diagnostic: MMLU 70.68%, HumanEval 71.95%, and AIME25 36.67% are useful signals, but they are not current vLLM full-protocol results.
- Benchmark issue: official Qwen and DeepSeek numbers use different prompts, reasoning budgets, sampling, and sometimes thinking-mode models. The tables above are reference controls, not apples-to-apples leaderboard claims.
- Next benchmark controls: audit logged MATH-500 and BBH samples first. Do not download more control models by default; use published model-card numbers unless a same-harness rerun is explicitly needed and the model is already cached or manually staged.

Full local artifacts from the remote runs are kept under `benchmark_artifacts/remote-20260704/`, `benchmark_artifacts/remote-20260705-modern-math/`, and `benchmark_artifacts/remote-20260706-vllm-formal/`.

## Model Artifacts

The release is split by runtime format:

Both artifacts come from the same v3 LoRA SFT run: `r=64`, `alpha=128`, `dropout=0.05`, all linear layers targeted, 3.0 epochs, and 495 optimizer steps. The BF16 repository is the merged full-precision release; the GGUF repository is the quantized local-inference release used by the desktop assistant.

- Full BF16 merged model: [xu2409324124/qwen3-4b-latex-correction-v3-bf16](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v3-bf16)
  - Use this for Transformers, vLLM-compatible conversion, further fine-tuning, or producing new quantizations.
- GGUF Q4_K_M model: [xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m)
  - Use this for llama.cpp, Ollama, LM Studio, and other GGUF local-inference runtimes.

Download examples:

```bash
huggingface-cli download xu2409324124/qwen3-4b-latex-correction-v3-bf16 --local-dir models/qwen3-4b-latex-correction-v3-bf16
huggingface-cli download xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m --include "*.gguf" --local-dir models/qwen3-4b-latex-correction-v3-gguf-q4-k-m
```

## Repository Layout

```text
.
├── data/frozen/phase1/      # frozen source JSONL files used to build train/eval splits
├── training/                # dataset preparation, LLaMA-Factory configs, inference, evaluation
├── tests/                   # unit tests for dataset, config, postprocess, and semantic evaluation
├── tools/data_generation/   # historical data generation and sampling utilities
├── archive/phase1/          # historical phase-1 datasets, reviews, audits, and handoff notes
├── main.py                  # original Tkinter desktop assistant
├── ollama_client.py         # local Ollama streaming client
└── summon.py / show.py      # desktop assistant helper scripts
```

Generated files are intentionally ignored: `training/data/`, `saves/`, and `reports/`.

## Training Workflow

The complete training and evaluation path is documented in [`training/README.md`](training/README.md). It covers:

- canonicalizing and cleaning the frozen formula dataset
- generating v5 connected-group train/development/test splits for LLaMA-Factory
- validating dry-run plans and explicitly launching separate v5 smoke/SFT profiles
- comparing the base and every completed SFT checkpoint on development with immutable model revisions
- reporting raw/postprocessed micro and group-macro scores, independent protocol compliance and provenance hashes
- exporting BF16 and GGUF release artifacts

## Desktop Assistant

The original desktop assistant is still available as a lightweight local Ollama client with a classic Tkinter UI.

### Prerequisites

1. Install [Ollama](https://ollama.com/).
2. Download this project's GGUF release, not the original base Qwen checkpoint, and create the Ollama alias used by the desktop client. This is the quantized v3 SFT model trained with LoRA `r=64` for 495 optimizer steps over 3.0 epochs:

   Model link: [xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m)

```bash
huggingface-cli download xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m --include "*.gguf" --local-dir models/qwen3-4b-latex-correction-v3-gguf-q4-k-m
GGUF=$(find "$PWD/models/qwen3-4b-latex-correction-v3-gguf-q4-k-m" -name "*.gguf" | head -n 1)
printf 'FROM %s\nPARAMETER temperature 0.1\n' "$GGUF" > Modelfile
ollama create qwen3-latex-correction:v3-q4-k-m -f Modelfile
```

### Install and Run

```bash
git clone git@github.com:2409324124/Qwen-Desktop-Assistant-Classic.git
cd Qwen-Desktop-Assistant-Classic
conda create -n qwen-assistant python=3.10
conda activate qwen-assistant
pip install httpx pyperclip pynput
python main.py
```

The window starts hidden. Select text in another application, press `Alt + Shift + Q`, and the assistant opens with the captured context.

## License

MIT License. Feel free to modify and adapt.
