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

PERSPECTIVE_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "beginner": {
            "type": "string",
            "description": "纯口语化描述（小白视角），用自然中文描述用户会怎么说这条公式。",
        },
        "programmer": {
            "type": "string",
            "description": "键盘伪代码（程序员视角），用 plain-text、ASCII、代码式写法表达公式。",
        },
        "researcher": {
            "type": "string",
            "description": "中英夹杂的科研速记（真实科研场景），像组会笔记、草稿、推导速记。",
        },
    },
    "required": ["beginner", "programmer", "researcher"],
    "additionalProperties": False,
}


def load_local_env(env_path: str = ".env") -> None:
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
    @abstractmethod
    async def generate(self, formula: dict[str, Any]) -> dict[str, str]:
        raise NotImplementedError


class GeminiGenerator(PerspectiveGenerator):
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
        return model.split("/", 1)[1] if model.startswith("models/") else model

    def _build_prompt(self, formula: dict[str, Any]) -> str:
        # 这版 prompt 吸收了 Tavily 检索得到的真实网页表达风格：
        # 1. beginner 更像用户提问，而不是逐字符念符号
        # 2. programmer 更像 plain-text/ASCII/代码式键盘输入
        # 3. researcher 更像中英夹杂、组会速记、草稿 shorthand
        #
        # 同时继续严格限制：不能求解、不能解释含义、不能改写变量结构、不能直接抄标准公式。
        return (
            "# [角色设定]\n"
            "你是一位资深的大语言模型数据合成专家与提示词工程师，擅长为 SFT/LoRA 构造高质量用户输入数据。\n\n"
            "# [任务目标]\n"
            "给定一条标准公式，请生成三种不同风格的“用户输入”，这些输入都应该指向同一个目标公式，"
            "但表达方式要像真实人类会输入给模型的话，而不是把标准公式原样抄一遍。\n\n"
            "# [目标公式元数据]\n"
            f"- name: {formula.get('name', 'unknown')}\n"
            f"- category: {formula.get('category', 'unknown')}\n"
            f"- target_formula: {formula['standard_latex']}\n"
            f"- sympy_expr: {formula.get('sympy_expr')}\n\n"
            "# [三种视角要求]\n"
            "1. beginner（纯口语化描述 / 小白视角）\n"
            "- 必须主要使用自然中文。\n"
            "- 要像真实用户在问模型“这个公式怎么写”。\n"
            "- 可以描述结构，但不要机械地逐字符念公式。\n"
            "- 少用“像某个符号长什么样”这类生硬表达。\n"
            "- 不要出现太多程序员式符号缩写，比如 sum、inf、==、exp( 之类。\n\n"
            "2. programmer（键盘伪代码 / 程序员视角）\n"
            "- 要像人在键盘上直接输入的 plain-text 公式。\n"
            "- 允许使用 ASCII、函数名、简写、代码风格写法。\n"
            "- 可以使用 sum(), exp(), int, sqrt, ^, **, ==, <= 这类键盘表达。\n"
            "- 但不要只是把标准公式机械转抄成另一种排版；要保留真实输入感。\n\n"
            "3. researcher（中英夹杂科研速记 / 真实科研场景）\n"
            "- 要像组会笔记、论文草稿、推导速记、白板记录。\n"
            "- 允许中英夹杂、术语缩写、局部省略、简短片段式表达。\n"
            "- 风格应更像 shorthand，而不是完整解释句。\n"
            "- 可以简洁，但必须仍然能明显指向目标公式。\n\n"
            "# [硬性约束]\n"
            "1. 严禁求解、推导、解释物理意义或数学意义。\n"
            "2. 严禁捏造目标公式中不存在的变量、系数、上下限、条件。\n"
            "3. 三个字段必须都忠实对应同一条目标公式。\n"
            "4. beginner / programmer / researcher 三种风格必须明显不同。\n"
            "5. 不要输出 markdown、标题、解释、问候语。\n"
            "6. 最终只返回结构化 JSON，对应字段为 beginner、programmer、researcher。\n\n"
            "# [反例提醒]\n"
            "- 不要把 beginner 写成逐字符读公式。\n"
            "- 不要把 programmer 写成几乎与标准公式完全一样的转写。\n"
            "- 不要把 researcher 写成完整教材式解释段落。\n"
        )

    def _build_request_payload(self, formula: dict[str, Any]) -> dict[str, Any]:
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
                "temperature": 0.75,
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
