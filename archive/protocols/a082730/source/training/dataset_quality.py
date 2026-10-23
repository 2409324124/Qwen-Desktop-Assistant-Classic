from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from training.latex_postprocess import postprocess_latex

_LOW_INFORMATION_PROMPTS = {"那个", "就是", "我想问", "product"}


def is_low_information_prompt(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized in _LOW_INFORMATION_PROMPTS


def record_selector(record: dict[str, Any]) -> tuple[str, str, str]:
    metadata = record.get("metadata") or {}
    return (
        str(metadata.get("source_file") or ""),
        str(record.get("input") or ""),
        str(metadata.get("formula_name") or ""),
    )


def load_quality_overrides(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise ValueError(f"{path}: quality overrides must be a JSON array of objects")
    return payload


def apply_quality_overrides(
    records: list[dict[str, Any]],
    overrides: list[dict[str, Any]],
    *,
    target_field: str = "output",
    require_all_overrides: bool = True,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    decisions: dict[tuple[str, str, str], dict[str, Any]] = {}
    for override in overrides:
        selector = (
            str(override.get("source_file") or ""),
            str(override.get("input") or ""),
            str(override.get("formula_name") or ""),
        )
        if selector in decisions:
            raise ValueError(f"duplicate quality override: {selector}")
        decisions[selector] = override

    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    matched: set[tuple[str, str, str]] = set()
    for record in records:
        selector = record_selector(record)
        override = decisions.get(selector)
        if override is None and is_low_information_prompt(str(record.get("input") or "")):
            rejected.append(record)
            counts["excluded"] += 1
            continue
        if override is None:
            normalized = deepcopy(record)
            value = normalized.get(target_field)
            if isinstance(value, str):
                normalized_value = postprocess_latex(value)
                normalized[target_field] = normalized_value
                if target_field == "output":
                    normalized["canonical_output"] = normalized_value
            accepted.append(normalized)
            counts["kept"] += 1
            continue

        matched.add(selector)
        action = override.get("action")
        if action == "exclude":
            rejected.append(record)
            counts["excluded"] += 1
        elif action == "replace_output":
            output = override.get("output")
            if not isinstance(output, str) or not output.strip():
                raise ValueError(f"replacement output must be non-empty: {selector}")
            repaired = deepcopy(record)
            repaired[target_field] = postprocess_latex(output)
            if target_field == "output":
                repaired["canonical_output"] = repaired[target_field]
            metadata = dict(repaired.get("metadata") or {})
            metadata["quality_override_reason"] = str(override.get("reason") or "")
            repaired["metadata"] = metadata
            accepted.append(repaired)
            counts["repaired"] += 1
        else:
            raise ValueError(f"unsupported quality override action {action!r}: {selector}")

    missing = set(decisions) - matched
    if require_all_overrides and missing:
        raise ValueError(f"quality overrides did not match records: {sorted(missing)}")

    return accepted, rejected, {name: counts[name] for name in ("kept", "repaired", "excluded")}
