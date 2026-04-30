"""Core Mixins for Fast Database Models.

Provides reusable mixins for common model patterns like lookup tables,
timestamp handling, and serialization.

This module follows DRY principles to eliminate code duplication across
model definitions.

Example:
    >>> from fastx_database.core.mixins import LookupModelMixin
    >>> from fastx_database.persistence.models import Base
    >>>
    >>> class StatusLk(Base, LookupModelMixin):
    ...     __tablename__ = "status_lk"
    ...     # id, urn, code, description, created_at, updated_at are provided
    ...     # to_dict() method is provided

"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String

from fastx_database.core.constants.db import StringLength, SoftDeleteFlag


class LookupModelMixin:
    """Mixin for lookup table models with standard schema.

    Provides common lookup table columns:
    - id: Primary key (BigInteger, autoincrement)
    - urn: Unique Resource Name (String 128, unique, indexed)
    - code: Unique code (String 64, unique, indexed)
    - description: Human-readable label (String 255)
    - created_at: Timestamp (DateTime, not null, default utcnow)
    - updated_at: Timestamp (DateTime, nullable, onupdate utcnow)

    Also provides a standard to_dict() serialization method.

    Attributes:
        id (int): Primary key
        urn (str): Unique Resource Name
        code (str): Unique code for business logic
        description (str): Human-readable description
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp

    Example:
        >>> from fastx_database.persistence.models import Base
        >>> from fastx_database.core.mixins import LookupModelMixin
        >>> from fastx_database.core.constants.table import Table
        >>>
        >>> class StatusLk(Base, LookupModelMixin):
        ...     __tablename__ = Table.STATUS_LK
        ...     # All columns and methods provided by mixin
        ...     pass
        >>>
        >>> status = StatusLk(urn="urn:status:active", code="active", description="Active")
        >>> status.to_dict()
        {'urn': 'urn:status:active', 'code': 'active', 'description': 'Active',
         'created_at': '2024-01-01T00:00:00', 'updated_at': None}

    """

    # Primary key
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Unique identifiers
    urn = Column(String(StringLength.URN), nullable=False, unique=True, index=True)
    code = Column(String(StringLength.CODE), nullable=False, unique=True, index=True)

    # Description
    description = Column(String(StringLength.NAME), nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow
    )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the lookup record to a dictionary.

        Returns:
            Dictionary with urn, code, description, created_at, updated_at.
            Datetimes are ISO-formatted strings.

        Example:
            >>> status = StatusLk(urn="urn:status:active", code="active",
            ...                   description="Active status")
            >>> status.to_dict()
            {'urn': 'urn:status:active', 'code': 'active',
             'description': 'Active status', 'created_at': '2024-01-01T00:00:00',
             'updated_at': None}

        """
        return {
            "urn": self.urn,
            "code": self.code,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TimestampMixin:
    """Mixin for models requiring created_at and updated_at timestamps.

    Provides:
    - created_at: Timestamp (DateTime, not null, default utcnow)
    - updated_at: Timestamp (DateTime, nullable, onupdate utcnow)

    Example:
        >>> from fastx_database.persistence.models import Base
        >>> from fastx_database.core.mixins import TimestampMixin
        >>>
        >>> class MyModel(Base, TimestampMixin):
        ...     __tablename__ = "my_model"
        ...     # created_at and updated_at columns provided

    """

    __abstract__ = True

    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow
    )


class URNMixin:
    """Mixin for models requiring a URN (Unique Resource Name).

    Provides:
    - urn: Unique Resource Name (String 128, unique, indexed)

    Example:
        >>> from fastx_database.persistence.models import Base
        >>> from fastx_database.core.mixins import URNMixin
        >>>
        >>> class MyModel(Base, URNMixin):
        ...     __tablename__ = "my_model"
        ...     # urn column provided

    """

    urn = Column(String(StringLength.URN), nullable=False, unique=True, index=True)


