# Noisy v4_300 Review Sync

这份文档用于让其他 LLM 或审稿人快速对齐当前 `noisy_v4_300` 的项目状态。

目标不是重新设计整个项目，而是帮助外部 reviewer 在理解现有架构与迭代历史的前提下，准确审查当前 `noisy` 验证集是否已经达到扩量门槛。

---

## 1. Project Goal

项目正在构建一个面向简体中文用户的 LaTeX 公式自动纠错 SFT 数据集。

整体数据集规划分为三层：

1. `clean`
- 高质量、自然、清晰的用户输入

2. `noisy`
- 模拟真实世界中不规范但仍可恢复的用户输入

3. `hard`
- 更复杂、更长尾、更高难度的输入

当前重点在 `noisy` 层。

---

## 2. Current Architecture

当前架构已经稳定为：

1. [mine_sympy.py](D:\1\mine_sympy.py)
- 生成标准公式底座
- 输出 `standard_latex`
- 输出 `sympy_expr`

2. [data_builder.py](D:\1\data_builder.py)
- 生成 `clean` 风格训练数据
- 使用 Gemini 生成用户输入风格
- 始终保留标准 LaTeX 作为 `output`

3. [noisy_builder.py](D:\1\noisy_builder.py)
- 从 `clean` 基线派生规则驱动的 `noisy` 数据

4. 本地 Ollama
- 当前不负责数据生成
- 只保留作未来 SFT 后本地评测

---

## 3. Clean Layer Status

当前 `clean` 基线：

- [train_clean_v1_120.jsonl](D:\1\train_clean_v1_120.jsonl)

状态：

- 已可用
- 作为当前 noisy 生成的上游基线

---

## 4. Noisy Layer Evolution

### `noisy_v1`

- [train_noisy_v1_100.jsonl](D:\1\train_noisy_v1_100.jsonl)

问题：

- 自然语言与 ASCII 机械拼接
- 模板感明显
- 可恢复性不稳定

### `noisy_v2`

- [train_noisy_v2_100.jsonl](D:\1\train_noisy_v2_100.jsonl)

改进：

- 修掉了主要的 Frankenstein 拼接问题

外部审稿结论：

- 可以小幅修正后扩量

### `noisy_v3`

- [train_noisy_v3_100.jsonl](D:\1\train_noisy_v3_100.jsonl)

改进：

- 收紧歧义 shorthand
- 打散前缀模板
- 加入轻量 typo 噪声

暴露的问题：

- 出现 `mathcal`、`frac`、`beginbmatrix` 一类 LaTeX 残片

后续纠偏结论：

- 这主要应被理解为 `over-corruption`
- 本质是规则层质量控制问题
- 不应简单粗暴定义成 implementation bug

### `noisy_v4`

当前最新生成器：

- [noisy_builder.py](D:\1\noisy_builder.py)

核心升级：

1. 重写公式降维逻辑
- 不再机械地把 LaTeX 命令扒成字母残片

2. 增加 surface 清洗层
- 清理 `mathcal`、`frac`、`beginbmatrix` 一类残留

3. 增加 post-filter / repair
- 对明显低质量 noisy 做兜底修复

4. 对复杂公式降低纯规则破坏强度
- 避免复杂表达再次被炸成乱码

---

## 5. Current Review Target

当前重点审查文件：

- [train_noisy_v4_300.jsonl](D:\1\train_noisy_v4_300.jsonl)

这是基于当前 [noisy_builder.py](D:\1\noisy_builder.py) 生成的 `300` 条 noisy 验证集。

---

## 6. Current Dataset Snapshot

### Record count

- 总数：`300`

### Structure check

每条记录都包含：

- `instruction`
- `input`
- `output`
- `metadata`

### Category distribution

- `stats_ml`: `89`
- `calculus`: `73`
- `physics`: `47`
- `algebra_trig`: `48`
- `matrix`: `43`

### Noise rule distribution

- `ascii_substitute`: `49`
- `mixed_language`: `46`
- `partial_formula_reference`: `41`
- `operator_confusion`: `41`
- `keyword_shorthand`: `34`
- `subscript_loss`: `33`
- `broken_brackets`: `32`
- `code_fragment_noise`: `14`
- `hat_bar_prime_loss`: `10`

---

## 7. What Has Already Been Fixed

相较于前几轮版本，当前 `v4_300` 已经明显解决了以下关键问题：

1. `mathcal / frac / beginbmatrix / endbmatrix` 残片堆砌
- 这类 `over-corruption` 样本已经不再是当前主问题

2. 极端机械拼接
- 当前样本整体上更接近真实用户输入

3. 高歧义 shorthand 的部分灾难样本
- 可恢复性底线已经基本守住

---

## 8. What Still Needs Attention

当前版本剩余问题不再是 blocker，而更像局部 polish：

1. 少量尾部变量堆砌
- 例如类似 `ygamma` 或变量片段尾随
- 数量已经很少，但仍需关注

2. 少量 rule 味仍偏强
- 主要可能出现在 `mixed_language` / `ascii_substitute` / `partial_formula_reference`

3. 个别 shorthand 或 partial reference 可能仍偏短
- 需要继续确认它们是否足够可恢复

---

## 9. Historical Target Ratios

### Dataset-layer ratio

整体目标比例：

- `clean`: `50%`
- `noisy`: `30%`
- `hard`: `20%`

### Domain ratio

领域配比目标：

- `stats_ml`: `30%`
- `calculus`: `25%`
- `physics`: `15%`
- `matrix`: `15%`
- `algebra_trig`: `15%`

当前 `noisy_v4_300` 不是要求严格精确命中这些比例，而是要求总体上不明显跑偏。

---

## 10. Reviewer Task Boundary

请外部 reviewer 注意：

- 不要脱离现有架构另起炉灶
- 不要重复指出 `v3` 已经修掉的问题
- 不要把受控破坏与代码 bug 混为一谈
- 请重点判断：
  - `v4_300` 是否已达到更大 noisy 验证集的扩量门槛
  - 当前剩余问题是否只是局部 polish

---

## 11. Recommended Review Focus

建议外部 reviewer 重点回答：

1. `noisy_v4_300` 是否已经越过质量门槛
2. 当前剩余问题是 blocker 还是 polish item
3. 哪些 `noise_rule` 已经足够稳定
4. 哪些 `noise_rule` 仍最值得继续盯
5. 是否可以直接扩成更大的 noisy 验证集

---

## 12. Bottom Line

当前 `noisy_v4_300` 的状态可以概括为：

> 它已经是一个成熟的 noisy 验证集底座，主要问题从系统性质量风险收缩为了少量局部瑕疵；当前最重要的判断，不再是“要不要推翻重做”，而是“是否已经足够进入更大规模扩量阶段”。

