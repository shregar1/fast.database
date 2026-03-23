"""
Helpers for optimistic locking with :class:`~fast_database.core.mixins.OptimisticLockMixin`.

SQLAlchemy can enforce version checks when ``__mapper_args__`` includes
``version_id_col``; these helpers cover manual checks in services.
"""

from __future__ import annotations

from typing import Any


class StaleVersionError(ValueError):
    """Raised when an instance's ``version`` does not match the expected value."""


def expected_version(instance: Any) -> int | None:
    """Return ``instance.version`` if the attribute exists, else ``None``."""
    return getattr(instance, "version", None)


def assert_version_matches(instance: Any, expected: int | None) -> None:
    """
    Ensure ``instance.version == expected`` before applying updates.

    Pass ``expected`` from the DTO / API (client-sent version). If ``expected``
    is ``None``, the check is skipped (e.g. create flow).
    """
    if expected is None:
        return
    current = expected_version(instance)
    if current is None:
        raise StaleVersionError("instance has no version column")
    if current != expected:
        raise StaleVersionError(
            f"stale version: expected {expected!r}, database has {current!r}"
        )
