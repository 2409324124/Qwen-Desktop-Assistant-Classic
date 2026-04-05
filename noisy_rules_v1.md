# Noisy 规则清单 V1

这份文档用于定义 `noisy` 层训练数据的第一版规则，不直接作为训练数据本身。

它的目标是把我们从 [noise_reference_sample.md](D:\1\noise_reference_sample.md) 和 [noise_reference_sample.json](D:\1\noise_reference_sample.json) 中看到的真实网页噪声，整理成可执行的生成策略。

---

## 1. noisy 层目标

`noisy` 层的目标不是制造“完全错误”的输入，而是模拟真实用户在输入公式时常见的：

- 不规范
- 不完整
- 中英混输
- 键盘化
- 结构残缺
- 术语缩写
- 局部错误

但这些输入仍然应该大体上能让模型恢复到正确公式。

换句话说：

- `clean` 强调清晰和高质量
- `noisy` 强调真实世界鲁棒性

---

## 2. 设计原则

### 原则 1：噪声必须“像真人”

不能为了加噪而加噪。

如果一种变形方式现实里几乎没人这么输，就不应大规模进入 `noisy`。

### 原则 2：仍要可恢复

`noisy` 不是做随机破坏。

它应该让模型“费点劲，但还能恢复”，而不是让人类都看不出来在写什么。

### 原则 3：噪声强度要可控

同一条样本不要同时叠太多种噪声。

建议大多数样本只叠加：

- 1 种主噪声
- 最多 1 种辅噪声

---

## 3. noisy 类型总览

当前建议第一版 noisy 规则包括以下 9 类：

1. `ascii_substitute`
2. `mixed_language`
3. `subscript_loss`
4. `hat_bar_prime_loss`
5. `operator_confusion`
6. `partial_formula_reference`
7. `broken_brackets`
8. `keyword_shorthand`
9. `code_fragment_noise`

---

## 4. 具体规则

### 4.1 `ascii_substitute`

定义：

- 用 plain-text / ASCII 写法替代标准数学排版

常见表现：

- `exp(x)` 代替指数写法
- `sum_j` 代替求和符号
- `int_a^b` 代替积分上下限
- `sqrt(x)` 代替根号
- `theta_hat` 代替 `\hat{\theta}`
- `x^2` / `x**2` 混用

示例：

- `softmax(x_i) = exp(x_i) / sum_j exp(x_j)`
- `f_prime(x) = limit((f(x+h)-f(x))/h, h->0)`

推荐生成方式：

- 规则生成：强
- Gemini 模拟：中

风险：

- 容易过于接近 `programmer clean`

建议占比：

- 高

---

### 4.2 `mixed_language`

定义：

- 中文描述中混入英文术语或公式片段

常见表现：

- `softmax`, `ReLU`, `gradient`, `loss`, `integral`, `matrix`
- 中文句子中夹 plain-text 公式片段

示例：

- `那个 softmax 公式，就是 exp(x_i) over sum_j exp(x_j)`
- `求导定义那个式子，limit h->0 的 difference quotient`

推荐生成方式：

- 规则生成：中
- Gemini 模拟：强

风险：

- 如果比例过高，会把 `noisy` 做成“半英文化数据集”

建议占比：

- 高

---

### 4.3 `subscript_loss`

定义：

- 下标信息丢失、压扁或写成 plain-text 近似

常见表现：

- `x_i` -> `xi`
- `x_1` -> `x1`
- `theta_t-1` -> `theta prev`
- `h_t` -> `h_t` / `ht` / `h current`

示例：

- `sum xi squared from i=1 to n`
- `theta prev - eta grad J(theta prev)`

推荐生成方式：

- 规则生成：强
- Gemini 模拟：中

风险：

- 丢太多会导致结构不可恢复

建议占比：

- 中高

---

### 4.4 `hat_bar_prime_loss`

定义：

- 帽子、横线、撇号等修饰信息丢失或弱化

常见表现：

- `\hat{y}` -> `y_hat` / `pred y` / `y`
- `\bar{x}` -> `x_bar` / `mean x`
- `f'(x)` -> `f prime x` / `derivative of f`

示例：

- `MSE = sum (y - yhat)^2 / N`
- `sample mean x bar = 1/N sum xi`

推荐生成方式：

- 规则生成：强
- Gemini 模拟：中

风险：

- 若完全丢失修饰信息，多个公式之间容易混淆

建议占比：

- 中

---

### 4.5 `operator_confusion`

定义：

- 运算符或关系符使用不规范，但不彻底失真

常见表现：

- `=` 和 `==` 混用
- `*` 显式写乘法
- `/` 取代分式
- `to` / `->` / `from ... to ...` 混写

