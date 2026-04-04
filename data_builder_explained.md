# `data_builder.py` 阅读说明

这份说明文档对应的是当前最新版的 [data_builder.py](D:\1\data_builder.py)。

和上一版最大的区别是：

- 它已经不再直接调用 Ollama
- 它也不再内置具体模型的 system prompt
- 它现在是一个“模型无关的数据管道层”

换句话说，当前架构是：

```text
mine_sympy.py -> 标准公式数据
Gemini API -> 三种视角表达
data_builder.py -> 校验 / 展平 / 保存训练数据
Ollama -> 等 SFT 完成后再做本地验收测试
```

---

## 1. 这个脚本现在负责什么

它现在只负责数据管道，不负责模型策略。

它的职责有 5 件事：

1. 读取标准公式数据
2. 调用外部生成器接口
3. 检查生成器返回的数据格式是否合格
4. 把三种视角展开成三条 SFT 样本
5. 保存成 JSONL

它不再负责：

- 写 system prompt
- 调 Ollama
- 规定具体模型怎么生成

这些现在都应该由 Gemini 那一层负责。

---

## 2. 当前的核心抽象：`PerspectiveGenerator`

这是整个重构后的关键。

```python
class PerspectiveGenerator(ABC):
    @abstractmethod
    async def generate(self, formula: dict[str, Any]) -> dict[str, str]:
        ...
```

你可以把它理解成一个统一协议：

- 输入：一条公式字典
- 输出：三种视角表达

只要任何外部生成器满足这个协议，`data_builder.py` 就能直接接。

要求返回格式固定为：

```python
{
    "beginner": "...",
    "programmer": "...",
    "researcher": "..."
}
```

这就是现在的数据契约。

---

## 3. `GeminiGeneratorStub` 是什么

当前文件里有一个：

```python
class GeminiGeneratorStub(PerspectiveGenerator):
```

它不是正式实现，而是一个接口占位。

你后面真正接 Gemini API 的时候，只需要补这个类：

1. `__init__()` 里接收 `api_key / model / endpoint`
2. `generate()` 里调用 Gemini
3. 返回三种视角表达的 dict

也就是说，以后你主要动这个类，而不是再去重写整个数据管道。

---

## 4. `AsyncFormulaDatasetBuilder` 现在是什么角色

它现在不再是“模型请求器”，而是“数据编排器”。

你可以把它理解成：

```text
源公式数据 + 外部生成器 -> 训练样本
```

它内部主要做这些事情：

### `load_source()`

负责读取上游公式 JSON。

会检查：

- 文件是否存在
- 顶层是不是 list
- 每条数据是否有 `standard_latex`

---

### `validate_generated_payload()`

这是新架构里最重要的一层校验。

因为你以后换成 Gemini 后，模型返回内容可能还是会漂。

所以这里规定：

- 必须是 dict
- 必须同时存在 `beginner`
- 必须同时存在 `programmer`
- 必须同时存在 `researcher`
- 每个字段都必须是非空字符串

如果不满足，就直接判定为坏数据。

这一步的意义是：

- 生成逻辑可以灵活
- 但最终数据契约必须稳定

---

### `_request_formula()`

负责处理单条公式。

它的逻辑很简单：

1. 进入 `Semaphore`
2. 调用 `generator.generate(formula)`
3. 校验返回结果
4. 成功则展平
5. 失败则重试
6. 最终失败则跳过当前公式

这里的 `Semaphore` 仍然保留，因为即使以后换成 Gemini，也不代表可以无限并发。

原因包括：

- API 限速
- 本地网络抖动
- 成本控制
- 批处理稳定性

所以这个限流层仍然有价值。

---

### `flatten_records()`

这是训练格式转换层。

外部生成器返回的是：

```python
{
    "beginner": "...",
    "programmer": "...",
    "researcher": "..."
}
```

但训练时更适合写成 3 条独立记录：

```python
{
    "instruction": "...",
    "input": "...",
    "output": "...",
    "metadata": {...}
}
```

所以这里会把一条公式拆成三条样本。

---

### `build()`

负责整批并发调度。

流程是：

1. 为每条公式创建任务
2. 用 `asyncio.gather()` 并发执行
3. 拍平成一维列表
4. 打乱顺序

---

### `save_records()`

负责保存成 JSONL。

每行一条训练样本，方便后续训练和排查。

---

## 5. CLI 参数怎么理解

当前命令行参数里最重要的是这些：

```bash
python data_builder.py \
  --src formulas.json \
  --out train.jsonl \
  --concurrency 3 \
  --retries 2 \
  --limit 10 \
  --gemini-api-key YOUR_KEY \
  --gemini-model gemini-2.5-pro \
  --gemini-endpoint YOUR_ENDPOINT
```

注意：

- 这些 Gemini 参数现在只是留口，不代表已经接通真实 API
- 真正的 API 调用逻辑还要写进 `GeminiGeneratorStub.generate()`

---

## 6. 你以后最该改哪里

如果你准备正式接 Gemini，主要改这一个位置：

[data_builder.py](D:\1\data_builder.py)

具体是：

- `GeminiGeneratorStub.__init__()`
- `GeminiGeneratorStub.generate()`

只要这里返回格式正确，其它地方基本都不用动。

---

## 7. 为什么这版更符合你当前目标

因为你现在的真实分工是：

- `mine_sympy.py` 负责“标准公式底座”
- Gemini 负责“高质量表达生成”
- `data_builder.py` 负责“数据管道”
- Ollama 负责“SFT 后验收测试”

所以 `data_builder.py` 不应该再把 prompt 和具体模型策略写死。

这版的价值就在于：

- 把模型调用从数据管道里剥离出去
- 让 Gemini 接入变成局部修改
- 保持训练数据输出契约稳定

---

## 8. 一句话总结

当前版 `data_builder.py` 已经从“基于 Ollama 的生成脚本”重构成了“面向 Gemini 接入的数据管道骨架”。

它现在最重要的能力不是生成，而是：

- 限流
- 重试
- 校验
- 展平
- 保存

如果你要，我下一步可以继续直接把 `GeminiGeneratorStub` 补成真正可调用 Gemini API 的版本。

