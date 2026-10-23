"""Deterministic transitive closure shared by allocation and frozen isolation.

The kernel computes connectivity only. Callers own split policy, group IDs,
quarantine decisions and their historical evidence schemas.
"""
from collections import defaultdict
from collections.abc import Callable, Iterable, Sequence
from typing import Hashable, TypeVar

T = TypeVar("T")


def connected_components(
    items: Sequence[T],
    keys: Callable[[T], Iterable[Hashable]],
    *,
    order: Iterable[int] | None = None,
    on_edge: Callable[[int, int, Hashable], None] | None = None,
    on_item: Callable[[int], None] | None = None,
) -> list[list[T]]:
    """Connect items sharing keys; preserve input order within/components.

    Keys and visit order determine evidence order. Every repeated key emits an
    edge (even if already transitively connected), preserving audit evidence.
    ``on_edge`` receives first owner, current item and the shared key.
    """
    parent = list(range(len(items)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    owners: dict[Hashable, int] = {}
    for index in range(len(items)) if order is None else order:
        for key in sorted(keys(items[index])):
            if key in owners:
                anchor = owners[key]
                parent[find(index)] = find(anchor)
                if on_edge is not None:
                    on_edge(anchor, index, key)
            else:
                owners[key] = index
        if on_item is not None:
            on_item(index)
    groups: dict[int, list[T]] = defaultdict(list)
    for index, item in enumerate(items):
        groups[find(index)].append(item)
    return list(groups.values())
