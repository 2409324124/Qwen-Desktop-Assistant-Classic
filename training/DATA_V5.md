# v5：按结构与近亲关系隔离

v4 的“零重叠”只适用于当时登记的名称、文本和来源键，不能证明相似公式没有跨集合。v5 保留 v4 数据和历史预测，改用来源、完整结构、参数模板和显式近亲关系的连通组。基础数学符号仍可共享；同组公式整体进入一个集合。

## 规则

[formula_families.json](formula_families.json) 显式覆盖生成器全部 58 个模板：15 个用户指定的近亲组，以及 8 个明确的单模板组。未知家族不自动成为可训练单例。

结构签名从完整保真 AST 生成，对自由变量、函数名及合法局部束缚变量规范化，保留重复关系、类型、运算顺序、矩阵/行列式、修饰符、常量和作用域。另一个模板签名仅抽象乘法中的直接标量系数和直接的非特殊整数幂；保留加法常数、整个分母中的数字、0/1/-1、数学常量、数字下标、上下界和复杂指数内部的数字。下标位置的 `i/e` 作为变量一致改名，其他位置保留常量身份。例如 `2*x` 与 `3*a` 模板相同，`x+2` 与 `a+3` 不同；`x_i` 与 `a_j` 结构相同，但评分仍不接受变量漂移。原始与修订目标使用同一签名空间；两者任一无法生成签名则隔离。

这两种签名只用于保守合组，**不是数学等价证明，也不会放宽评分**。例如 `x+y` 和 `a+b` 同组，评分仍拒绝变量漂移。各签名和近亲边取传递闭包；重复记录保留全部来源和连接关系。`group_connections.jsonl` 保存每次连接的端点、依据和身份，`group_manifest.jsonl` 保存最终组名单。

`\lim_{h\to 0}` 的单变量作用域现在可以验证，37 条导数极限定义获得结构签名。尚未支持的积分绑定继续隔离，不以“可读成若干符号”代替完整作用域解析。

## 本次导出

| 项目 | 数量 |
| --- | ---: |
| 输入源记录 | 3060 |
| 原质量审查通过 | 744 |
| 独立 Symbol Boundary 诊断 | 20 |
| 结构阶段新增隔离 | 67 |
| 通过结构审查（去重前） | 657 |
| 去重后主数据 | 643 |
| 最终完整组 | 19 |

新增隔离的 67 条包括 47 条积分公式和 20 条原始标签含 `\phix` 等粘连命令的记录。后者即使修订标签可解析，原始目标仍无法获得可靠结构签名，因此待复核。合计隔离 2383 条；隔离不等于已经证明每条数学错误。

| 集合 | 组数 | 记录数 |
| --- | ---: | ---: |
| train | 11 | 515 |
| development (`eval`) | 4 | 64 |
| test | 4 | 64 |

当前规则为 `v5-structure-near-2`、`faithful_structure_v2`、`component-allocation-v1`，seed=42。样本比例约 **80.09/9.95/9.95%**。连接关系仍取完整传递闭包，最后分配改为整组精确搜索；不硬编码公式名单，不拆组。依次最小化以下目标，前一项优先于后一项：

1. 三个集合相对目标样本数的绝对偏差之和（本次为 1.2 条，达到最优）。
2. 各集合缺失的类别数（软目标，不要求每类出现在所有集合）。
3. 相对 80/10/10 目标组数的绝对偏差之和。
4. 各类别相对目标样本数的绝对偏差之和。

三路切分组数充足时，开发和测试各至少 3 个组，并保留至少一个训练组；不足时降低最少组数，在汇总中显式报告空集合。合法局部移动只提供初始搜索上界，最终枚举使用可证明的偏差下界剪枝，保留全部可能的最优方案。相同目标值通过 seed 与排序后的组 ID 对应的分配哈希确定选择；seed 不选择更差的目标值。`dataset_summary.json` 记录目标顺序、目标值、最少组数及搜索统计。

| 类别 | train | development | test |
| --- | ---: | ---: | ---: |
| algebra_trig | 73 | 2 | 32 |
| calculus | 166 | 0 | 0 |
| matrix | 83 | 33 | 12 |
| physics | 28 | 5 | 10 |
| stats_ml | 165 | 24 | 10 |

开发集包含二次方程、仿射与激活、平方反比定律、通用矩阵布局；测试集包含高斯公式、电磁场关系、质能关系、复数与三角表示。开发和测试各覆盖 4 类，但类别分布仍不均衡，测试中 44/64 条来自复数与三角组；**两者均没有微积分**。样本比例改善不能消除这些代表性限制。

- 欧拉公式、欧拉恒等式、复数极坐标及旋转矩阵同在测试组。
- 库仑定律和万有引力同在开发组；两种运动学公式同在训练组。
- Fourier/Laplace 已登记同一个近亲组，但当前因积分作用域未验证，均在隔离集。
- 20 条 Symbol Boundary 仅在独立诊断集，不进主训练、开发、测试或主分数。

