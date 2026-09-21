from __future__ import annotations

from typing import TypeVar

T = TypeVar("T")


def paginate(items: list[T], page: int, page_size: int) -> tuple[list[T], int, int]:
    total = len(items)
    pages = (total + page_size - 1) // page_size if total else 0
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], total, pages
