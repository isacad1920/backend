"""Common pagination utilities for consistent API behavior."""
from __future__ import annotations
from typing import Tuple

DEFAULT_PAGE = 1
DEFAULT_SIZE = 25
MAX_SIZE = 200

class PaginationParams:
    __slots__ = ('page','size','skip','take')
    def __init__(self, page: int, size: int):
        self.page = page
        self.size = size
        self.skip = (page - 1) * size
        self.take = size


def clamp_page_size(page: int | None, size: int | None) -> PaginationParams:
    p = page or DEFAULT_PAGE
    s = size or DEFAULT_SIZE
    if p < 1:
        p = 1
    if s < 1:
        s = DEFAULT_SIZE
    if s > MAX_SIZE:
        s = MAX_SIZE
    return PaginationParams(p, s)


def page_count(total: int, size: int) -> int:
    if total <= 0:
        return 1
    from math import ceil
    return ceil(total/size)
