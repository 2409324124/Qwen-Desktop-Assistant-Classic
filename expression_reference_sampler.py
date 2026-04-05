import argparse
import asyncio
import json
from collections import Counter
from pathlib import Path
from typing import Any

from tavily_client import build_tavily_client


# 小规模 prompt 校准研究集。
# 先从这些代表性公式入手，避免一上来把检索面铺太大。
DEFAULT_TARGET_FORMULAS = [
    "Softmax Function",
    "ReLU Activation Function",
    "Fundamental Theorem of Calculus",
    "Gaussian Integral",
    "Coulomb's Law",
    "Schrodinger Equation",
    "Rotation Matrix",
    "Jacobian Matrix",
    "Pythagorean Theorem",
    "Euler's Formula",
]


QUERY_TEMPLATES = {
    "beginner": [
        "{name} how people describe this formula in plain language",
        "{name} 口语 怎么说 公式",
    ],
    "programmer": [
        "{name} how to type formula in plain text",
        "{name} keyboard notation formula",
    ],
    "researcher": [
        "{name} shorthand notation notes formula",
        "{name} 中英 公式 速记",
    ],
}


def load_formulas(src_path: str) -> list[dict[str, Any]]:
    with open(src_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("Source formulas file must be a JSON list.")
    return data


def choose_target_formulas(
    formulas: list[dict[str, Any]],
    names: list[str],
) -> list[dict[str, Any]]:
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
    for style, templates in QUERY_TEMPLATES.items():
        for template in templates:
            queries.append(
                {
                    "style": style,
                    "query": template.format(name=name),
                }
            )
    return queries


async def sample_formula_references(
    client,
    formula: dict[str, Any],
    max_results: int,
) -> dict[str, Any]:
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
                "style": query_obj["style"],
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
    lines.append("# 公式真实表达采样摘要")
    lines.append("")
    lines.append("这份文档用于给 prompt 调优提供真实网页表达参考，不直接作为训练数据。")
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
            lines.append(f"### {query['style']} | {query['query']}")
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
    parser.add_argument("--out-json", default="expression_reference_sample.json")
    parser.add_argument("--out-md", default="expression_reference_sample.md")
    parser.add_argument("--max-results", type=int, default=4)
    args = parser.parse_args()

    formulas = load_formulas(args.src)
    targets = choose_target_formulas(formulas, DEFAULT_TARGET_FORMULAS)
    client = build_tavily_client()

    references: list[dict[str, Any]] = []
    for formula in targets:
        references.append(await sample_formula_references(client, formula, args.max_results))

    Path(args.out_json).write_text(
        json.dumps(references, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_markdown_summary(args.out_md, references)

    print(f"[DONE] Sampled {len(references)} formulas -> {args.out_json} and {args.out_md}")


if __name__ == "__main__":
    asyncio.run(async_main())
