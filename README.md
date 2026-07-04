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

The merged BF16 SFT v3 model was also checked with external `lm-eval` benchmarks on an RTX 3090. These are not the primary task metrics, but they test whether the specialization destroyed broad abilities.

| Benchmark | SFT v3 full-run result | What it checks | Interpretation |
| --- | ---: | --- | --- |
| GSM8K | 81.35% flexible / 68.16% strict | grade-school math reasoning | arithmetic reasoning remains usable after SFT |
| MATH / Hendrycks | 0.06% exact match | competition-style generated answers | this zero-shot non-chat harness is a poor fit for the formula-restoration SFT and should not be used as the main success metric |
| MMLU | 70.68% | broad 57-subject knowledge | no obvious general-knowledge collapse |
| HumanEval | 71.95% pass@1 | Python code generation | no obvious coding collapse |

The most important preservation checks here are MMLU and HumanEval: despite specializing a 4B model for strict LaTeX output, both remain strong for this model size. The low Hendrycks MATH result is best read as a prompt/harness mismatch for this release, not as a contradiction of the task-specific LaTeX math result.

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

These figures are context, not a single leaderboard: benchmark variants, prompts, chat templates, and harnesses differ. OpenAI describes GPT-4o as matching GPT-4 Turbo-level text and coding performance, while the Qwen model card reports stronger official scores on newer variants such as MMLU-Pro and MMLU-Redux. Our release should be judged primarily by its local LaTeX restoration task, then by preservation checks.

| Model / source | Reported or measured signal | Notes |
| --- | --- | --- |
| Qwen3-4B LaTeX Correction LoRA v3 | 98.97% math accuracy on local clean LaTeX eval; 70.68% MMLU; 71.95% HumanEval | This repository's measured release numbers |
| DeepSeek V4 Pro API baseline | 69.86% math accuracy on the same local LaTeX eval | Strong general model, but weaker canonical-format adherence on this task |
| [Qwen/Qwen3-4B-Instruct-2507 official card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) | MMLU-Pro 69.6, MMLU-Redux 84.2, MultiPL-E 76.8 | Different benchmark variants from our `lm-eval` full run |
| [GPT-4o official positioning](https://openai.com/index/hello-gpt-4o/) | GPT-4 Turbo-level text and code performance | Frontier context only; not rerun in this repository's harness |

Full local artifacts from the remote run are kept outside Git under `benchmark_artifacts/remote-20260704/`.

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
