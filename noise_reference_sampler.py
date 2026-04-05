import argparse
import asyncio
import json
from collections import Counter
from pathlib import Path
from typing import Any

from tavily_client import build_tavily_client


DEFAULT_TARGET_FORMULAS = [
    "Softmax Function",
    "ReLU Activation Function",
    "Limit Definition of Derivative",
    "Fundamental Theorem of Calculus",
    "Coulomb's Law",
    "Rotation Matrix",
    "Jacobian Matrix",
    "Law of Sines",
    "Mean Squared Error",
    "Gradient Descent Update",
]


NOISE_QUERY_TEMPLATES = {
    "messy_nl": [
        "{name} formula how do I type this",
        "{name} 这个公式怎么打",
    ],
    "plain_text": [
        "{name} plain text formula notation",
        "{name} keyboard formula input",
    ],
    "latex_help": [
        "{name} latex help input notation",
        "{name} latex 写法 求助",
    ],
    "mixed_language": [
        "{name} 中文 英文 混合 公式 写法",
        "{name} formula notes shorthand mixed language",
    ],
}


def load_formulas(src_path: str) -> list[dict[str, Any]]:
    with open(src_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("Source formulas file must be a JSON list.")
    return data


def choose_target_formulas(formulas: list[dict[str, Any]], names: list[str]) -> list[dict[str, Any]]:
    by_name: dict[str, dict[str, Any]] = {}
    for formula in formulas:
        name = formula.get("name")
        if isinstance(name, str) and name not in by_name:
            by_name[name] = formula

    selected: list[dict[str, Any]] = []
    for name in names:
        formula = by_name.get(name)
        if formula:
            selected.append(formula)
    return selected


def build_queries(formula: dict[str, Any]) -> list[dict[str, str]]:
    name = formula["name"]
    queries: list[dict[str, str]] = []
    for noise_type, templates in NOISE_QUERY_TEMPLATES.items():
        for template in templates:
            queries.append(
                {
                    "noise_type": noise_type,
                    "query": template.format(name=name),
                }
            )
    return queries


async def sample_formula_noise_references(client, formula: dict[str, Any], max_results: int) -> dict[str, Any]:
    queries = build_queries(formula)
    sampled_queries: list[dict[str, Any]] = []

    for query_obj in queries:
        response = await client.search(
            query_obj["query"],
            topic="general",
            search_depth="advanced",
            max_results=max_results,
            include_answer="advanced",
            include_raw_content=False,
        )
        sampled_queries.append(
            {
                "noise_type": query_obj["noise_type"],
                "query": query_obj["query"],
                "answer": response.get("answer"),
                "results": [
                    {
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "content": item.get("content"),
                        "score": item.get("score"),
                    }
                    for item in response.get("results", [])
                ],
            }
        )

    return {
        "name": formula.get("name"),
        "category": formula.get("category"),
        "standard_latex": formula.get("standard_latex"),
        "queries": sampled_queries,
    }


def write_markdown_summary(path: str, references: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    lines.append("# 真实噪声表达采样摘要")
    lines.append("")
    lines.append("这份文档用于提炼 noisy 层规则，不直接作为训练数据。")
    lines.append("")

    category_counts = Counter(item["category"] for item in references)
    lines.append("## 覆盖分布")
    lines.append("")
    for category, count in sorted(category_counts.items()):
        lines.append(f"- `{category}`: {count}")
    lines.append("")

    for item in references:
        lines.append(f"## {item['name']}")
        lines.append("")
        lines.append(f"- Category: `{item['category']}`")
        lines.append(f"- Formula: `{item['standard_latex']}`")
        lines.append("")

        for query in item["queries"]:
            lines.append(f"### {query['noise_type']} | {query['query']}")
            lines.append("")
            if query.get("answer"):
                lines.append(f"- Answer Summary: {query['answer']}")
            for result in query["results"][:3]:
                title = result.get("title") or "(untitled)"
                url = result.get("url") or ""
                content = (result.get("content") or "").replace("\n", " ").strip()
                if len(content) > 280:
                    content = content[:277] + "..."
                lines.append(f"- [{title}]({url})")
                if content:
                    lines.append(f"  Snippet: {content}")
            lines.append("")

    Path(path).write_text("\n".join(lines), encoding="utf-8")


async def async_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="formulas_clean_120.json")
    parser.add_argument("--out-json", default="noise_reference_sample.json")
    parser.add_argument("--out-md", default="noise_reference_sample.md")
    parser.add_argument("--max-results", type=int, default=3)
    args = parser.parse_args()

    formulas = load_formulas(args.src)
    targets = choose_target_formulas(formulas, DEFAULT_TARGET_FORMULAS)
    client = build_tavily_client()

    references: list[dict[str, Any]] = []
    for formula in targets:
        references.append(await sample_formula_noise_references(client, formula, args.max_results))

    Path(args.out_json).write_text(
        json.dumps(references, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_markdown_summary(args.out_md, references)

    print(f"[DONE] Sampled {len(references)} formulas -> {args.out_json} and {args.out_md}")


if __name__ == "__main__":
    asyncio.run(async_main())
