"""fastx_database.
==================

Shared SQLAlchemy ORM models intended to be reused across multiple apps.

The canonical declarative `Base` is exposed here for convenience:
`from fastx_database import Base`.

Mixins, soft-delete, optimistic locking, and soft-delete helpers::

    from fastx_database import Base, TimestampMixin, SoftDeleteMixin, OrganizationScopedMixin
    from fastx_database.core.soft_delete import select_active, mark_soft_deleted
"""

__version__ = "1.6.0"

from fastx_database.persistence.models import Base
from fastx_database.core.mixins import (
    AuditActorMixin,
    OptimisticLockMixin,
    OrganizationScopedMixin,
    SoftDeleteMixin,
    TenantIdMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

# Model migrations - imported when models are imported
from fastx_database.migrations import (
    ModelMigration,
    get_model_migration,
    get_registered_models,
    register_model_migration,
    run_model_migrations,
)
from fastx_database.core.optimistic_lock import (
    StaleVersionError,
    assert_version_matches,
    expected_version,
)
from fastx_database.core.soft_delete import (
    filter_active,
    filter_not_deleted,
    mark_soft_deleted,
    restore_soft_deleted,
    select_active,
    SoftDeleteQuery,
    SoftDeleteRepositoryMixin,
    where_not_deleted,
)

__all__ = [
    # Mixins
    "AuditActorMixin",
    "Base",
    "OptimisticLockMixin",
    "OrganizationScopedMixin",
    "StaleVersionError",
    "SoftDeleteMixin",
    "TenantIdMixin",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    # Soft delete helpers
    "assert_version_matches",
    "expected_version",
    "where_not_deleted",
    "select_active",
    "mark_soft_deleted",
    "restore_soft_deleted",
    "filter_active",
    "filter_not_deleted",
    "SoftDeleteQuery",
    "SoftDeleteRepositoryMixin",
    # Migrations
    "ModelMigration",
    "get_model_migration",
    "get_registered_models",
    "register_model_migration",
    "run_model_migrations",
]
