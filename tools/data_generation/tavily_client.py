import argparse
import asyncio
import json
import os
from typing import Any, Optional

import aiohttp


DEFAULT_TAVILY_BASE_URL = "https://api.tavily.com"


def load_local_env(env_path: str = ".env") -> None:
    # 轻量级 .env 读取器。
    # 只解析 KEY=VALUE，忽略空行和注释行。
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


class TavilyClient:
    # Tavily 的轻量异步客户端。
    #
    # 当前先聚焦最常用的 search 接口，后面如果需要 extract/crawl/research，
    # 可以沿用同样的模式继续扩展。
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_TAVILY_BASE_URL,
        timeout: int = 60,
    ) -> None:
        if not api_key:
            raise ValueError("Tavily API key is required. Set TAVILY_API_KEY in .env or environment variables.")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def search(
        self,
        query: str,
        *,
        topic: str = "general",
        search_depth: str = "advanced",
        max_results: int = 5,
        include_answer: bool | str = "advanced",
        include_raw_content: bool | str = False,
        include_domains: Optional[list[str]] = None,
        exclude_domains: Optional[list[str]] = None,
        time_range: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        country: Optional[str] = None,
    ) -> dict[str, Any]:
        # 按 Tavily 官方 search 接口封装请求体。
        # 返回原始 JSON，调用方按自己的场景做后处理。
        payload: dict[str, Any] = {
            "query": query,
            "topic": topic,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
        }

        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains
        if time_range:
            payload["time_range"] = time_range
        if start_date:
            payload["start_date"] = start_date
        if end_date:
            payload["end_date"] = end_date
        if country:
            payload["country"] = country

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{self.base_url}/search",
                headers=self._headers,
                json=payload,
            ) as response:
                response.raise_for_status()
                return await response.json()


def build_tavily_client() -> TavilyClient:
    load_local_env()
    api_key = os.getenv("TAVILY_API_KEY")
    base_url = os.getenv("TAVILY_BASE_URL", DEFAULT_TAVILY_BASE_URL)
    timeout = int(os.getenv("TAVILY_TIMEOUT", "60"))
    return TavilyClient(api_key=api_key, base_url=base_url, timeout=timeout)


async def async_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Query to send to Tavily search")
    parser.add_argument("--topic", default="general")
    parser.add_argument("--search-depth", default="advanced")
    parser.add_argument("--max-results", type=int, default=5)
    parser.add_argument("--include-answer", default="advanced")
    parser.add_argument("--include-raw-content", default="false")
    args = parser.parse_args()

    raw_content_value: bool | str
    if args.include_raw_content.lower() in {"true", "markdown", "text"}:
        raw_content_value = (
            True if args.include_raw_content.lower() == "true" else args.include_raw_content.lower()
        )
    else:
        raw_content_value = False

    client = build_tavily_client()
    data = await client.search(
        args.query,
        topic=args.topic,
        search_depth=args.search_depth,
        max_results=args.max_results,
        include_answer=args.include_answer,
        include_raw_content=raw_content_value,
    )
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(async_main())
