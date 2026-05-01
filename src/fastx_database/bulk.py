"""Bulk operations utilities for SQLAlchemy repositories.

Provides a mixin class with efficient batch insert, update, delete, and upsert
methods, plus supporting dataclasses and helpers.

Usage::

    from fastx_database.bulk import BulkOperationsMixin, BulkResult

    class MyRepository(BulkOperationsMixin):
        def __init__(self, session):
            self.session = session

        async def seed_users(self, user_dicts: list[dict]) -> list:
            return await self.bulk_create(User, user_dicts, batch_size=500)

        async def sync_products(self, product_dicts: list[dict]) -> int:
            return await self.bulk_upsert(
                Product, product_dicts, key_fields=["sku"],
            )
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Iterable, Iterator, TypeVar

from sqlalchemy import delete, inspect, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def chunked(iterable: Iterable[T], size: int) -> Iterator[list[T]]:
    """Yield successive chunks of *size* from *iterable*.

    >>> list(chunked([1, 2, 3, 4, 5], 2))
    [[1, 2], [3, 4], [5]]
    """
    if size < 1:
        raise ValueError("Chunk size must be >= 1")
    batch: list[T] = []
    for item in iterable:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class BulkResult:
    """Aggregate result of a bulk operation."""

    created: int = 0
    updated: int = 0
    deleted: int = 0
    errors: int = 0
    failed_items: list[dict[str, Any]] = field(default_factory=list)
    duration_ms: float = 0.0

    @property
    def total_affected(self) -> int:
        return self.created + self.updated + self.deleted

    def __repr__(self) -> str:
        parts = []
        if self.created:
            parts.append(f"created={self.created}")
        if self.updated:
            parts.append(f"updated={self.updated}")
        if self.deleted:
            parts.append(f"deleted={self.deleted}")
        if self.errors:
            parts.append(f"errors={self.errors}")
        parts.append(f"duration_ms={self.duration_ms:.1f}")
        return f"BulkResult({', '.join(parts)})"


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------


class BulkOperationsMixin:
    """Mixin providing async bulk CRUD operations for SQLAlchemy repositories.

    The consuming class must expose either a ``session`` attribute or pass a
    session explicitly to each method.  Both
    :class:`~sqlalchemy.ext.asyncio.AsyncSession` and synchronous
    :class:`~sqlalchemy.orm.Session` are supported — when a synchronous session
    is provided the helpers call synchronous engine methods instead.
    """

    # Allow subclasses to override the default batch size globally.
    default_batch_size: int = 1000

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_session(self, session: AsyncSession | Any | None) -> Any:
        """Return the session to use — explicit param wins over self.session."""
        if session is not None:
            return session
        s = getattr(self, "session", None)
        if s is None:
            raise RuntimeError(
                "No session available. Either set self.session or pass "
                "a session to the bulk method."
            )
        return s

    @staticmethod
    def _is_async_session(session: Any) -> bool:
        return isinstance(session, AsyncSession)

    @staticmethod
    def _primary_key_columns(model_class: type) -> list[str]:
        """Return the primary key column names for *model_class*."""
        mapper = inspect(model_class)
        return [col.name for col in mapper.primary_key]

    # ------------------------------------------------------------------
    # bulk_create
    # ------------------------------------------------------------------

    async def bulk_create(
        self,
        model_class: type,
        items: list[dict[str, Any]],
        *,
        batch_size: int | None = None,
        session: AsyncSession | Any | None = None,
    ) -> list[Any]:
        """Insert *items* in efficient batches and return created ORM objects.

        Uses ``insert().values()`` with ``returning()`` to fetch back the
        created rows including server-generated columns (e.g. auto-increment
        IDs, defaults).

        Parameters
        ----------
        model_class:
            The SQLAlchemy ORM model class to insert into.
        items:
            A list of dicts, each representing a row to insert.
        batch_size:
            Number of rows per INSERT statement.  Defaults to
            ``self.default_batch_size``.
        session:
            Optional explicit session.  Falls back to ``self.session``.

        Returns
        -------
        list
            The created ORM instances (or raw Row objects when ``returning``
            is not supported).
        """
        if not items:
            return []

        batch_size = batch_size or self.default_batch_size
        sess = self._resolve_session(session)
        is_async = self._is_async_session(sess)
        created: list[Any] = []
        total = len(items)

        logger.debug(
            "bulk_create: inserting %d rows into %s (batch_size=%d)",
            total,
            model_class.__tablename__,
            batch_size,
        )

        for idx, batch in enumerate(chunked(items, batch_size), start=1):
            try:
                stmt = pg_insert(model_class).values(batch).returning(model_class)
                if is_async:
                    result = await sess.execute(stmt)
                else:
                    result = sess.execute(stmt)
                rows = result.scalars().all()
                created.extend(rows)
                logger.debug(
                    "bulk_create: batch %d — inserted %d rows", idx, len(rows)
                )
            except Exception:
                logger.exception(
                    "bulk_create: batch %d failed (%d items)", idx, len(batch)
                )
                raise

        logger.info(
            "bulk_create: completed — %d/%d rows inserted into %s",
            len(created),
            total,
            model_class.__tablename__,
        )
        return created

    # ------------------------------------------------------------------
    # bulk_update
    # ------------------------------------------------------------------

    async def bulk_update(
        self,
        model_class: type,
        items: list[dict[str, Any]],
        *,
        key_field: str = "id",
        batch_size: int | None = None,
        session: AsyncSession | Any | None = None,
    ) -> int:
        """Update rows matching *key_field* with the remaining dict values.

        Each dict in *items* **must** contain the *key_field*.  The other
        key/value pairs are set on the matched row.

        Returns the total number of rows updated.
        """
        if not items:
            return 0

        batch_size = batch_size or self.default_batch_size
        sess = self._resolve_session(session)
        is_async = self._is_async_session(sess)
        updated_count = 0
        total = len(items)

        logger.debug(
            "bulk_update: updating %d rows in %s by %s (batch_size=%d)",
            total,
            model_class.__tablename__,
            key_field,
            batch_size,
        )

        key_col = getattr(model_class, key_field)

        for idx, batch in enumerate(chunked(items, batch_size), start=1):
            try:
                for row_dict in batch:
                    row_dict = dict(row_dict)  # avoid mutating caller's data
                    key_value = row_dict.pop(key_field)
                    if not row_dict:
                        continue
                    stmt = (
                        update(model_class)
                        .where(key_col == key_value)
                        .values(**row_dict)
                    )
                    if is_async:
                        result = await sess.execute(stmt)
                    else:
                        result = sess.execute(stmt)
                    updated_count += result.rowcount
                logger.debug(
                    "bulk_update: batch %d — processed %d items", idx, len(batch)
                )
            except Exception:
                logger.exception(
                    "bulk_update: batch %d failed (%d items)", idx, len(batch)
                )
                raise

        logger.info(
            "bulk_update: completed — %d rows updated in %s",
            updated_count,
            model_class.__tablename__,
        )
        return updated_count

    # ------------------------------------------------------------------
    # bulk_delete
    # ------------------------------------------------------------------

    async def bulk_delete(
        self,
        model_class: type,
        ids: list[Any],
        *,
        key_field: str = "id",
        batch_size: int | None = None,
        session: AsyncSession | Any | None = None,
    ) -> int:
        """Delete rows whose *key_field* is in *ids*.

        Splits into batches to stay within database parameter-count limits.
        Returns the total number of rows deleted.
        """
        if not ids:
            return 0

        batch_size = batch_size or self.default_batch_size
        sess = self._resolve_session(session)
        is_async = self._is_async_session(sess)
        deleted_count = 0
        total = len(ids)

        logger.debug(
            "bulk_delete: deleting up to %d rows from %s by %s (batch_size=%d)",
            total,
            model_class.__tablename__,
            key_field,
            batch_size,
        )

        key_col = getattr(model_class, key_field)

        for idx, batch_ids in enumerate(chunked(ids, batch_size), start=1):
            try:
                stmt = delete(model_class).where(key_col.in_(batch_ids))
                if is_async:
                    result = await sess.execute(stmt)
                else:
                    result = sess.execute(stmt)
                deleted_count += result.rowcount
                logger.debug(
                    "bulk_delete: batch %d — deleted %d rows",
                    idx,
                    result.rowcount,
                )
            except Exception:
                logger.exception(
                    "bulk_delete: batch %d failed (%d ids)", idx, len(batch_ids)
                )
                raise

        logger.info(
            "bulk_delete: completed — %d/%d rows deleted from %s",
            deleted_count,
            total,
            model_class.__tablename__,
        )
        return deleted_count

    # ------------------------------------------------------------------
    # bulk_upsert
    # ------------------------------------------------------------------

    async def bulk_upsert(
        self,
        model_class: type,
        items: list[dict[str, Any]],
        *,
        key_fields: list[str],
        batch_size: int | None = None,
        session: AsyncSession | Any | None = None,
    ) -> int:
        """Upsert rows using ``INSERT ... ON CONFLICT DO UPDATE`` (PostgreSQL).

        *key_fields* specifies the column(s) that form the unique constraint
        used to detect conflicts.  Non-key columns are updated on conflict.

        Returns the total number of affected rows (inserted + updated).
        """
        if not items:
            return 0

        batch_size = batch_size or self.default_batch_size
        sess = self._resolve_session(session)
        is_async = self._is_async_session(sess)
        affected_count = 0
        total = len(items)

        logger.debug(
            "bulk_upsert: upserting %d rows into %s on %s (batch_size=%d)",
            total,
            model_class.__tablename__,
            key_fields,
            batch_size,
        )

        for idx, batch in enumerate(chunked(items, batch_size), start=1):
            try:
                stmt = pg_insert(model_class).values(batch)
                # Determine columns to update on conflict — everything except
                # the conflict key columns themselves.
                all_columns = {c.name for c in inspect(model_class).columns}
                update_cols = all_columns - set(key_fields)
                if update_cols:
                    set_clause = {
                        col: stmt.excluded[col] for col in update_cols
                    }
                    stmt = stmt.on_conflict_do_update(
                        index_elements=key_fields,
                        set_=set_clause,
                    )
                else:
                    # Nothing to update — just ignore conflicts.
                    stmt = stmt.on_conflict_do_nothing(
                        index_elements=key_fields,
                    )

                if is_async:
                    result = await sess.execute(stmt)
                else:
                    result = sess.execute(stmt)
                affected_count += result.rowcount
                logger.debug(
                    "bulk_upsert: batch %d — affected %d rows",
                    idx,
                    result.rowcount,
                )
            except Exception:
                logger.exception(
                    "bulk_upsert: batch %d failed (%d items)", idx, len(batch)
                )
                raise

        logger.info(
            "bulk_upsert: completed — %d rows affected in %s",
            affected_count,
            model_class.__tablename__,
        )
        return affected_count

    # ------------------------------------------------------------------
    # bulk_operation (convenience wrapper with BulkResult tracking)
    # ------------------------------------------------------------------

    async def bulk_operation(
        self,
        *,
        model_class: type,
        create: list[dict[str, Any]] | None = None,
        update_items: list[dict[str, Any]] | None = None,
        delete_ids: list[Any] | None = None,
        key_field: str = "id",
        batch_size: int | None = None,
        session: AsyncSession | Any | None = None,
    ) -> BulkResult:
        """Run multiple bulk operations and return a unified :class:`BulkResult`.

        This is a convenience wrapper that calls :meth:`bulk_create`,
        :meth:`bulk_update`, and :meth:`bulk_delete` as needed, collecting
        results and timing information.

        Any individual operation that fails is recorded in
        ``result.failed_items`` and ``result.errors`` — the remaining
        operations still execute.
        """
        result = BulkResult()
        t0 = time.monotonic()

        if create:
            try:
                created = await self.bulk_create(
                    model_class,
                    create,
                    batch_size=batch_size,
                    session=session,
                )
                result.created = len(created)
            except Exception as exc:
                result.errors += 1
                result.failed_items.append(
                    {"operation": "create", "count": len(create), "error": str(exc)}
                )
                logger.exception("bulk_operation: create step failed")

        if update_items:
            try:
                result.updated = await self.bulk_update(
                    model_class,
                    update_items,
                    key_field=key_field,
                    batch_size=batch_size,
                    session=session,
                )
            except Exception as exc:
                result.errors += 1
                result.failed_items.append(
                    {
                        "operation": "update",
                        "count": len(update_items),
                        "error": str(exc),
                    }
                )
                logger.exception("bulk_operation: update step failed")

        if delete_ids:
            try:
                result.deleted = await self.bulk_delete(
                    model_class,
                    delete_ids,
                    key_field=key_field,
                    batch_size=batch_size,
                    session=session,
                )
            except Exception as exc:
                result.errors += 1
                result.failed_items.append(
                    {
                        "operation": "delete",
                        "count": len(delete_ids),
                        "error": str(exc),
                    }
                )
                logger.exception("bulk_operation: delete step failed")

        result.duration_ms = (time.monotonic() - t0) * 1000
        logger.info("bulk_operation: %r", result)
        return result
