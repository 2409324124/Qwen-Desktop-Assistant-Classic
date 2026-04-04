import argparse
import asyncio
import json
import os
import random
from abc import ABC, abstractmethod
from typing import Any, Optional

import aiohttp


DEFAULT_INSTRUCTION = "请将以下含糊、口语化或程序化描述还原为标准的 LaTeX 公式。"
DEFAULT_GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"

# Gemini 结构化输出 schema。
# 我们直接把输出格式钉死成 3 个字符串字段，便于后续稳定 flatten。
PERSPECTIVE_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "beginner": {
            "type": "string",
            "description": "纯口语化描述（小白视角），只能用通俗自然语言描述公式形态。",
        },
        "programmer": {
            "type": "string",
            "description": "键盘伪代码（程序员视角），使用纯键盘字符、缩写或类代码逻辑表达。",
        },
        "researcher": {
            "type": "string",
            "description": "中英夹杂的含糊拼写（真实科研场景），允许术语缩写、中英文混合和局部省略。",
        },
    },
    "required": ["beginner", "programmer", "researcher"],
    "additionalProperties": False,
}


def load_local_env(env_path: str = ".env") -> None:
    # 轻量级 .env 读取器，避免为了加载 API key 额外引入 python-dotenv。
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


class PerspectiveGenerator(ABC):
    # 外部生成器统一接口。
    # 任何模型提供方只要实现 generate(formula) -> 三视角 dict，
    # data_builder 的其余部分就可以保持不变。
    @abstractmethod
    async def generate(self, formula: dict[str, Any]) -> dict[str, str]:
        raise NotImplementedError


