# Qwen3 4B LaTeX Correction SFT

This repository contains a reproducible Qwen3 4B SFT workflow for restoring noisy, colloquial, or pseudocode-like math descriptions into canonical LaTeX formulas. It also keeps the original local desktop assistant that started the project.

## Release

| item | value |
| --- | --- |
| Base model | `Qwen/Qwen3-4B-Instruct-2507` |
| Fine-tuning method | LoRA, rank 64, alpha 128 |
| Training framework | LLaMA-Factory |
| Evaluation split | `latex_formula_eval_clean`, 292 examples |
| Primary metric | Math-only accuracy via the local LaTeX AST matcher |

| model | math accuracy | format compliance | exact accuracy | parse coverage |
| --- | ---: | ---: | ---: | ---: |
| Base Qwen3-4B-Instruct-2507 | 13.36% | 2.40% | 2.40% | 36.99% |
| DeepSeek V4 Pro baseline | 69.86% | 41.78% | 21.23% | 97.95% |
| Qwen3-4B LaTeX Correction LoRA v3 | 98.97% | 83.22% | 83.22% | 100.00% |

The SFT model is trained to return formula-only output in the repository's canonical LaTeX dialect: standard fractions, `bmatrix` matrices, and braced superscripts/subscripts. The current inference prompt uses a two-section system message with a role definition followed by concrete formatting examples.

`math_accuracy` is the primary score: it checks whether the mathematical structure is correct while allowing harmless presentation differences. `format_compliance_accuracy` remains separate and stricter, measuring whether the output follows the exact canonical dialect expected by the desktop assistant workflow.

## Result Interpretation

### 1. Did the SFT work?

Yes. On the cleaned fixed eval split, LoRA v3 moved the task from a weak base-model behavior to a reliable formula-restoration model:

- Base Qwen3-4B-Instruct-2507: 13.36% math accuracy, 2.40% exact accuracy.
- DeepSeek V4 Pro API baseline: 69.86% math accuracy, 21.23% exact accuracy.
- Qwen3-4B LaTeX Correction LoRA v3: 98.97% math accuracy, 83.22% exact accuracy.

This is the intended SFT shape: the model learned the mapping from noisy descriptions to canonical LaTeX, not merely a looser natural-language explanation style.

### 2. What happened to general math and coding ability?

The merged BF16 SFT v3 model was also checked with external `lm-eval` benchmarks on an RTX 3090. These are not the primary task metrics, but they test whether the specialization destroyed broad abilities. The latest preservation run adds modern reasoning/STEM checks: MATH-500-style `hendrycks_math500`, AIME25, and GPQA Diamond.

| Benchmark | SFT v3 result | Samples | What it checks | Interpretation |
| --- | ---: | ---: | --- | --- |
| GSM8K | 81.35% flexible / 68.16% strict | 1,319 | grade-school math reasoning | arithmetic reasoning remains usable after SFT |
| MATH / Hendrycks | 0.06% exact match | 5,000 | competition-style generated answers | this zero-shot non-chat harness is a poor fit for this release |
| MATH-500 / `hendrycks_math500` | 0.20% exact match | 500 | competition-style generated answers | same extraction/prompt caveat as Hendrycks MATH |
| AIME25 | 36.67% exact match | 30 | recent contest math | the model still solves a non-trivial subset after LaTeX SFT |
| GPQA Diamond CoT | 8.59% flexible extract | 198 | graduate-level science QA | weak in this harness; likely prompt/extraction and non-thinking-model limitations |
| MMLU | 70.68% | 14,042 | broad 57-subject knowledge | no obvious general-knowledge collapse |
| HumanEval | 71.95% pass@1 | 164 | Python code generation | no obvious coding collapse |

The most important preservation checks here are MMLU, HumanEval, GSM8K, and AIME25: despite specializing a 4B non-thinking model for strict LaTeX output, broad knowledge, coding, and short-form math reasoning did not collapse. The extremely low Hendrycks MATH / MATH-500 exact-match result should be treated as a benchmark compatibility issue until rerun with a chat-template prompt that asks for a boxed final answer and a Qwen-compatible answer extractor.

### 3. Why is the LaTeX output accurate?

The strongest gains came from reducing output entropy before training:

- The frozen source data is split into clean, noisy, hard, and targeted layers, then quality-reviewed before splitting.
- Training targets use deterministic `canonical_output`, not free-form original labels.
- Canonicalization removes avoidable dialect choices: fractions use `\frac{...}{...}`, matrices use `bmatrix`, and superscripts/subscripts are braced.
- The system prompt is stored per sample and defines a narrow formula-only role plus concrete formatting examples.
- The LoRA profile targets all linear layers with rank 64 / alpha 128, BF16, low learning rate `1.5e-5`, and clean eval monitoring.
- The evaluator separates math correctness from formatting compliance, so semantic success and canonical-dialect success can be diagnosed independently.

