"""
fastmvc_db_models
==================

Shared SQLAlchemy ORM models intended to be reused across multiple apps.

The canonical declarative `Base` is exposed here for convenience:
`from fastmvc_db_models import Base`.

Mixins, soft-delete, optimistic locking, and soft-delete helpers::

    from fastmvc_db_models import Base, TimestampMixin, SoftDeleteMixin, OrganizationScopedMixin
    from fastmvc_db_models.soft_delete import select_active, mark_soft_deleted
"""

from src.models import Base
from src.mixins import (
    AuditActorMixin,
    OptimisticLockMixin,
    OrganizationScopedMixin,
    SoftDeleteMixin,
    TenantIdMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)
from src.optimistic_lock import (
    StaleVersionError,
    assert_version_matches,
    expected_version,
)
from src.soft_delete import (
    filter_active,
    mark_soft_deleted,
    restore_soft_deleted,
    select_active,
    where_not_deleted,
)

__all__ = [
    "AuditActorMixin",
    "Base",
    "OptimisticLockMixin",
    "OrganizationScopedMixin",
    "StaleVersionError",
    "SoftDeleteMixin",
    "TenantIdMixin",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    "assert_version_matches",
    "expected_version",
    "where_not_deleted",
    "select_active",
    "mark_soft_deleted",
    "restore_soft_deleted",
    "filter_active",
]
