"""Pagination limit constants."""

from __future__ import annotations

from typing import Final


class Pagination:
    DEFAULT_LIMIT: Final[int] = 100
    LARGE_LIMIT: Final[int] = 200
    SMALL_LIMIT: Final[int] = 50
    CHAT_LIMIT: Final[int] = 20
    BULK_LIMIT: Final[int] = 500
    METERED_BILLING_LIMIT: Final[int] = 5000
    MAX_EXPORT_LIMIT: Final[int] = 10000
