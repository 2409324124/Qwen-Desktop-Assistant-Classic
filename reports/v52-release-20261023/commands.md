# v5.2 checkpoint-30 model release commands

Host: `home-ms03`. Working directory: `/mnt/RC10/qwen-latex/releases/v52-20261023`.
All merge/conversion/validation ran on CPU. No training, benchmark, Colab, or inference service was started.

```bash
hf repos tag create xu2409324124/qwen3-4b-latex-correction-v3-bf16 v3-archive-20261023 --revision 455d0a161457f4e95efa8ff7d74addcdcfff32b1
hf repos tag create xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m v3-archive-20261023 --revision 7350f8000b05bee313b95b93ccae45ac3add7383
python -m pip install --target .deps antlr4-python3-runtime==4.9.3
CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 PYTHONPATH="$PWD/.deps" llamafactory-cli export export.yaml
python /mnt/RC10/qwen-latex/llama.cpp/convert_hf_to_gguf.py bf16 --outfile qwen3-4b-latex-correction-v5.2-bf16.gguf --outtype bf16 --model-name Qwen3-4B-LaTeX-Correction-v5.2
/mnt/RC10/qwen-latex/llama.cpp/build/bin/llama-quantize qwen3-4b-latex-correction-v5.2-bf16.gguf gguf/qwen3-4b-latex-correction-v5.2-q4_k_m.gguf Q4_K_M 8
CUDA_VISIBLE_DEVICES="" python validate_merge.py
CUDA_VISIBLE_DEVICES="" /mnt/RC10/qwen-latex/llama.cpp/build/bin/llama-completion -m gguf/qwen3-4b-latex-correction-v5.2-q4_k_m.gguf -ngl 0 -c 512 -n 1 -t 8 -p "x+y=" --no-conversation
CUDA_VISIBLE_DEVICES="" /mnt/RC10/qwen-latex/llama.cpp/build/bin/llama-tokenize -m gguf/qwen3-4b-latex-correction-v5.2-q4_k_m.gguf -p "x平方加y平方" --ids --no-bos --log-disable
hf upload xu2409324124/qwen3-4b-latex-correction-v3-bf16 bf16 . --revision main --commit-message "Release v5.2 checkpoint-30 merged BF16; preserve v3 archive tag"
hf upload xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m gguf . --revision main --delete qwen3-4b-latex-correction-v3-q4_k_m.gguf --commit-message "Release v5.2 checkpoint-30 Q4_K_M GGUF; preserve v3 archive tag"
```

Environment executable prefix: `/mnt/RC10/qwen-latex/miniforge3/envs/latex-sft/bin`.
Local `.deps` avoids changing the shared ANTLR dependency used by lm_eval. Initial LLaMA-Factory launch failed before loading because OmegaConf requires ANTLR 4.9.3; rerun succeeded with the isolated dependency.

Versions: LLaMA-Factory `0b7aaf8f6a624bd89a01a155d4265ec861cbdf38`; llama.cpp `063d9c156e816ae3cf62db01f429a07a099afe97`; Transformers 5.6.0; PEFT 0.18.1; PyTorch 2.11.0+cu128; huggingface_hub 1.18.0.

The first GGUF validation used `llama-cli`, which no longer supports `--no-conversation` and entered an interactive prompt loop. That one process was terminated, its repeated console log reduced to a small diagnostic excerpt, and validation was rerun successfully with `llama-completion`. The one-token completion is a file-load test, not evidence of mathematical correctness or quantized benchmark accuracy.