In short, the model is good because the dataset no longer asks it to guess one of many valid LaTeX dialects. The SFT turns a strong general model into a narrow canonical transducer for this desktop assistant workflow.

### 4. External model context

These figures are context, not a single leaderboard: benchmark variants, prompts, chat templates, answer extraction, reasoning budget, and tool access differ. Our release should be judged primarily by its local LaTeX restoration task, then by preservation checks.

#### Same-size and near-size controls

| Model / source | Scale | AIME | MATH-500 | GPQA Diamond / GPQA | Other signal | Notes |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Qwen3-4B LaTeX Correction LoRA v3 | 4B | AIME25 36.67% | `hendrycks_math500` 0.20% | GPQA Diamond CoT 8.59% | MMLU 70.68%, HumanEval 71.95%, local LaTeX math 98.97% | This repository's measured BF16 SFT v3 run |
| [Qwen3-4B-Instruct-2507 official card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) | 4B | AIME25 47.4 | - | GPQA 62.0 | MMLU-Pro 69.6, MultiPL-E 76.8 | Official non-thinking base-family reference; different harness |
| [Qwen3-4B-Thinking-2507 official card](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507) | 4B | AIME25 81.3 | - | GPQA 65.8 | MMLU-Pro 74.0, LiveCodeBench 55.2 | Same size but reasoning-specialized thinking model |
| [DeepSeek-R1-Distill-Qwen-7B](https://huggingface.co/deepseek-ai/DeepSeek-R1) | 7B | AIME2024 55.5 | 92.8 | 49.1 | LiveCodeBench 37.6 | Distilled reasoning model, not a formula-correction SFT |
| [DeepSeek-R1-Distill-Llama-8B](https://huggingface.co/deepseek-ai/DeepSeek-R1) | 8B | AIME2024 50.4 | 89.1 | 49.0 | LiveCodeBench 39.6 | Near-size open reasoning control |

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

### 5. Benchmark caveats and next controls

The benchmark story is mixed in a useful way:

- Strength: the main LaTeX task is clearly solved for this dataset: 98.97% math accuracy and 83.22% exact canonical-format accuracy on the cleaned 292-example eval split.
- Strength: MMLU 70.68% and HumanEval 71.95% are strong for a specialized 4B LoRA and do not show catastrophic forgetting. These two are the cleanest broad-capability preservation signals in this run.
- Strength: AIME25 36.67% shows non-trivial modern contest-math retention, even though the model was trained for formula restoration rather than long-chain theorem solving.
- Weakness: GPQA Diamond 8.59% is poor and should be read as "not a graduate science QA model" under this prompt/harness.
- Weakness: Hendrycks MATH and MATH-500 exact-match are not credible capability estimates for this release until the prompt, chat template, reasoning length, and answer extraction are aligned with the model family.
- Benchmark issue: official Qwen and DeepSeek numbers use different prompts, reasoning budgets, sampling, and sometimes thinking-mode models. The tables above are reference controls, not apples-to-apples leaderboard claims.
- Next benchmark controls: rerun MATH-500 and GPQA with a Qwen-style chat prompt asking for `\boxed{}` final answers; run Base Qwen3-4B-Instruct-2507 under the exact same harness; add LaTeX-130K/CER/BLEU/EM once that dataset is locally staged.

Full local artifacts from the remote runs are kept under `benchmark_artifacts/remote-20260704/` and `benchmark_artifacts/remote-20260705-modern-math/`.

## Model Artifacts

The release is split by runtime format:

- Full BF16 merged model: [xu2409324124/qwen3-4b-latex-correction-v3-bf16](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v3-bf16)
  - Use this for Transformers, vLLM-compatible conversion, further fine-tuning, or producing new quantizations.
- GGUF Q4_K_M model: [xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m)
  - Use this for llama.cpp, Ollama, LM Studio, and other GGUF local-inference runtimes.

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
- generating fixed train/eval splits for LLaMA-Factory
- running smoke and full LoRA training
- running base-model and LoRA inference baselines
- evaluating exact, canonical, symbol-fidelity, semantic, and parse-coverage metrics
- exporting BF16 and GGUF release artifacts

## Desktop Assistant

The original desktop assistant is still available as a lightweight local Ollama client with a classic Tkinter UI.

### Prerequisites

1. Install [Ollama](https://ollama.com/).
2. Pull a local Qwen model:

```bash
ollama pull qwen2.5:1.5b
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