class GeminiGenerator(PerspectiveGenerator):
    # 真实 Gemini REST 适配器。
    #
    # 这里把“怎么请求 Gemini”封装起来，
    # 让数据管道层只关心标准输入和标准输出。
    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_GEMINI_MODEL,
        endpoint: str = DEFAULT_GEMINI_ENDPOINT,
        timeout: int = 90,
    ) -> None:
        if not api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY in .env or env vars.")

        self.api_key = api_key
        self.model = self._normalize_model_name(model)
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout

    @staticmethod
    def _normalize_model_name(model: str) -> str:
        # 兼容两种写法：
        # 1. gemini-2.5-flash
        # 2. models/gemini-2.5-flash
        return model.split("/", 1)[1] if model.startswith("models/") else model

    def _build_prompt(self, formula: dict[str, Any]) -> str:
        # 这里保留 provider-specific prompt。
        # 当前先采用中文主提示词，后续如果要做中英双语扩展，继续在这里演进即可。
        return (
            "# [角色设定]\n"
            "你是一位资深的大语言模型（LLM）数据合成专家与提示词工程师。"
            "你深谙如何为 SFT（监督微调）和 LoRA 训练构建高质量、多样化的指令微调数据集。"
            "你极其擅长角色扮演与用户意图逆向工程，能够精准模拟不同知识背景"
            "（从零基础小白到资深科研人员）的用户在使用大模型处理数学、深度学习或工程公式时的真实输入习惯。\n\n"
            "# [背景上下文]\n"
            "在真实的科研与工程场景中，用户输入复杂数学公式或特定领域术语时，往往不会使用标准且完美的 LaTeX 语法。"
            "为了提升大语言模型对人类泛化输入，尤其是具有高度长尾特征的口语化、伪代码化、中英夹杂输入的理解与泛化能力，"
            "我们需要批量合成多样化的用户指令特征。当前需要针对给定的标准公式或学术表达式，"
            "生成三种不同认知颗粒度的自然语言描述，以模拟真实世界的复杂 Prompt 场景。\n\n"
            "# [核心任务]\n"
            "你的核心任务是接收输入的标准公式，并将其准确降维、拆解并重构为以下三种特定视角的输入特征：\n"
            "1. 纯口语化描述（小白视角）：完全不使用任何专业数学符号或编程术语，用最基础、最通俗的日常语言描述公式的视觉形态。\n"
            "2. 键盘伪代码（程序员视角）：模拟软件工程师在不方便输入公式时，习惯使用的纯键盘字符、缩写或类代码逻辑表达。\n"
            "3. 中英夹杂的含糊拼写（真实科研场景）：模拟科研人员在组会记录、快速推导或编写草稿时，极具特征的中英文混用、术语缩写及部分结构省略的表达。\n\n"
            "# [边界与约束]\n"
            "1. 严禁过度解释：仅翻译和模拟输入的形态，绝对不能对目标公式进行数学求解、化简或解释其物理/工程意义。\n"
            "2. 严禁偏离设定：三种视角的颗粒度必须泾渭分明，不能在小白视角中出现编程缩写，也不能在程序员视角中出现过多中文口语连接词。\n"
            "3. 严禁捏造数据：必须 100% 忠实于目标公式本身的变量和结构，绝对不能脑补原公式中不存在的参数、常数或条件限制。\n"
            "4. 格式硬约束：最终只返回结构化 JSON，对应字段为 beginner、programmer、researcher；禁止输出任何额外说明。\n\n"
            "# [目标公式元数据]\n"
            f"- name: {formula.get('name', 'unknown')}\n"
            f"- category: {formula.get('category', 'unknown')}\n"
            f"- target_formula: {formula['standard_latex']}\n"
            f"- sympy_expr: {formula.get('sympy_expr')}\n\n"
            "# [字段语义映射]\n"
            "- beginner 对应：纯口语化描述（小白视角）\n"
            "- programmer 对应：键盘伪代码（程序员视角）\n"
            "- researcher 对应：中英夹杂的含糊拼写（真实科研场景）\n"
        )

    def _build_request_payload(self, formula: dict[str, Any]) -> dict[str, Any]:
        # 官方文档说明：
        # generateContent 使用 contents + generationConfig，
        # 且 structured output 要设置 responseMimeType 和 responseJsonSchema。
        return {
            "contents": [
                {
                    "parts": [
                        {
                            "text": self._build_prompt(formula),
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseJsonSchema": PERSPECTIVE_JSON_SCHEMA,
                "temperature": 0.7,
            },
        }

    async def generate(self, formula: dict[str, Any]) -> dict[str, str]:
        url = f"{self.endpoint}/models/{self.model}:generateContent"
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=self._build_request_payload(formula)) as response:
                response.raise_for_status()
                body = await response.json()

        candidates = body.get("candidates") or []
        if not candidates:
            raise ValueError("Gemini response did not include candidates")

        content = candidates[0].get("content") or {}
        parts = content.get("parts") or []
        text_chunks = [part.get("text", "") for part in parts if isinstance(part, dict) and part.get("text")]
        if not text_chunks:
            raise ValueError("Gemini response did not include text parts")

        raw_text = "".join(text_chunks).strip()
        payload = json.loads(raw_text)
        if not isinstance(payload, dict):
            raise ValueError("Gemini structured output is not a JSON object")

        return payload


class AsyncFormulaDatasetBuilder:
    # 数据管道层：
    # 1. 读取标准公式
    # 2. 调用外部生成器
    # 3. 校验输出契约
    # 4. 展平为训练样本
    # 5. 保存 jsonl
    def __init__(
        self,
        src_path: str,
        out_path: str,
        generator: PerspectiveGenerator,
        max_concurrency: int = 3,
        retries: int = 2,
        instruction: str = DEFAULT_INSTRUCTION,
        limit: Optional[int] = None,
    ) -> None:
        self.src_path = src_path
        self.out_path = out_path
        self.generator = generator
        self.max_concurrency = max(1, min(max_concurrency, 4))
        self.retries = retries
        self.instruction = instruction
        self.limit = limit
        self.formulas: list[dict[str, Any]] = []
        self.semaphore = asyncio.Semaphore(self.max_concurrency)

    def load_source(self) -> None:
        if not os.path.exists(self.src_path):
            raise FileNotFoundError(f"Source file {self.src_path} not found.")

        with open(self.src_path, "r", encoding="utf-8") as handle:
            formulas = json.load(handle)

        if not isinstance(formulas, list):
            raise ValueError("Source JSON must be a list of formula objects.")

        filtered = [item for item in formulas if item.get("standard_latex")]
        if self.limit is not None:
            filtered = filtered[: self.limit]
        self.formulas = filtered

    def validate_generated_payload(self, payload: Any) -> dict[str, str]:
        # 这里把下游训练需要的数据契约钉死。
        if not isinstance(payload, dict):
            raise ValueError("generator output must be a dict")

        normalized: dict[str, str] = {}
        for key in ("beginner", "programmer", "researcher"):
            value = payload.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"generator output missing valid '{key}' field")
            normalized[key] = value.strip()
        return normalized

    async def _request_formula(self, formula: dict[str, Any]) -> list[dict[str, Any]]:
        last_error = "unknown error"

        # semaphore 仍然保留，主要是为了控制 API 并发、失败风暴和整体稳定性。
        async with self.semaphore:
            for attempt in range(self.retries + 1):
                try:
                    generated = await self.generator.generate(formula)
                    validated = self.validate_generated_payload(generated)
                    return self.flatten_records(formula, validated)
                except Exception as exc:
                    last_error = f"{type(exc).__name__}: {exc}"
                    if attempt < self.retries:
                        await asyncio.sleep(1.5 * (attempt + 1))

        print(f"[WARN] generation failed for {formula.get('name')}: {last_error}")
        return []

    def flatten_records(
        self,
        formula: dict[str, Any],
        generated: dict[str, str],
    ) -> list[dict[str, Any]]:
        # 1 条公式 * 3 个视角 -> 3 条独立训练样本。
        records: list[dict[str, Any]] = []
        for perspective in ("beginner", "programmer", "researcher"):
            records.append(
                {
                    "instruction": self.instruction,
                    "input": generated[perspective],
                    "output": formula["standard_latex"],
                    "metadata": {
                        "formula_name": formula.get("name"),
                        "category": formula.get("category"),
                        "sympy_expr": formula.get("sympy_expr"),
                        "perspective": perspective,
                        "generator": self.generator.__class__.__name__,
                        "generator_model": getattr(self.generator, "model", None),
                    },
                }
            )
        return records

    async def build(self) -> list[dict[str, Any]]:
        tasks = [self._request_formula(formula) for formula in self.formulas]
        nested_records = await asyncio.gather(*tasks)
        records = [record for group in nested_records for record in group]
        random.shuffle(records)
        return records

    def save_records(self, records: list[dict[str, Any]]) -> None:
        with open(self.out_path, "w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_generator(args: argparse.Namespace) -> PerspectiveGenerator:
    api_key = args.gemini_api_key or os.getenv("GEMINI_API_KEY")
    model = args.gemini_model or os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
    endpoint = args.gemini_endpoint or os.getenv("GEMINI_ENDPOINT", DEFAULT_GEMINI_ENDPOINT)
    timeout = args.gemini_timeout or int(os.getenv("GEMINI_TIMEOUT", "90"))

    return GeminiGenerator(
        api_key=api_key,
        model=model,
        endpoint=endpoint,
        timeout=timeout,
    )


async def async_main() -> None:
    load_local_env()

    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="formulas.json")
    parser.add_argument("--out", default="train.jsonl")
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--gemini-api-key", default=None)
    parser.add_argument("--gemini-model", default=None)
    parser.add_argument("--gemini-endpoint", default=None)
    parser.add_argument("--gemini-timeout", type=int, default=None)
    args = parser.parse_args()

    builder = AsyncFormulaDatasetBuilder(
        src_path=args.src,
        out_path=args.out,
        generator=build_generator(args),
        max_concurrency=args.concurrency,
        retries=args.retries,
        limit=args.limit,
    )
    builder.load_source()
    records = await builder.build()
    builder.save_records(records)
    print(f"[DONE] Generated {len(records)} records -> {args.out}")


if __name__ == "__main__":
    asyncio.run(async_main())
