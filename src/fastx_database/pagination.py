"""Cursor-based and offset-based pagination utilities.

Provides pagination models and repository mixins for SQLAlchemy async
sessions.  Cursor-based pagination avoids the performance pitfalls of
``OFFSET`` by filtering on an indexed column, making it suitable for
large datasets and infinite-scroll UIs.

Example (cursor)::

    class UserRepository(CursorPaginationMixin):
        def __init__(self, session: AsyncSession) -> None:
            self.session = session

        async def list_users(self, cursor: str | None = None) -> CursorPage:
            query = select(User).where(User.is_active.is_(True))
            return await self.paginate_cursor(query, limit=25, cursor=cursor)

Example (offset)::

    class UserRepository(OffsetPaginationMixin):
        def __init__(self, session: AsyncSession) -> None:
            self.session = session

        async def list_users(self, page: int = 1) -> OffsetPage:
            query = select(User).where(User.is_active.is_(True))
            return await self.paginate_offset(query, page=page, page_size=25)
"""

from __future__ import annotations

import base64
import math
from dataclasses import dataclass, field
from typing import Any, Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def encode_cursor(value: Any) -> str:
    """Base64-encode a cursor value for safe transport in URLs/headers.

    The value is first converted to a string, then encoded with
    URL-safe base64 (no padding).

    Args:
        value: The column value to encode (e.g. an ``id`` integer or a
            timestamp string).

    Returns:
        A URL-safe base64-encoded string.
    """
    raw = str(value).encode("utf-8")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def decode_cursor(cursor: str) -> str:
    """Decode a base64-encoded cursor back to its original string value.

    Args:
        cursor: The base64-encoded cursor string produced by
            :func:`encode_cursor`.

    Returns:
        The decoded string value.

    Raises:
        ValueError: If *cursor* is not valid base64.
    """
    # Re-add padding stripped by encode_cursor.
    padded = cursor + "=" * (-len(cursor) % 4)
    try:
        return base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
    except Exception as exc:
        raise ValueError(f"Invalid cursor: {cursor!r}") from exc


# ---------------------------------------------------------------------------
# Page models
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CursorPage:
    """A page of results obtained via cursor-based pagination.

    Attributes:
        items: The rows for the current page.
        next_cursor: An opaque cursor pointing to the *next* page, or
            ``None`` if there is no next page.
        prev_cursor: An opaque cursor pointing to the *previous* page,
            or ``None`` if there is no previous page.
        has_next: Whether more rows exist after this page.
        has_prev: Whether more rows exist before this page.
        total: The total number of rows matching the base query.  This
            is ``None`` by default because computing ``COUNT(*)`` can be
            expensive on large tables.
    """

    items: list[Any] = field(default_factory=list)
    next_cursor: str | None = None
    prev_cursor: str | None = None
    has_next: bool = False
    has_prev: bool = False
    total: int | None = None


@dataclass(frozen=True, slots=True)
class OffsetPage:
    """A page of results obtained via traditional offset-based pagination.

    Attributes:
        items: The rows for the current page.
        total: Total number of rows matching the base query.
        page: The 1-based page number.
        page_size: Maximum number of items per page.
        total_pages: The total number of pages.
        has_next: Whether a subsequent page exists.
        has_prev: Whether a preceding page exists.
    """

    items: list[Any] = field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False


# ---------------------------------------------------------------------------
# Mixins
# ---------------------------------------------------------------------------


