"""SQLAlchemy mixin and utilities for soft-delete functionality.

Provides a model mixin, automatic query filtering via ``do_orm_execute``,
a repository mixin, and a cascade helper.

Usage::

    from fastx_database.soft_delete import (
        SoftDeleteMixin,
        SoftDeleteQuery,
        SoftDeleteRepositoryMixin,
        cascade_soft_delete,
        install_soft_delete_hook,
    )

    class Item(SoftDeleteMixin, Base):
        __tablename__ = "items"
        id = Column(Integer, primary_key=True)
        name = Column(String)

    # Install the session-level hook once
    install_soft_delete_hook(Session)

    # Queries automatically exclude deleted rows
    session.execute(select(Item)).scalars().all()

    # Include deleted
    session.execute(select(Item).execution_options(include_deleted=True))

    # Only deleted
    session.execute(select(Item).execution_options(only_deleted=True))
"""

from __future__ import annotations

import datetime
from datetime import timedelta
from typing import Any, Iterable, Sequence, TypeVar

from sqlalchemy import Column, DateTime, Index, event, inspect, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session, ORMExecuteState

T = TypeVar("T")


# ---------------------------------------------------------------------------
# 1. SoftDeleteMixin
# ---------------------------------------------------------------------------

class SoftDeleteMixin:
    """SQLAlchemy mixin that adds soft-delete columns and helper methods.

    Adds:
    - ``deleted_at`` column (DateTime, nullable, default ``None``, indexed)
    - ``is_deleted`` hybrid property (``True`` when ``deleted_at`` is not ``None``)
    - ``soft_delete()`` -- mark the row as deleted
    - ``restore()`` -- clear the deletion marker
    - ``hard_delete()`` -- permanently remove via ``Session.delete``
    """

    deleted_at = Column(
        DateTime,
        nullable=True,
        default=None,
        index=True,
    )

    @hybrid_property
    def is_deleted(self) -> bool:  # type: ignore[override]
        """Return ``True`` when the row has been soft-deleted."""
        return self.deleted_at is not None

    @is_deleted.expression  # type: ignore[no-redef]
    def is_deleted(cls):  # noqa: N805
        """SQL-level expression for ``is_deleted``."""
        return cls.deleted_at.isnot(None)

    def soft_delete(self) -> None:
        """Mark this record as soft-deleted (sets ``deleted_at`` to now)."""
        self.deleted_at = datetime.datetime.utcnow()

    def restore(self) -> None:
        """Restore a soft-deleted record (clears ``deleted_at``)."""
        self.deleted_at = None

    def hard_delete(self) -> None:
        """Permanently delete this record from the database.

        The instance must be associated with a session.

        Raises:
            sqlalchemy.exc.InvalidRequestError: If the instance is not
                attached to a session.
        """
        session = Session.object_session(self)
        if session is None:
            raise RuntimeError(
                "Cannot hard_delete a detached instance. "
                "Add it to a session first."
            )
        session.delete(self)


# ---------------------------------------------------------------------------
# 2. SoftDeleteQuery -- event-based automatic filtering
# ---------------------------------------------------------------------------

def _model_uses_soft_delete(mapper) -> bool:
    """Return ``True`` if *mapper*'s class uses :class:`SoftDeleteMixin`."""
    return issubclass(mapper.class_, SoftDeleteMixin)


def _soft_delete_orm_execute_handler(execute_state: ORMExecuteState) -> None:
    """``do_orm_execute`` event handler that adds soft-delete filters.

    Respects two execution options:

    * ``include_deleted=True`` -- skip the filter entirely
    * ``only_deleted=True`` -- invert the filter (``deleted_at IS NOT NULL``)
    """
    if not execute_state.is_select:
        return

    include_deleted = execute_state.execution_options.get("include_deleted", False)
    only_deleted = execute_state.execution_options.get("only_deleted", False)

    if include_deleted:
        return

    # Collect all mapped entities referenced by the statement.
    # Each column entity carries a mapper we can inspect.
    for mapper_info in execute_state.all_mappers:
        if not _model_uses_soft_delete(mapper_info):
            continue
        entity = mapper_info.class_
        if only_deleted:
            execute_state.statement = execute_state.statement.filter(
                entity.deleted_at.isnot(None)
            )
        else:
            execute_state.statement = execute_state.statement.filter(
                entity.deleted_at.is_(None)
            )


def install_soft_delete_hook(session_or_factory: Any) -> None:
    """Register the ``do_orm_execute`` hook on a session class or factory.

    Call once during application startup::

        install_soft_delete_hook(Session)

    Args:
        session_or_factory: A ``Session`` class, ``sessionmaker``,
            ``scoped_session``, or ``async_sessionmaker``.
    """
    event.listen(session_or_factory, "do_orm_execute", _soft_delete_orm_execute_handler)


class SoftDeleteQuery:
    """Namespace providing query helpers for soft-delete models.

    These are convenience class-methods that return modified ``select``
    statements.  They work with SQLAlchemy 2.0 style queries.

    Usage::

        stmt = SoftDeleteQuery.with_deleted(Item)
        stmt = SoftDeleteQuery.only_deleted(Item)
    """

    @staticmethod
    def with_deleted(entity: type[T]) -> Any:
        """Return a ``select()`` that includes soft-deleted rows.

        Equivalent to::

            select(entity).execution_options(include_deleted=True)
        """
        return select(entity).execution_options(include_deleted=True)

    @staticmethod
    def only_deleted(entity: type[T]) -> Any:
        """Return a ``select()`` that returns *only* soft-deleted rows.

        Equivalent to::

            select(entity).execution_options(only_deleted=True)
        """
        return select(entity).execution_options(only_deleted=True)