class SoftDeleteMixin:
    """Mixin for models requiring soft delete functionality.

    Provides:
    - is_deleted: Boolean flag as String(1) (default 'N')
    - deleted_at: Timestamp when deleted (nullable)
    - delete() / restore() / force_delete() methods
    - Query filtering helpers

    Example:
        >>> from fastx_database.persistence.models import Base
        >>> from fastx_database.core.mixins import SoftDeleteMixin
        >>>
        >>> class MyModel(Base, SoftDeleteMixin):
        ...     __tablename__ = "my_model"
        ...     # is_deleted and deleted_at columns provided
        >>>
        >>> item = MyModel(name="Test")
        >>> item.delete()  # Soft delete
        >>> db.commit()
        >>>
        >>> item.restore()  # Restore
        >>> db.commit()

    """

    __abstract__ = True

    is_deleted = Column(
        "is_deleted", type_=String(StringLength.SOFT_DELETE_FLAG), nullable=False, default=SoftDeleteFlag.NO, server_default=SoftDeleteFlag.NO
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def delete(self) -> None:
        """Soft delete the record.

        Sets deleted_at timestamp and is_deleted flag.
        Does not actually remove from database.
        """
        from datetime import datetime

        self.deleted_at = datetime.utcnow()
        self.is_deleted = SoftDeleteFlag.YES

    def restore(self) -> None:
        """Restore a soft-deleted record.

        Clears deleted_at timestamp and is_deleted flag.
        """
        self.deleted_at = None
        self.is_deleted = SoftDeleteFlag.NO

    def force_delete(self) -> None:
        """Actually delete the record from database.

        Use with caution - this permanently removes data.
        Must be overridden or use db.delete(obj).
        """
        raise NotImplementedError(
            "force_delete must be implemented by the model or use db.delete(obj)"
        )


class AuditActorMixin:
    """Mixin for models requiring audit tracking (created_by_id, updated_by_id).

    Provides:
    - created_by_id: User ID who created the record
    - updated_by_id: User ID who last updated the record

    Example:
        >>> from fastx_database.persistence.models import Base
        >>> from fastx_database.core.mixins import AuditActorMixin
        >>>
        >>> class MyModel(Base, AuditActorMixin):
        ...     __tablename__ = "my_model"
        ...     # created_by_id and updated_by_id columns provided

    """

    created_by_id = Column(BigInteger, nullable=True)
    updated_by_id = Column(BigInteger, nullable=True)


class UUIDPrimaryKeyMixin:
    """Mixin for models using UUID as primary key.

    Provides:
    - id: UUID primary key

    Example:
        >>> from fastx_database.persistence.models import Base
        >>> from fastx_database.core.mixins import UUIDPrimaryKeyMixin
        >>>
        >>> class MyModel(Base, UUIDPrimaryKeyMixin):
        ...     __tablename__ = "my_model"
        ...     # UUID id column provided

    """

    __abstract__ = True

    id = Column(String(StringLength.UUID), primary_key=True)


class TenantIdMixin:
    """Mixin for multi-tenant models requiring tenant_id.

    Provides:
    - tenant_id: Tenant identifier column

    Example:
        >>> from fastx_database.persistence.models import Base
        >>> from fastx_database.core.mixins import TenantIdMixin
        >>>
        >>> class MyModel(Base, TenantIdMixin):
        ...     __tablename__ = "my_model"
        ...     # tenant_id column provided

    """

    tenant_id = Column(BigInteger, nullable=False, index=True)


class OrganizationScopedMixin:
    """Mixin for models scoped to an organization.

    Provides:
    - organization_id: Organization identifier column with foreign key to organizations

    Example:
        >>> from fastx_database.persistence.models import Base
        >>> from fastx_database.core.mixins import OrganizationScopedMixin
        >>>
        >>> class MyModel(Base, OrganizationScopedMixin):
        ...     __tablename__ = "my_model"
        ...     # organization_id column with FK provided

    """

    organization_id = Column(
        BigInteger, ForeignKey("organizations.id"), nullable=False, index=True
    )


class OptimisticLockMixin:
    """Mixin for optimistic locking support.

    Provides:
    - version: Version number for optimistic locking

    Example:
        >>> from fastx_database.persistence.models import Base
        >>> from fastx_database.core.mixins import OptimisticLockMixin
        >>>
        >>> class MyModel(Base, OptimisticLockMixin):
        ...     __tablename__ = "my_model"
        ...     # version column provided for optimistic locking

    """

    version = Column(BigInteger, nullable=False, default=0)