示例：

- `exp(i*pi) + 1 == 0`
- `F = ke * q1 * q2 / R^2`

推荐生成方式：

- 规则生成：强
- Gemini 模拟：弱

风险：

- 太多 `==` 会把 noisy 做成“程序员数据”

建议占比：

- 中

---

### 4.6 `partial_formula_reference`

定义：

- 只说出公式一部分，但能让人联想到目标公式

常见表现：

- 只提核心结构
- 只说“那个积分从 0 到无穷的”
- 只说“那个 a 平方加 b 平方等于 c 平方”

示例：

- `那个 a平方+b平方=c平方 的公式`
- `就是 exp 除以 sum exp 那个 softmax`

推荐生成方式：

- 规则生成：弱
- Gemini 模拟：强

风险：

- 太短时可能映射到多个候选公式

建议占比：

- 中高

---

### 4.7 `broken_brackets`

定义：

- 括号、花括号、分组结构不完整或被简化

常见表现：

- `f(x+h)-f(x)/h`
- `sigma(Wx+b` 
- `int_a^b f(x dx`

示例：

- `limit h->0 (f(x+h)-f(x)/h`
- `softmax(exp xi / sum exp xj)`

推荐生成方式：

- 规则生成：强
- Gemini 模拟：弱

风险：

- 破坏过头会降低可恢复性

建议占比：

- 中

---

### 4.8 `keyword_shorthand`

定义：

- 用关键词、短语、术语片段替代完整表达

常见表现：

- `Bayes formula`
- `quotient rule`
- `Jacobian 2x2 partial matrix`
- `MSE loss`

示例：

- `Bayes formula P(A|B)`
- `Jacobian 2x2 partials`

推荐生成方式：

- 规则生成：中
- Gemini 模拟：强

风险：

- 过短时可能丢失目标唯一性

建议占比：

- 中高

---

### 4.9 `code_fragment_noise`

定义：

- 把公式写成不完整代码、伪函数、注释风格片段

常见表现：

- `relu = max(0,x)`
- `theta_next = theta_prev - lr * grad`
- `if x>0 return x else 0`

示例：

- `GD update: theta_t = theta_prev - lr * gradJ`
- `relu(x): max(0,x)`

推荐生成方式：

- 规则生成：中
- Gemini 模拟：中

风险：

- 容易过度偏程序员群体

建议占比：

- 中

---

## 5. 生成策略建议

第一版 `noisy` 不建议完全靠单一手段生成。

推荐混合策略：

- 40% 规则生成
- 40% Gemini 模拟
- 20% 规则 + Gemini 叠加

### 为什么这样分

- 规则生成适合可控、低风险的结构噪声
- Gemini 模拟适合真实人类表达噪声
- 两者叠加可以制造更自然但仍可控的复杂 noisy 样本

---

## 6. 规则与生成方式映射

更适合规则生成的：

- `ascii_substitute`
- `subscript_loss`
- `hat_bar_prime_loss`
- `operator_confusion`
- `broken_brackets`

更适合 Gemini 模拟的：

- `mixed_language`
- `partial_formula_reference`
- `keyword_shorthand`

两边都可用的：

- `code_fragment_noise`

---

## 7. 第一版 noisy 层推荐配比

在 `noisy` 层内部，建议先用以下粗粒度分配：

- `ascii_substitute`: 20%
- `mixed_language`: 15%
- `subscript_loss`: 10%
- `hat_bar_prime_loss`: 10%
- `operator_confusion`: 10%
- `partial_formula_reference`: 10%
- `broken_brackets`: 10%
- `keyword_shorthand`: 10%
- `code_fragment_noise`: 5%

这不是最终真理，但足够作为 V1 启动配方。

---

## 8. 当前不建议大规模使用的噪声

以下噪声先不要大量加入：

- 完全错误的变量替换
- 多个关键运算同时破坏
- 把公式变成几乎不可辨认的残片
- 纯随机字符噪声
- 过于口水化、完全不含结构信息的自然语言

这些更适合后面单独作为 `hard` 或错误诊断集的一部分，而不是 `noisy v1`。

---

## 9. 下一步建议

基于这份规则清单，后续建议按这个顺序推进：

1. 做 `noisy` 小样本原型
   - 先生成 50 到 100 条

2. 人工审查
   - 看 noisy 是否“像真人”而不是“像脚本”

3. 再扩到正式 `noisy` 验证集
   - 例如 900 条

---

## 10. 一句话总结

`noisy v1` 的核心不是“把输入弄乱”，而是“模拟真实世界中用户会怎么不规范地表达公式，同时仍然让模型有机会恢复正确 LaTeX”。 

