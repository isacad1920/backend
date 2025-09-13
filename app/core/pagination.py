"""
Pagination helpers for converting between skip/limit and page/size.
"""
from typing import Tuple


def to_page_size(skip: int, limit: int) -> Tuple[int, int]:
    """Convert skip/limit to page/size."""
    if limit <= 0:
        return 1, 10
    page = (max(skip, 0) // limit) + 1
    return page, limit


def to_skip_limit(page: int, size: int) -> Tuple[int, int]:
    """Convert page/size to skip/limit."""
    page = max(page, 1)
    size = max(size, 1)
    skip = (page - 1) * size
    return skip, size
