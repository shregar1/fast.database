"""
Helpers for querying and mutating soft-deleted rows.

Expects models using :class:`fastmvc_db_models.mixins.SoftDeleteMixin` or any
model with an ``is_deleted`` boolean column (and optionally ``deleted_at``).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.orm import InstrumentedAttribute

T = TypeVar("T")


def where_not_deleted(model_class: type[T]) -> Any:
    """
    SQL expression: ``is_deleted IS false``.

    Use with 2.0 style ``select()`` / ``update()``::

        stmt = select(Model).where(where_not_deleted(Model))
    """
    return model_class.is_deleted.is_(False)


def select_active(model_class: type[T]) -> Select[tuple[T]]:
    """``select(model_class).where(not deleted)``."""
    return select(model_class).where(where_not_deleted(model_class))


def mark_soft_deleted(
    instance: Any,
    *,
    when: datetime | None = None,
) -> None:
    """Set ``is_deleted`` true and ``deleted_at`` when the attribute exists."""
    instance.is_deleted = True
    if hasattr(instance, "deleted_at"):
        instance.deleted_at = when or datetime.now(timezone.utc)


def restore_soft_deleted(instance: Any) -> None:
    """Clear soft-delete flags (e.g. admin undo)."""
    instance.is_deleted = False
    if hasattr(instance, "deleted_at"):
        instance.deleted_at = None


def filter_active(query: Any, is_deleted_attr: InstrumentedAttribute[bool]) -> Any:
    """
    Apply ``WHERE is_deleted IS false`` to a legacy :class:`Query` or compatible object.

    Prefer :func:`where_not_deleted` / :func:`select_active` for 2.0 ``select()``.
    """
    return query.filter(is_deleted_attr.is_(False))
