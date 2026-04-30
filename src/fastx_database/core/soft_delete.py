"""Helpers for querying and mutating soft-deleted rows.

Expects models using :class:`fastx_database.core.mixins.SoftDeleteMixin` or any
model with an ``is_deleted`` boolean column (and optionally ``deleted_at``).

Usage:
    from fastx_database.core.mixins import SoftDeleteMixin
    from fastx_database.core.soft_delete import (
        where_not_deleted,
        select_active,
        mark_soft_deleted,
        restore_soft_deleted,
        SoftDeleteRepositoryMixin,
    )

    class Item(SoftDeleteMixin, Base):
        __tablename__ = "items"
        id = Column(Integer, primary_key=True)
        name = Column(String)

    # Create
    item = Item(name="Test")
    db.add(item)
    db.commit()

    # Soft delete (sets deleted_at and is_deleted)
    item.delete()
    db.commit()

    # Query excludes deleted by default
    stmt = select_active(Item)
    items = session.execute(stmt).scalars().all()  # Deleted items excluded

    # Include deleted
    all_items = session.execute(
        select(Item)
    ).scalars().all()

    # Restore
    item.restore()
    db.commit()
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TypeVar, Optional

from sqlalchemy import Select, select
from sqlalchemy.orm import InstrumentedAttribute

T = TypeVar("T")


def where_not_deleted(model_class: type[T]) -> Any:
    """SQL expression: ``is_deleted IS false``.

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
    """Apply ``WHERE is_deleted IS false`` to a legacy :class:`Query` or compatible object.

    Prefer :func:`where_not_deleted` / :func:`select_active` for 2.0 ``select()``.
    """
    return query.filter(is_deleted_attr.is_(False))


def filter_not_deleted(query: Any) -> Any:
    """Filter query to exclude soft-deleted records.

    Usage:
        query = db.query(Item)
        query = filter_not_deleted(query)

    Works with legacy Query objects.
    """
    entity = query._entity_zero()
    if hasattr(entity.class_, "is_deleted"):
        return query.filter(entity.class_.is_deleted == False)
    return query


# Repository mixin for soft delete support
class SoftDeleteRepositoryMixin:
    """Repository mixin that adds soft delete operations.

    Usage:
        class ItemRepository(BaseRepository, SoftDeleteRepositoryMixin):
            pass
    """

    async def find_with_deleted(self, **filters):
        """Find records including soft-deleted ones."""
        query = self._query(**filters)
        return await self._execute_query(query)

    async def find_only_deleted(self, **filters):
        """Find only soft-deleted records."""
        query = self._query(**filters)
        query = query.filter(self._entity_class.is_deleted == True)
        return await self._execute_query(query)

    async def soft_delete(self, entity_id: str) -> bool:
        """Soft delete a record by ID."""
        entity = await self.get_by_id(entity_id)
        if entity and hasattr(entity, "delete"):
            entity.delete()
            await self._save(entity)
            return True
        return False

    async def restore(self, entity_id: str) -> bool:
        """Restore a soft-deleted record."""
        entity = await self.get_by_id(entity_id)
        if entity and hasattr(entity, "restore"):
            entity.restore()
            await self._save(entity)
            return True
        return False


# Legacy Query class for backward compatibility
class SoftDeleteQuery:
    """Query class that automatically filters out soft-deleted records.

    Usage:
        class Item(SoftDeleteMixin, Base):
            __tablename__ = "items"
            query_class = SoftDeleteQuery
    """

    def __new__(cls, *entities, **kwargs):
        """Create a new query that excludes deleted records."""
        query = super().__new__(cls)
        # Filter out deleted by default
        if entities:
            mapper = entities[0].__mapper__
            if hasattr(mapper.class_, "is_deleted"):
                query = query.filter(mapper.class_.is_deleted == False)
        return query

    def include_deleted(self):
        """Include soft-deleted records in results."""
        # Remove the is_deleted filter
        return self.filter()

    def only_deleted(self):
        """Return only soft-deleted records."""
        return self.filter(self._entity_zero().class_.is_deleted == True)