# ---------------------------------------------------------------------------
# 3. SoftDeleteRepositoryMixin
# ---------------------------------------------------------------------------

class SoftDeleteRepositoryMixin:
    """Mixin for repository classes that operate on soft-deletable models.

    Expects the host repository to expose:
    - ``self.session`` -- a SQLAlchemy ``Session``
    - ``self.model`` -- the mapped model class (must use ``SoftDeleteMixin``)

    Override ``delete`` to soft-delete by default.
    """

    # -- delete override -----------------------------------------------------

    def delete(self, id: Any) -> bool:
        """Soft-delete a record by primary key.

        Returns ``True`` if the record was found and soft-deleted,
        ``False`` otherwise.
        """
        record = self.session.get(self.model, id)
        if record is None:
            return False
        record.soft_delete()
        self.session.flush()
        return True

    # -- force delete --------------------------------------------------------

    def force_delete(self, id: Any) -> bool:
        """Hard-delete a record by primary key (permanent removal).

        Returns ``True`` if the record was found and deleted,
        ``False`` otherwise.
        """
        record = self.session.execute(
            select(self.model)
            .filter_by(id=id)
            .execution_options(include_deleted=True)
        ).scalar_one_or_none()
        if record is None:
            return False
        self.session.delete(record)
        self.session.flush()
        return True

    # -- restore -------------------------------------------------------------

    def restore(self, id: Any) -> bool:
        """Restore a previously soft-deleted record.

        Returns ``True`` if the record was found and restored,
        ``False`` otherwise.
        """
        record = self.session.execute(
            select(self.model)
            .filter_by(id=id)
            .execution_options(include_deleted=True)
        ).scalar_one_or_none()
        if record is None:
            return False
        record.restore()
        self.session.flush()
        return True

    # -- list deleted --------------------------------------------------------

    def list_deleted(self, **filters: Any) -> Sequence[Any]:
        """Return only soft-deleted records, optionally filtered.

        Args:
            **filters: Column-name / value pairs passed to ``filter_by``.
        """
        stmt = (
            select(self.model)
            .filter_by(**filters)
            .execution_options(only_deleted=True)
        )
        return self.session.execute(stmt).scalars().all()

    # -- purge ---------------------------------------------------------------

    def purge(self, older_than: timedelta) -> int:
        """Permanently delete records soft-deleted before *older_than* ago.

        Args:
            older_than: A ``timedelta`` representing the age threshold.

        Returns:
            The number of records permanently deleted.
        """
        threshold = datetime.datetime.utcnow() - older_than
        stmt = (
            select(self.model)
            .filter(self.model.deleted_at.isnot(None))
            .filter(self.model.deleted_at < threshold)
            .execution_options(include_deleted=True)
        )
        records = self.session.execute(stmt).scalars().all()
        count = len(records)
        for record in records:
            self.session.delete(record)
        if count:
            self.session.flush()
        return count

    # -- bulk soft delete ----------------------------------------------------

    def bulk_soft_delete(self, ids: Iterable[Any]) -> int:
        """Soft-delete multiple records by primary key.

        Args:
            ids: An iterable of primary-key values.

        Returns:
            The number of records that were soft-deleted.
        """
        ids = list(ids)
        if not ids:
            return 0
        stmt = (
            select(self.model)
            .filter(self.model.id.in_(ids))
        )
        records = self.session.execute(stmt).scalars().all()
        now = datetime.datetime.utcnow()
        for record in records:
            record.deleted_at = now
        if records:
            self.session.flush()
        return len(records)


# ---------------------------------------------------------------------------
# 4. cascade_soft_delete
# ---------------------------------------------------------------------------

def cascade_soft_delete(
    model: type,
    relationships: Sequence[str],
) -> None:
    """Set up cascade soft-delete on specified relationships.

    When an instance of *model* is soft-deleted (its ``deleted_at`` is set
    to a non-``None`` value), each related collection named in
    *relationships* will also be soft-deleted.  Related models must also
    use :class:`SoftDeleteMixin`.

    This works by listening to the ``set`` event on
    ``model.deleted_at``.

    Args:
        model: The parent model class (must use ``SoftDeleteMixin``).
        relationships: Sequence of relationship attribute names whose
            targets should be cascade-soft-deleted.

    Usage::

        class Parent(SoftDeleteMixin, Base):
            __tablename__ = "parents"
            id = Column(Integer, primary_key=True)
            children = relationship("Child", back_populates="parent")

        class Child(SoftDeleteMixin, Base):
            __tablename__ = "children"
            id = Column(Integer, primary_key=True)
            parent_id = Column(Integer, ForeignKey("parents.id"))
            parent = relationship("Parent", back_populates="children")

        cascade_soft_delete(Parent, ["children"])
    """

    @event.listens_for(model.deleted_at, "set")
    def _on_deleted_at_set(target: Any, value: Any, oldvalue: Any, initiator: Any) -> None:
        if value is None:
            # Restoring -- cascade restore
            for rel_name in relationships:
                related = getattr(target, rel_name, None)
                if related is None:
                    continue
                # Handle both collections and scalar relationships
                if hasattr(related, "__iter__"):
                    for child in related:
                        if hasattr(child, "restore"):
                            child.restore()
                elif hasattr(related, "restore"):
                    related.restore()
        else:
            # Soft-deleting -- cascade soft-delete
            for rel_name in relationships:
                related = getattr(target, rel_name, None)
                if related is None:
                    continue
                if hasattr(related, "__iter__"):
                    for child in related:
                        if hasattr(child, "soft_delete"):
                            child.soft_delete()
                elif hasattr(related, "soft_delete"):
                    related.soft_delete()
