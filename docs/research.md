# SFT 研究与复现

## CPU 安装和当前数据

在仓库根目录创建独立 Python 环境，再安装 `pip install -e '.[dev]'`。普通验证和保存预测评分不需要 Torch、LLaMA-Factory、vLLM 或桌面依赖。

```bash
latex-sft data verify --data-version v5.2
latex-sft train --data-version v5.2
latex-sft evaluate --data-version v5.2 --baseline-only
```

新入口默认 v5.2；这里仍显式写出版本便于复核。上面的 train/evaluate **只打印计划**，没有 `--execute` 不下载模型、不启动推理或训练。没有自动前置 smoke。旧接口如 `python -m training.run_v5_experiment train` 保留历史 v5 默认，不能与新命令省略版本后的含义混淆。

reviewed v5.2 包含 476 train / 56 dev / 56 test；来源与审核在现有 `training/data/v5.2` 和 `training/reviews` 路径。最终 test 只验证归属和隔离，不参与本次重构的推理或选模。数据规则见 [DATA_V5](../training/DATA_V5.md)。

## 已保存预测的评分

```bash
latex-sft score \
  --predictions reports/v5.2-colab-sft-20261023/development/checkpoint-30/predictions.jsonl \
  --report /tmp/latex-sft-checkpoint30.md \
  --json /tmp/latex-sft-checkpoint30.json
```

该命令只读取预测，不加载模型。原始输出与后处理指标分别报告；未验证不自动判对。原评分快照保留，当前重构不修改评分规则。

## 需要 GPU 时的独立环境

本轮不执行这一节。正式使用时，为 LLaMA-Factory 和 lm_eval/vLLM 分别准备兼容环境，避免不同 Torch/CUDA 依赖互相覆盖。`training`、`inference`、`benchmark` 可选依赖是安装入口，不代表复现旧运行的精确版本锁；准确环境来自各运行报告。

- v5.2 原训练使用 LLaMA-Factory 0.9.5，2 epochs，rank 64 / alpha 128，原始 Qwen3-4B-Instruct-2507 基座，保存两个 epoch 的 adapter。
- 通用数学对比使用 vLLM 0.22.0；每个任务先基座再 checkpoint-30，明确输出预算、样本数、chat template、seed 与答案抽取协议。
- 新运行使用新的输出目录。只有明确执行 `latex-sft train --data-version v5.2 --execute` 才训练；实际后端命令仍为 `llamafactory-cli train <effective_config.yaml>`。
- 完成训练后，`latex-sft evaluate --data-version v5.2 --run-dir <新运行目录> --execute` 比较基座与已完成 checkpoint，仅在 development 选模。
- 外部 benchmark 直接使用 `lm_eval run --model vllm`，复用报告里的任务覆盖和生成设置。历史 run.sh 含当时主机绝对路径，先按自己的缓存与输出目录修改，不直接执行归档脚本。

公式修复的短输出预算和通用数学解题预算分开配置。AIME 32K 已显示循环输出，不能仅靠不断放大上限来获得可靠改善。

## 验证

```bash
python -m unittest discover -s tests -v
cd packages/cli
npm ci --ignore-scripts
npm test
npm pack
```

本轮 CPU 回归必须保持冻结数据、逐题评分、组指标与 cp30 并列选择结果一致；Node 测试使用本地模拟 HTTP 服务。当前真实训练/评测结果见 [实验索引](../reports/README.md)，历史入口和数据审计文档保留供复查。
