# Qwen LaTeX SFT Lab

面向 **LaTeX 公式修复、数据质量和可复核 SFT 实验**的研究仓库。Python 工具链负责数据、训练和评测；轻量 npm CLI 通过用户自己的 Ollama 使用模型。原 Windows/Tkinter 桌面已[归档](archive/desktop/README.md)。

## 最新发现：v5.2 checkpoint-30

| 同协议比较 | 基座 Qwen3-4B-Instruct-2507 | v5.2 checkpoint-30 |
|---|---:|---:|
| 公式修复开发集，56 条 | 33/56，58.93% | **48/56，85.71%** |
| 公式组平均 | 77.22% | **92.12%** |
| 输出协议合规 | 96.43% | 98.21% |
| GSM8K，200 题，4K 输出 | 90.0% | 89.5% |
| MATH-500，200 题，4K，保守主指标 | 56.5% | 66.0% |
| AIME25，30 题，4K 输出 | 23.33% | 30.0% |
| AIME25，30 题，32K 输出 | 40.0% | 36.67% |

**公式修复开发集收益明确；通用数学结果混合，SFT 长输出重复更多。** 第二个 epoch 的 checkpoint-60 同为 48/56，按冻结的并列规则选择较早的 checkpoint-30。

这些是开发选择与限量诊断结果：开发集只有四个公式组，没有微积分，56 条最终测试记录尚未推理。MATH 主指标包含格式/可验证性改善，其最后 boxed 匹配辅助指标为 84.5% → 87.0%，不能全部解释为推理提升。AIME 32K 触顶为 3 → 9 题，超过 100 次 boxed 重复为 3 → 8 题；跨预算生成存在早期分叉，不能全部归因于更多推理。未发现训练 EOS 漏训或截断证据，尚不能确诊过拟合。MATH 16K 与三题 8K 没有执行。

- [训练与开发选择报告](reports/v5.2-colab-sft-20261023/README.md)
- [通用数学 4K 对比](reports/v52-math-20261023/README.md) · [AIME 32K 与复读诊断](reports/v52-math-long-20261023/README.md)
- [实验索引](reports/README.md) · [历史 v3 文档](docs/history/v3-README.md)

## 使用入口

### 用自己的 Ollama 修复公式

安装 Node.js 22+，准备已运行的 Ollama 和已安装的模型。当前 npm 包尚未发布；从本仓库打包安装：

```bash
cd packages/cli
npm pack
npm install -g ./qwen-latex-cli-0.1.0.tgz
qwen-latex models
qwen-latex correct "x平方加y平方" --model <已安装模型名>
```

CLI 不需要 Python、PyTorch 或模型权重，不会自动下载模型或启动服务。详细参数与 stdin/文件用法见 [CLI 文档](docs/cli.md)。模型输出不是数学正确性的自动证明。

**v5.2 是 HF LoRA adapter，不是现成的 Ollama 模型。** 已有 v3 GGUF 属于历史发布，不能用来声称复现上表 v5.2 的结果。v5.2 权重与报告保存在 [HF 私有归档](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v5-2/tree/3721b25f40f3e9383d99b2991ba9dd0e4749dc86)，需要相应账号访问。Ollama 用户显式选择自己的模型；本轮没有转换新 GGUF。

### 研究与复现

```bash
python3 -m venv .venv
# Linux/macOS；Windows 使用 .venv\Scripts\activate
source .venv/bin/activate
pip install -e '.[dev]'
latex-sft --help
python -m unittest discover -s tests -v
```

CPU 数据检查与保存预测评分无需训练/GPU 依赖。正式训练继续使用 LLaMA-Factory，外部评测使用 `lm_eval`；按 [研究指南](docs/research.md) 准备各自环境。数据主版本为 reviewed v5.2：476 train / 56 dev / 56 test。

## 架构与边界

- [架构与历史协议迁移](docs/architecture.md)
- [v5 分组隔离与审查协议](training/DATA_V5.md)
- [Future](docs/future.md)：npm 正式发布、v5.2 Ollama 发布物与可选托管服务。

当前没有托管服务，不提供通用数学能力提升保证；历史 v3 的高分存在标签、泄漏和评分协议问题，保留用于审计。
