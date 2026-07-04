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

## General Capability Preservation

The SFT run was also checked with external `lm-eval` benchmarks to ensure the LaTeX specialization did not cause broad capability regression. The full run below uses the merged BF16 SFT v3 model, evaluated on an RTX 3090 with `lm-eval` after smoke-testing both the base and SFT models.

| Benchmark | SFT v3 result | reference base score | preservation result |
| --- | ---: | ---: | --- |
| GSM8K | 81.35% flexible / 68.16% strict | not rerun full | math reasoning preserved in smoke and full SFT run |
| MATH / Hendrycks | 0.06% | not rerun full | task format is much stricter than the LaTeX SFT target |
| MMLU | 70.68% | ~66.5% official/reference | no regression; higher than reference |
| HumanEval | 71.95% pass@1 | ~68.9% official/reference | no regression; higher than reference |

The two most important regression checks for this release are MMLU and HumanEval. They cover broad factual knowledge and code-generation ability respectively, and both remained above the reference base scores after LoRA fine-tuning. Full local artifacts from the remote run are kept outside Git under `benchmark_artifacts/remote-20260704/`.

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
