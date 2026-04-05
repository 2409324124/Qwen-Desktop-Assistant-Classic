# Tavily 接入说明

这份文档用于说明 Tavily 在当前项目中的定位，以及后续真正把它接进工作流时该怎么用。

---

## 1. 当前定位

Tavily 不是训练数据生成的主模型提供方。

它在当前项目中的定位是：

- 联网检索增强
- 事实核查
- 补充实时网页上下文
- 为后续 agent / LLM 提供更强的搜索结果

也就是说：

- Gemini 负责生成训练数据里的语言输入特征
- Tavily 负责搜索
- Ollama 负责后续本地模型验收

---

## 2. 当前已准备好的文件

- [tavily_client.py](D:\1\tavily_client.py)
- [`.env.example`](D:\1\.env.example)

`tavily_client.py` 当前已经具备：

- 读取 `.env`
- 读取 `TAVILY_API_KEY`
- 调用 Tavily `/search`
- 返回原始 JSON
- 命令行 smoke test 入口

---

## 3. 环境变量

请在本地 [`.env`](D:\1\.env) 中加入：

```env
TAVILY_API_KEY=你的真实key
TAVILY_BASE_URL=https://api.tavily.com
TAVILY_TIMEOUT=60
```

注意：

- `.env` 已被 git 忽略
- 不要把真实 key 写进代码
- 不要把真实 key 提交到仓库

---

## 4. 最小调用方式

命令行 smoke test：

```powershell
D:\1\latex\python.exe tavily_client.py "latest Tavily API search docs"
```

Python 代码调用：

```python
from tavily_client import build_tavily_client

client = build_tavily_client()
result = await client.search(
    "latest Tavily API search docs",
    topic="general",
    search_depth="advanced",
    max_results=5,
    include_answer="advanced",
)
```

---

## 5. 推荐的使用场景

后续我们最可能在这些地方接 Tavily：

1. 数据审查
   - 检查某些公式、术语、缩写是否来自真实网页表达

2. 真实用户输入增强
   - 搜索论文、博客、论坛里的公式口语化写法

3. Agent 外部检索
   - 让后续 agent 在需要联网时优先走 Tavily，而不是依赖默认搜索

4. 训练后验收
   - 对比模型回答和检索事实

---

## 6. 当前没有做的事

这次只完成了“接入前准备”，还没有：

- 把 Tavily 接进 `data_builder.py`
- 把 Tavily 接进自动化工作流
- 使用真实 key 发请求

这样做的好处是：

- 不会误消耗你的额度
- 不会在还没确定使用场景时把检索逻辑耦合进主流程

---

## 7. 下一步建议

真正接入时，建议不要一上来把 Tavily 混进训练主流水线，而是先做成单独的检索辅助层。

推荐顺序：

1. 先完成 `clean/noisy/hard` 数据体系
2. 再把 Tavily 用于数据审查和真实表达补充
3. 最后再决定要不要把 Tavily 变成 agent 的默认检索后端

