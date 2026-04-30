"""Status and state string constants."""

from __future__ import annotations

from typing import Final


class Status:
    PENDING: Final[str] = "pending"
    ACTIVE: Final[str] = "active"
    DRAFT: Final[str] = "draft"
    PAID: Final[str] = "paid"
    SHIPPED: Final[str] = "shipped"
    PAYMENT_FAILED: Final[str] = "payment_failed"


class SourceType:
    MANUAL: Final[str] = "MANUAL"


class LedgerType:
    INCOME: Final[str] = "INCOME"
    EXPENSE: Final[str] = "EXPENSE"


class Frequency:
    WEEKLY: Final[str] = "WEEKLY"
    MONTHLY: Final[str] = "MONTHLY"


class Channel:
    IN_APP: Final[str] = "in_app"


class Category:
    PRODUCT: Final[str] = "product"


class AuthMethod:
    PASSWORD: Final[str] = "password"


class Scope:
    FULL: Final[str] = "full"