查看完整[逐组审计](data/v5/group_audit.md)、[连接依据](data/v5/group_connections.jsonl)、[逐条审查](data/v5/review_manifest.jsonl)和[汇总与哈希](data/v5/dataset_summary.json)。导出文件按已有 Git 规则保持忽略。此前 `b0328f2` 的 445/167/31 分配及完整导出保存在本地 `reports/v5-group-audit/b0328f2-before-allocation-fix/`；本次仅修订 v5 规则与导出，v4 和历史预测不变。

## 评测与复现

当前只完成 CPU 计划验证和 mock 子进程测试，没有真实 v5 训练、模型推理或 Colab 验收，不产生新的模型准确率。未来预测 JSONL 保留 `metadata.formula_group_id` 后，评测同时输出：

- `math_accuracy` / `micro_math_accuracy`：按样本平均。
- `macro_math_accuracy`：先算每组准确率，再给每组相同权重。
- `by_formula_group_id`：各组样本数、准确率、独立输出协议合规率和解析覆盖率。
- `grouped_coverage`：分组指标实际覆盖的主样本比例；没有组 ID 时宏平均为 null，不伪造分组。

raw 和后处理结果分别计算。`metadata.evaluation_role=diagnostic` 的行进入独立诊断指标，不改变主分数。测试只有四组且缺少微积分，即使同时报告两种平均也不足以证明广泛泛化。历史 v3 接触过旧来源，v5 不能追溯成为它的未见测试集。

```bash
python3 -B -m unittest discover -s tests -q
python3 -B -m training.prepare_dataset --out-dir training/data/v5 --seed 42
# 后续获得新预测后再评测；保留每条预测的分组 metadata。
python3 -B -m training.evaluate_latex --predictions predictions-v5.jsonl --report reports/v5-eval.md --json reports/v5-eval.json
```

默认准备目录已切到 v5。准备工具会拒绝覆盖已有其他版本或未标版本的数据目录。v4 和旧预测本轮通过 SHA256 核对保持不变；相同输入、规则和 seed 的导出可逐字节复现。旧训练配置继续保留；v5 使用独立的 `qwen3_4b_lora_sft_v5.yaml` 和 `qwen3_4b_lora_smoke_v5.yaml`。

## v5 实验入口与模型选择

统一入口 `training.run_v5_experiment` 默认只校验本地数据/代码/导出哈希并打印计划，不联网或下载模型，只有加 `--execute` 才调用训练或模型推理。没有单独的 `plan` 子命令：

```bash
python3 -B -m training.run_v5_experiment train --profile smoke
python3 -B -m training.run_v5_experiment train --profile sft
python3 -B -m training.run_v5_experiment evaluate --baseline-only
# 仅在正式 SFT 已完成、manifest 和 checkpoint 齐全后可生成比较计划：
python3 -B -m training.run_v5_experiment evaluate --run-dir saves/qwen3-4b-latex-correction/lora/sft-v5
```

正式配置为 SDPA、BF16、3 epochs，逐 epoch 保存与计算开发集 loss，保留全部 3 轮 checkpoint，不按 `eval_loss` 自动加载最佳模型。smoke 为最多 64 个样本、5 个 optimizer steps，写入独立的 `smoke-v5` 根目录。`train --run-dir` 指定实验根，根下保存 `effective_config.yaml` 和 `run_manifest.json`，HF checkpoint 写入 `checkpoints/checkpoint-N`。执行时拒绝覆盖已有根目录，真实训练还要求 CUDA BF16 支持。

基座执行时解析并记录不可变 HF revision，再只读检查对应 revision 的本地全部 safetensors 权重；缓存缺失或不完整时停止并给出准确的 `hf download MODEL --revision SHA` 命令，由用户手动下载，不自动抓取大模型。训练完成时锁定 checkpoint config/weights 和存在的 trainer_state 哈希，评测前重新核对。正式 checkpoint 比较使用训练已锁定的 revision，每次同时重新评测 base 和全部 checkpoint。比较只接受 completed sft，拒绝 smoke、失败或未完成实验，核验数据、协议、配置和 adapter 身份。独立 baseline 的默认结果根为 `reports/v5/base-development`，checkpoint 比较默认 `reports/v5/checkpoint-development`；`evaluate --output` 可改为新的结果根，执行时已有目录拒绝覆盖。

候选模型只在 development 上按 **postprocessed macro math accuracy，再 micro math accuracy** 排序；同分优先 base，再优先较早 checkpoint。base 获胜可以推荐 base，不强行推荐 SFT。输出完整 raw/postprocessed、per-group 指标、预测哈希、环境与数据/配置/adapter/协议哈希；独立 baseline 不进行 checkpoint 选择。入口只核验 test 的成员和隔离信息，不对 test 运行模型或给出成绩。

当前验收不含真实 GPU、模型或 Colab 执行；依赖兼容、显存和实际收益需未来 smoke 与正式训练后再验证。远端大于等于 1 GB 的模型文件由用户手动预取固定 revision 到同一 HF 缓存，避免自动大文件下载；未来执行解析的 revision 必须与缓存一致，见[训练操作说明](README.md#manual-remote-model-prefetch)。新 inference 默认 v5 development；重现旧 v3 命令必须显式传旧 `--eval-file training/data/latex_formula_eval_clean.jsonl`。旧 98.97% 是旧评分器和旧切分的历史成绩，不是 v5 有效结果。
