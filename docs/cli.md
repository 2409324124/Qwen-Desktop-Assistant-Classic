# Ollama CLI

`qwen-latex-cli` 提供 `qwen-latex` 命令，Node.js 22+，不依赖 Python 或 GPU 库。包尚未公开发布；从 `packages/cli` 执行 `npm pack`，再用 `npm install -g ./qwen-latex-cli-0.1.0.tgz` 安装。正式 npm 发布属于后续工作。

## 调用

```bash
qwen-latex models
qwen-latex correct "x平方加y平方" --model my-formula-model
qwen-latex correct --file input.txt --model my-formula-model
cat input.txt | qwen-latex correct --model my-formula-model
qwen-latex correct "x+y" --model my-formula-model --max-tokens 256 --json
```

文本参数、UTF-8 文件和 stdin 三选一。整个文件或 stdin 内容作为一次请求，不按行拆分成批量任务。stdout 只包含结果，诊断写 stderr；`--json` 返回文本、模型、结束原因及服务端提供的 usage。模型生成结果不等于已经通过数学保真验证。

| 配置 | 默认 / 来源 |
|---|---|
| Ollama 兼容地址 | `http://localhost:11434/v1`；`--base-url` 覆盖 `QWEN_LATEX_BASE_URL` |
| 模型 | 必填；`--model` 覆盖 `QWEN_LATEX_MODEL` |
| 输出预算 | 256 tokens；`--max-tokens` 设置正整数 |
| 超时 | 120000 毫秒；`--timeout-ms` 设置正整数 |

CLI 使用 Ollama 的 `/v1/chat/completions` 与 `/v1/models`，不下载模型，不启动 Ollama，不自动重试生成。Ctrl+C 中断当前 HTTP 请求。HTTP/连接/超时错误返回非零退出码；服务端报告 length 截断时也返回非零退出码并提示结果不完整。非流式输出避免将中途响应误认为完整结果。

CLI 使用与 Python 研究代码同源的公式修复提示词；没有复制 Python AST 评分器到 JavaScript，也不根据公式名称替换成另一个公式。

## 模型版本

用户必须指定 Ollama 中实际存在的模型。v5.2 checkpoint-30 目前以 HF LoRA 保存，不能把其仓库名直接当作已安装的 Ollama 模型名。旧 v3 GGUF 是不同模型，其历史评分不能代表 v5.2。新 GGUF 转换/发布和我们的托管服务均留待后续。

Ollama 接口说明：https://docs.ollama.com/api/openai-compatibility