class CursorPaginationMixin:
    """Async repository mixin providing cursor-based pagination.

    The consuming class **must** expose a ``session`` attribute that is
    an :class:`~sqlalchemy.ext.asyncio.AsyncSession`.

    Cursor pagination works by remembering the ordering-column value of
    the last (or first) row on the current page and using a ``WHERE``
    filter (``>`` or ``<``) to fetch the next (or previous) slice.  This
    is far more efficient than ``OFFSET`` for large tables with an
    appropriate index on the ordering column.
    """

    session: AsyncSession

    async def paginate_cursor(
        self,
        query: Select,
        *,
        limit: int = 20,
        cursor: str | None = None,
        order_by: str = "id",
        direction: str = "after",
        include_total: bool = False,
    ) -> CursorPage:
        """Return a :class:`CursorPage` for *query*.

        Args:
            query: A SQLAlchemy ``Select`` statement.  The mixin will
                add ordering, filtering, and limit clauses — callers
                should **not** apply those themselves.
            limit: Maximum number of items to return per page.
            cursor: An opaque cursor string produced by a previous call.
                ``None`` fetches the first page.
            order_by: The name of the column to order by.  The column
                **must** exist on the first entity in the query's column
                list and should be indexed for best performance.
            direction: ``"after"`` for forward pagination (rows *after*
                the cursor) or ``"before"`` for backward pagination
                (rows *before* the cursor).
            include_total: If ``True``, run an additional ``COUNT``
                query to populate :attr:`CursorPage.total`.  Defaults to
                ``False`` because the count can be expensive.

        Returns:
            A :class:`CursorPage` with up to *limit* items.

        Raises:
            ValueError: If *direction* is not ``"after"`` or
                ``"before"``, or if the ordering column cannot be
                resolved.
        """
        if direction not in ("after", "before"):
            raise ValueError(
                f"direction must be 'after' or 'before', got {direction!r}"
            )

        # Resolve the ordering column from the query's primary entity.
        entity = _resolve_entity(query)
        order_col = getattr(entity, order_by, None)
        if order_col is None:
            raise ValueError(
                f"Column {order_by!r} not found on {entity.__name__}"
            )

        # -----------------------------------------------------------------
        # Optional total count
        # -----------------------------------------------------------------
        total: int | None = None
        if include_total:
            count_q = select(func.count()).select_from(query.subquery())
            result = await self.session.execute(count_q)
            total = result.scalar_one()

        # -----------------------------------------------------------------
        # Apply cursor filter
        # -----------------------------------------------------------------
        has_prev = False
        if cursor is not None:
            cursor_value = decode_cursor(cursor)
            if direction == "after":
                query = query.where(order_col > cursor_value)
            else:
                query = query.where(order_col < cursor_value)

        # -----------------------------------------------------------------
        # Ordering
        # -----------------------------------------------------------------
        if direction == "after":
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())

        # Fetch one extra row to determine whether more pages exist.
        query = query.limit(limit + 1)

        result = await self.session.execute(query)
        rows: Sequence[Any] = result.scalars().all()

        # -----------------------------------------------------------------
        # Determine has_next / has_prev and trim the extra sentinel row.
        # -----------------------------------------------------------------
        if direction == "after":
            has_next = len(rows) > limit
            items = list(rows[:limit])
            has_prev = cursor is not None
        else:
            has_next = cursor is not None
            has_prev = len(rows) > limit
            items = list(rows[:limit])
            # Reverse so items are in ascending order regardless of
            # the direction the user paginated.
            items.reverse()

        # -----------------------------------------------------------------
        # Build cursors
        # -----------------------------------------------------------------
        next_cursor: str | None = None
        prev_cursor: str | None = None

        if items:
            if has_next:
                last_value = getattr(items[-1], order_by)
                next_cursor = encode_cursor(last_value)
            if has_prev:
                first_value = getattr(items[0], order_by)
                prev_cursor = encode_cursor(first_value)

        return CursorPage(
            items=items,
            next_cursor=next_cursor,
            prev_cursor=prev_cursor,
            has_next=has_next,
            has_prev=has_prev,
            total=total,
        )


class OffsetPaginationMixin:
    """Async repository mixin providing offset-based pagination.

    The consuming class **must** expose a ``session`` attribute that is
    an :class:`~sqlalchemy.ext.asyncio.AsyncSession`.

    Offset pagination is simpler to reason about but can degrade on
    large tables because the database must skip *offset* rows before
    returning results.  Prefer :class:`CursorPaginationMixin` when
    performance on deep pages matters.
    """

    session: AsyncSession

    async def paginate_offset(
        self,
        query: Select,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> OffsetPage:
        """Return an :class:`OffsetPage` for *query*.

        Args:
            query: A SQLAlchemy ``Select`` statement.  The mixin will
                add ``LIMIT`` and ``OFFSET`` — callers should **not**
                apply those themselves.
            page: The 1-based page number to retrieve.
            page_size: Maximum number of items per page.

        Returns:
            An :class:`OffsetPage` with up to *page_size* items.

        Raises:
            ValueError: If *page* or *page_size* is less than 1.
        """
        if page < 1:
            raise ValueError(f"page must be >= 1, got {page}")
        if page_size < 1:
            raise ValueError(f"page_size must be >= 1, got {page_size}")

        # Total count
        count_q = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_q)
        total: int = count_result.scalar_one()

        total_pages = max(1, math.ceil(total / page_size))

        # Data query
        offset = (page - 1) * page_size
        data_q = query.limit(page_size).offset(offset)
        data_result = await self.session.execute(data_q)
        items = list(data_result.scalars().all())

        return OffsetPage(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_entity(query: Select) -> Any:
    """Extract the primary mapped entity from a ``Select`` statement.

    Works for queries built via ``select(MyModel)`` or
    ``select(MyModel.col1, MyModel.col2)``.

    Raises:
        ValueError: If the entity cannot be determined.
    """
    # query.column_descriptions is a list of dicts; the first entry's
    # "entity" key holds the mapped class (or None for raw columns).
    for desc in query.column_descriptions:
        entity = desc.get("entity")
        if entity is not None:
            return entity
    raise ValueError(
        "Could not resolve a mapped entity from the query. "
        "Ensure the query selects from a mapped ORM class."
    )
