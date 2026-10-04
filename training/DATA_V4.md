# v4 管线与历史离线复评（2026-10-05）

> 分组结论已被 [v5 结构与近亲审计](DATA_V5.md) 修正：此文的零重叠只覆盖 v4 已登记的名称、来源和文本键，不能证明相似公式没有跨集合。下列数字保留为历史记录。

本轮修复生成、审查、规范化、分组与评分协议，没有启动推理或训练，也没有调整 LoRA 超参数。frozen 原始数据、旧 `training/data/*.jsonl`、targeted 源文件和历史 predictions 保持原样。v4 产物与 reports 按仓库原规则不纳入 Git。

## 数据与追溯

3060 条源记录经过同一审查入口，包括 3000 条 frozen 和 60 条 targeted：

| 处理 | 记录数 |
| --- | ---: |
| 原样保留 | 363 |
| 接受并替换输出 | 381 |
| 隔离待复核 | 2316 |
| 接受总数（去重前） | 744 |
| 移除重复记录 | 14 |
| 最终保留 | 730 |

381 条替换包括 **364 条表面规范化**，并不等于 381 条数学错误。另有 17 条按明确输入恢复；理由包括 14 条 BCE 求和作用域/损失符号修复、3 条索引恢复（理由可以交叠）。

隔离是保守筛查结果，不能声称 2316 条均已证明错误。旧信息破坏规则、无法证明的显式转写、缺失/漂移符号、矛盾输入、损坏控制字符和不完整公式进入人工复核队列。通过记录标为 `rule_checked_not_semantic_proof`，并不表示任意自然语言语义已有形式化证明。完整中文描述不因公式名或中文本身被排除；其中未明确提供的自由符号仍需复核。`source_input` 仅用于溯源和归组，不能用于补全当前输入。

- [dataset_summary.json](data/v4/dataset_summary.json)：数量、原因、源文件/规则代码/导出文件 SHA256。
- [review_manifest.jsonl](data/v4/review_manifest.jsonl)：全部 3060 条逐条决定，原始与修订标签、原因、来源及组标识。
- [latex_formula_quarantine.jsonl](data/v4/latex_formula_quarantine.jsonl)：独立隔离集；本轮没有加入拒答/澄清训练协议。

来源 ID 为相对源路径及真实物理行号；还保存每条原记录内容 SHA256。重复样本保留完整 `source_records`，不丢失其家族、祖先输入与公式 ID。新生成器分配独立符号角色，保留 `formula_id`/`symbol_map`，BCE 显式分组；noisy/hard 的历史规则名称保留，但未来仅加排版与 filler 噪声，停止截断、删下标或算子等不可逆变换。

## 分组切分

按公式家族、共享目标/原标签、来源、祖先输入与 `formula_id` 建连通组；同一组不能跨集合。`input/source_input` 和 `target/original_target` 各使用统一命名空间。规范化保留特殊字体、行列式、算子类型与作用域，缓存的旧 canonical 字段只作历史溯源。

| 集合 | 组数 | 记录数 |
| --- | ---: | ---: |
| train | 44 | 649 |
| development (`eval`) | 5 | 32 |
| test | 5 | 49 |

seed 42，目标是类别内约 80/10/10 **组比例**；家族大小不同，所以记录比例不等于 80/10/10。`eval_clean` 是 development 的兼容别名。targeted 有 35 条在 train、20 条在 test，其余隔离，不再强制加入 train。所有输入、方程、来源、家族、lineage 及跨字段泄漏检查均为零。

这些新切分只供后续训练使用，**不能追溯作为历史 v3 的未见测试集**。现有 v3 配置仍指向历史目录，不会自动开始训练。

## 评分与复评

主指标是完整公式保真验证率：保留自由变量、常量、特殊字体、矩阵/行列式及运算顺序；只允许已声明的 `sum/prod/lim` 局部束缚名合法替换。拒绝变量捕获、额外矛盾公式、叉乘换序/错误结合和类型丢失。复杂绑定或不能证明的等价记为 `unverified`，不自动判对。另报解析覆盖、独立输出协议合规率、旧正确性与格式联合指标，以及 raw/postprocessed 结果。未知 raw 输出不伪造。

已有 Base/v3 各 292 条输出中，共同可靠对齐并通过数据审查的只有 **69 条**；217 条对应隔离样本，6 条来源匹配有歧义。

| 同一 69 条输出 | Base | v3 |
| --- | ---: | ---: |
| 旧宽松评分、原标签（诊断） | 8.70% | 98.55% |
| 保真评分、原标签 | 53.62% | 94.20% |
| 保真评分、修订标签、后处理输出 | 53.62% | 88.41% |
| 保真评分、修订标签、raw 输出 | 53.62% | 85.51% |

该保守子集有选择偏差，不能代表完整 292 条或独立泛化。全 292 条原标签的旧 98.97% 仍可复现；换保真评分为 82.53%，但原标签错误尚在，所以也不能当修复后真实准确率。通过共同子集的标签对照和原标签的评分对照，分别检查标签、模型与评分影响，不能仅按字符串变化计数学错误。

[comparison.md](../reports/offline-v4/comparison.md) 及相邻 JSON/逐条 alignment 保存全部结果。MATH-500 原官方 0/500 保留；已有 raw 日志可靠末框字符串命中 **59/500（11.8% 诊断下界）**，不是新的数学准确率。437 条无法可靠提取（含 15 条框后文字待核验），189 条疑似截断；缺少 finish reason/token count，不能断言实际截断。[math500-sample-audit.jsonl](../reports/offline-v4/math500-sample-audit.jsonl) 保存全部 500 条，便于分别复核。

## 复现与边界

```bash
python3 -m unittest discover -s tests -q
python3 -m training.prepare_dataset
python3 -m training.reevaluate_offline --dataset-dir training/data/v4 --output-dir reports/offline-v4
```

84 项测试通过，包括 BCE、符号碰撞、作用域捕获、中文混合输入、targeted 分组、跨字段泄漏、算子与矩阵类型、矛盾附加式、最终答案抽取。仍需人工复核隔离集、独立中文口述/OOD 集和多 checkpoint 比较；当前不能证明真正训练过拟合或遗忘。LaTeXC / LaTeX-130K 来源仍未核实，未作为主复评依据。

后续评测设计可以参考已核实的 [Speech-to-LaTeX（ICLR 2026）](https://proceedings.iclr.cc/paper_files/paper/2026/hash/aee5298251a418aad89618cf6b5e7ccc-Abstract-Conference.html)、[Synthetic Data Verification（ICLR 2026）](https://proceedings.iclr.cc/paper_files/paper/2026/hash/29806b2e4dcb35e42abed21d43e2b7d8-Abstract-Conference.html)、[Abstract Formulation（EMNLP 2025）](https://aclanthology.org/2025.emnlp-main.723/) 与 [KodCode（ACL 2025 Findings）](https://aclanthology.org/2025.findings-acl.365/)。真实口述分层、外部验证器可靠性、公式关系保真与语义去重是本项目的应用推导；中文测试仍需另建。[OOD forgetting 研究](https://arxiv.org/abs/2509.12235) 仅按预印本引用，不能将其结论直接套用于本 LoRA。
