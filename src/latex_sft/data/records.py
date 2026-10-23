"""Stable record identities, lineage, deduplication and summaries."""
from copy import deepcopy
from typing import Any
from .text import normalized_text


def lineage_rows(row: dict[str, Any]) -> list[dict[str, Any]]:
    """All pre-deduplication source records, including their original grouping edges."""
    return [row, *row.get('metadata', {}).get('source_records', [])]


def group_keys(row: dict[str, Any]) -> set[tuple[str, str]]:
    keys = set()
    for source in lineage_rows(row):
        meta = source.get('metadata', {})
        # Ancestor inputs and descendants' source_input share an identity.
        for value in (source.get('input'), meta.get('source_input')):
            if value: keys.add(('input', normalized_text(value)))
        # A repair cannot sever the connection to the source's original equation.
        for value in (source.get('output'), meta.get('original_output')):
            if value: keys.add(('equation', normalized_text(value)))
        for signature in meta.get('structural_signatures', []): keys.add(('structure', signature))
        for signature in meta.get('template_signatures', []): keys.add(('template', signature))
        if meta.get('near_family_id'): keys.add(('near_family',meta['near_family_id']))
        for label, field in (('family', 'formula_name'), ('lineage', 'formula_id')):
            if meta.get(field): keys.add((label, str(meta[field])))
        for source_id in [meta.get('source_id'), *meta.get('duplicate_source_ids', [])]:
            if source_id: keys.add(('source', source_id))
    return keys


def dedupe_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    seen: dict[tuple[str, str], dict[str, Any]] = {}
    deduped: list[dict[str, Any]] = []
    duplicates = 0
    for record in records:
        key = (normalized_text(record["input"]), normalized_text(record["output"]))
        if key in seen:
            duplicates += 1
            meta = seen[key].setdefault('metadata', {})
            for source in lineage_rows(record):
                snapshot = deepcopy(source)
                snapshot.setdefault('metadata', {}).pop('source_records', None)
                meta.setdefault('source_records', []).append(snapshot)
                source_id = snapshot['metadata'].get('source_id')
                if source_id and source_id != meta.get('source_id'):
                    ids = meta.setdefault('duplicate_source_ids', [])
                    if source_id not in ids: ids.append(source_id)
            continue
        clone = deepcopy(record)
        seen[key] = clone
        deduped.append(clone)
    return deduped, duplicates


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {"total": len(records), "layers": {}, "categories": {}}
    for record in records:
        metadata = record.get("metadata") or {}
        layer = str(metadata.get("dataset_layer") or "unknown")
        category = str(metadata.get("category") or "unknown")
        summary["layers"][layer] = summary["layers"].get(layer, 0) + 1
        summary["categories"][category] = summary["categories"].get(category, 0) + 1
    return summary

