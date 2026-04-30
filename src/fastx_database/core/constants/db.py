"""Database-level constants (string lengths, flags, defaults)."""

from __future__ import annotations

from typing import Final


class StringLength:
    URN: Final[int] = 128
    CODE: Final[int] = 64
    NAME: Final[int] = 255
    EMAIL: Final[int] = 255
    PASSWORD: Final[int] = 255
    STATUS: Final[int] = 32
    PHONE: Final[int] = 32
    DESCRIPTION: Final[int] = 512
    LONG_TEXT: Final[int] = 1024
    UUID: Final[int] = 36
    SOFT_DELETE_FLAG: Final[int] = 1


class SoftDeleteFlag:
    NO: Final[str] = "N"
    YES: Final[str] = "Y"


class ServerDefault:
    EMPTY_JSON_ARRAY: Final[str] = "[]"
    FALSE: Final[str] = "false"
    TRUE: Final[str] = "true"
    ZERO: Final[str] = "0"


DEFAULT_VERSION: Final[int] = 0
DEFAULT_ATTEMPTS: Final[int] = 0
MAX_IP_ADDRESS_LENGTH: Final[int] = 45
