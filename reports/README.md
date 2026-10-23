# 实验索引

| 实验 | 协议 / 结论 | 原始证据 |
|---|---|---|
| [v5.2 模型发布](v52-release-20261023/README.md) | BF16 / Q4_K_M 转换验证完成，HF 上传中 | 转换配置、命令与校验方法 |
| [v5.2 SFT](v5.2-colab-sft-20261023/README.md) | 476 train；56 dev；cp30/cp60 均 48/56，选择 cp30；56 test 未推理 | development 中逐题预测、指标、配置与 HF 归档收据 |
| [通用数学 4K](v52-math-20261023/README.md) | GSM8K 200、MATH-500 200、AIME25 30，同基座/SFT 对比 | results、tasks、comparison.json、原执行命令 |
| [AIME25 32K](v52-math-long-20261023/README.md) | 基座 12/30、SFT 11/30；SFT 重复更多 | results、comparison.json、budget-comparison.json、输出摘录 |
| [旧预测修订评分](v5-offline-reviewed/report.md) | 使用审查后的标签与评分器重评历史预测 | 原预测引用与 changed_judgments |
| [历史 v4 审计](../training/DATA_V4.md) | 标签、泄漏与评分问题的审计协议 | 旧实验不视为独立 v5 泛化证据 |

4K/32K 报告与 JSONL 从已完成运行目录原样导入，`import-manifest.json` 记录来源和文件校验值。运行脚本是历史执行证据，含当时的远端路径，不是当前机器直接可运行的部署脚本。

32K 目录中的历史 run.sh 包含计划中的 MATH 两轮，但实际只完成 AIME 两轮；MATH 16K 和三题 8K 均未执行。最终 test 没有新增推理。仓库不包含模型权重、运行临时文件或认证凭据。
