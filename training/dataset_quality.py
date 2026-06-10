from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
from typing import Any


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
        if override is None:
            accepted.append(record)
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
            repaired[target_field] = output
            if target_field == "output":
                repaired["canonical_output"] = output
            metadata = dict(repaired.get("metadata") or {})
            metadata["quality_override_reason"] = str(override.get("reason") or "")
            repaired["metadata"] = metadata
            accepted.append(repaired)
            counts["repaired"] += 1
        else:
            raise ValueError(f"unsupported quality override action {action!r}: {selector}")

    missing = set(decisions) - matched
    if missing:
        raise ValueError(f"quality overrides did not match records: {sorted(missing)}")

    return accepted, rejected, {name: counts[name] for name in ("kept", "repaired", "excluded")}
