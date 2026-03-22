"""
Reusable SQLAlchemy declarative mixins (timestamps, UUID PK, soft-delete, tenant scope,
optimistic locking, audit actor FKs).

Use with the package :class:`fast_database.models.Base`::

    from fast_database import Base
    from fast_database.mixins import TimestampMixin, UUIDPrimaryKeyMixin

    class Item(Base, UUIDPrimaryKeyMixin, TimestampMixin):
        __tablename__ = "items"
        name = Column(String(255), nullable=False)

**Mixin order:** put ``Base`` first, then mixins, then your columns.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, Uuid, text

from fast_database.constants.db.table import Table


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    """``created_at`` / ``updated_at`` with UTC-aware datetimes."""

    __abstract__ = True

    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=_utc_now)


class UUIDPrimaryKeyMixin:
    """Primary key ``id`` as UUID (SQLAlchemy :class:`Uuid` type)."""

    __abstract__ = True

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)


class OrganizationScopedMixin:
    """
    ``organization_id`` FK to :class:`~fast_database.models.organization.Organization`.

    Use for tenant-scoped rows. Add a composite index in ``__table_args__`` for
    common queries (see package README).
    """

    __abstract__ = True

    organization_id = Column(
        BigInteger,
        ForeignKey(f"{Table.ORGANIZATION}.id"),
        nullable=False,
        index=True,
    )


class TenantIdMixin:
    """
    Generic ``tenant_id`` (no FK) for multi-tenant discrimination.

    Prefer :class:`OrganizationScopedMixin` when the tenant is an organization row.
    """

    __abstract__ = True

    tenant_id = Column(BigInteger, nullable=False, index=True)


class OptimisticLockMixin:
    """
    Integer ``version`` for optimistic concurrency.

    Wire the mapper with :func:`sqlalchemy.orm.declared_attr`::

        from sqlalchemy.orm import declared_attr

        class Item(Base, OptimisticLockMixin):
            __tablename__ = "items"
            id = Column(Integer, primary_key=True)

            @declared_attr
            def __mapper_args__(cls):
                return {"version_id_col": cls.version}
    """

    __abstract__ = True

    version = Column(Integer, nullable=False, default=1, server_default=text("1"))


class AuditActorMixin:
    """
    Optional ``created_by_id`` / ``updated_by_id`` FK to ``user.id``.

    Nullable so inserts can omit actor; services set IDs from the current user.
    """

    __abstract__ = True

    created_by_id = Column(BigInteger, ForeignKey("user.id"), nullable=True, index=True)
    updated_by_id = Column(BigInteger, ForeignKey("user.id"), nullable=True, index=True)


class SoftDeleteMixin:
    """
    ``is_deleted`` flag and optional ``deleted_at`` for soft-delete rows.

    Existing models (e.g. :class:`~fast_database.models.user.User`) may define
    only ``is_deleted``; new tables can use this mixin for both columns and use
    helpers in :mod:`fast_database.soft_delete`.
    """

    __abstract__ = True

    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
