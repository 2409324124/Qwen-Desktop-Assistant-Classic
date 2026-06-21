# Qwen-Desktop-Assistant-Classic

A lightweight local desktop assistant that bridges **Ollama** and a classic Windows-style workflow. The app provides global hotkey activation, selected-text capture, and a nostalgic Windows 2000-inspired Tkinter UI.

This repository now also contains the training and evaluation workflow for a Qwen3 4B LaTeX formula-correction SFT model.

## Highlights

- **Global Hotkey** (`Alt + Shift + Q`): summon the assistant from any application.
- **Smart Clipboard Capture**: copy selected text and send it to the local model workflow.
- **Manual Input**: type directly into the prompt box when clipboard capture is not desired.
- **Classic UI**: Tkinter interface styled around a Windows 2000 palette and layout.
- **Local First**: desktop assistant inference runs through a local Ollama endpoint by default.
- **LaTeX SFT Workflow**: reproducible Qwen3 4B LoRA training, clean evaluation, and release artifacts live under [`training/`](training/README.md).

## LaTeX Correction SFT Release

The current SFT target is formula restoration: converting noisy, colloquial, or pseudocode-like math descriptions into canonical LaTeX formulas.

| item | value |
| --- | --- |
| Base model | `Qwen/Qwen3-4B-Instruct-2507` |
| Fine-tuning method | LoRA, rank 64, alpha 128 |
| Training framework | LLaMA-Factory |
| Evaluation split | `latex_formula_eval_clean`, 292 examples |
| Primary metric | Semantic accuracy via the local LaTeX AST matcher |

### Clean Eval Results

| model | exact accuracy | semantic accuracy | parse coverage |
| --- | ---: | ---: | ---: |
| Base Qwen3-4B-Instruct-2507 | 2.40% | 13.36% | 36.99% |
| Qwen3-4B LaTeX Correction LoRA v3 | 83.22% | 98.97% | 100.00% |

The base model often responds with explanatory text or malformed/truncated LaTeX. The SFT model is trained to return formula-only output in the repository's canonical LaTeX dialect.

### Model Artifacts

The release is split by runtime format:

- Full BF16 merged model: [xu2409324124/qwen3-4b-latex-correction-v3-bf16](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v3-bf16)
  - Use this for Transformers, vLLM-compatible conversion, further fine-tuning, or producing new quantizations.
- GGUF Q4_K_M model: [xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m)
  - Use this for llama.cpp, Ollama, LM Studio, and other GGUF local-inference runtimes.

The older aggregate release remains useful as an audit trail for adapters and reports, but the two repositories above are the clean model download targets.

## Training Workflow

The complete model-training path is documented in [`training/README.md`](training/README.md). It covers:

- canonicalizing and cleaning the formula dataset
- generating the fixed clean evaluation split
- running smoke and full LoRA training with LLaMA-Factory
- running base-model and LoRA inference baselines
- evaluating exact, canonical, symbol-fidelity, semantic, and parse-coverage metrics

## Getting Started

### Prerequisites

1. Install [Ollama](https://ollama.com/).
2. Pull a local Qwen model for the desktop assistant:

```bash
ollama pull qwen2.5:1.5b
```

### Installation

```bash
git clone git@github.com:2409324124/Qwen-Desktop-Assistant-Classic.git
cd Qwen-Desktop-Assistant-Classic
conda create -n qwen-assistant python=3.10
conda activate qwen-assistant
pip install httpx pyperclip pynput
```

### Usage

```bash
python main.py
```

The window starts hidden. Select text in another application, press `Alt + Shift + Q`, and the assistant will open with the captured context.

## Components

- `main.py`: Tkinter UI and hotkey listener.
- `ollama_client.py`: async Ollama API client for streaming responses.
- `summon.py`: helper script for hotkey troubleshooting.
- `training/`: dataset preparation, LoRA configs, inference, and evaluation utilities for the LaTeX SFT workflow.

## License

MIT License. Feel free to modify and adapt.
