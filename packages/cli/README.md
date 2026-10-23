# qwen-latex-cli

A lightweight client for an existing Ollama instance. Node.js 22 or newer is required; Python and GPU packages are not required by the CLI. The user manages the server and model installation.

This package is not yet published to npm. From this repository:

```sh
cd packages/cli
npm pack
npm install -g ./qwen-latex-cli-0.1.0.tgz
qwen-latex models
qwen-latex correct "x平方加y平方" --model YOUR_INSTALLED_MODEL
qwen-latex correct --file input.txt --model YOUR_INSTALLED_MODEL
cat input.txt | qwen-latex correct --model YOUR_INSTALLED_MODEL
```

Pass exactly one input source. File and stdin input must be UTF-8, and each is sent as a single request. Quote positional text containing spaces. Use `--` before text beginning with `--`.

| Setting | Flag | Environment | Default |
| --- | --- | --- | --- |
| Model | `--model` | `QWEN_LATEX_MODEL` | Required for `correct` |
| Ollama OpenAI-compatible base URL | `--base-url` | `QWEN_LATEX_BASE_URL` | `http://localhost:11434/v1` |
| Output token budget | `--max-tokens` | — | 256 |
| HTTP timeout in milliseconds | `--timeout-ms` | — | 120000 |

Flags take precedence over environment values. `models` uses `/v1/models`; `correct` uses `/v1/chat/completions`, non-streaming, temperature 0. No downloads, server startup, automatic retries, or mathematical verification are performed. Do not send private input to an endpoint you do not trust. Hosted inference is a future feature.

Normal stdout contains only the model text (or one installed model ID per line); diagnostics go to stderr. `correct --json` emits `{ "text", "model", "finish_reason", "usage" }`, with `usage` only when returned by the endpoint. `models --json` emits the model-list response. Exit codes: 0 success, 1 input/network/response error, 2 truncated or otherwise incomplete completion, 130 interrupted request. A truncated response is retained in stdout, with `finish_reason: "length"` in JSON and a warning on stderr.

The v5.2 Hugging Face checkpoint is a LoRA adapter, not an automatically installable Ollama model. Historical v3 Ollama/GGUF releases are a different model. Select a model already available on your server; this client does not convert or merge weights.

## Development

```sh
npm test
npm pack
```

The build copies `src/latex_sft/core/resources/latex-correction.txt` into package assets and verifies byte identity. Do not edit the generated asset. Tests use a local mock HTTP server and need no GPU or Ollama process. The tarball contains only the runtime, prompt asset, package metadata and this guide. Public npm publication is a separate step after confirming name availability, account and licensing.
