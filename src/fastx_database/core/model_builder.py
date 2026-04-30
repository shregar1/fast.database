"""Generic Model Builder for Fast Database.

Provides a flexible, configurable system for creating SQLAlchemy models
with customizable columns, mixins, and features.

Example:
    >>> from fastx_database.core.model_builder import ModelBuilder, ColumnConfig
    >>> 
    >>> # Build a custom user model
    >>> User = ModelBuilder("User", "users")\
    ...     .with_id()\
    ...     .with_column("email", String(255), unique=True, nullable=False)\
    ...     .with_column("name", String(100), nullable=True)\
    ...     .with_timestamps()\
    ...     .with_soft_delete()\
    ...     .build()
    >>> 
    >>> # Use the model
    >>> user = User(email="test@example.com", name="Test User")

"""

from __future__ import annotations

import inspect
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, TypeVar

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declared_attr

from fastx_database.persistence.models import Base
from fastx_database.core.constants.db import (
    StringLength,
    SoftDeleteFlag,
    ServerDefault,
    DEFAULT_VERSION,
)


@dataclass
class ColumnConfig:
    """Configuration for a model column."""

    name: str
    type_: Any
    nullable: bool = True
    unique: bool = False
    index: bool = False
    primary_key: bool = False
    default: Any = None
    server_default: Any = None
    foreign_key: str | None = None
    doc: str = ""

    def to_column(self) -> Column:
        """Convert config to SQLAlchemy Column."""
        kwargs = {
            "nullable": self.nullable,
            "unique": self.unique,
            "index": self.index,
            "default": self.default,
            "server_default": self.server_default,
            "doc": self.doc,
        }

        if self.primary_key:
            kwargs["primary_key"] = True
            kwargs["autoincrement"] = True

        if self.foreign_key:
            return Column(self.name, self.type_, ForeignKey(self.foreign_key), **kwargs)

        return Column(self.name, self.type_, **kwargs)


@dataclass
class IndexConfig:
    """Configuration for a table index."""

    name: str
    columns: list[str]
    unique: bool = False


@dataclass
class ModelConfig:
    """Complete model configuration."""

    name: str
    table_name: str
    columns: dict[str, ColumnConfig] = field(default_factory=dict)
    indexes: list[IndexConfig] = field(default_factory=list)
    mixins: list[type] = field(default_factory=list)
    features: dict[str, bool] = field(default_factory=dict)
    extra_attributes: dict[str, Any] = field(default_factory=dict)

    def copy(self) -> ModelConfig:
        """Create a deep copy of the config."""
        return deepcopy(self)


class ModelBuilder:
    """Fluent builder for creating customizable SQLAlchemy models.
    
    Allows fine-grained control over model columns, indexes, mixins,
    and features through a chainable API.
    
    Example:
        >>> Product = ModelBuilder("Product", "products")\
        ...     .with_id()\
        ...     .with_urn()\
        ...     .with_column("sku", String(50), unique=True, nullable=False)\
        ...     .with_column("price", Numeric(10, 2), default=0)\
        ...     .with_timestamps()\
        ...     .with_audit()\
        ...     .with_soft_delete()\
        ...     .with_index("idx_price", ["price"])\
        ...     .build()

    """

    def __init__(self, name: str, table_name: str | None = None):
        """Initialize the model builder.

        Args:
            name: Model class name
            table_name: Database table name (defaults to snake_case of name)

        """
        self.config = ModelConfig(
            name=name,
            table_name=table_name or self._to_snake_case(name),
        )

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert CamelCase to snake_case."""
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    # ==================== Standard Columns ====================

    def with_id(self, column_name: str = "id", type_: Any = BigInteger) -> ModelBuilder:
        """Add auto-incrementing primary key."""
        self.config.columns[column_name] = ColumnConfig(
            name=column_name,
            type_=type_,
            primary_key=True,
            nullable=False,
            doc="Primary key",
        )
        return self

    def with_uuid_id(self, column_name: str = "id") -> ModelBuilder:
        """Add UUID primary key."""
        self.config.columns[column_name] = ColumnConfig(
            name=column_name,
            type_=String(StringLength.UUID),
            primary_key=True,
            nullable=False,
            doc="UUID primary key",
        )
        return self

    def with_urn(
        self, length: int = 128, unique: bool = True, index: bool = True
    ) -> ModelBuilder:
        """Add URN (Unique Resource Name) column."""
        self.config.columns["urn"] = ColumnConfig(
            name="urn",
            type_=String(StringLength.URN if length == 128 else length),
            nullable=False,
            unique=unique,
            index=index,
            doc="Unique Resource Name",
        )
        return self

    def with_code(
        self, length: int = 64, unique: bool = True, index: bool = True
    ) -> ModelBuilder:
        """Add business code column."""
        self.config.columns["code"] = ColumnConfig(
            name="code",
            type_=String(StringLength.CODE if length == 64 else length),
            nullable=False,
            unique=unique,
            index=index,
            doc="Business code",
        )
        return self

    def with_name(
        self, length: int = 255, nullable: bool = False, index: bool = False
    ) -> ModelBuilder:
        """Add name column."""
        self.config.columns["name"] = ColumnConfig(
            name="name",
            type_=String(StringLength.NAME if length == 255 else length),
            nullable=nullable,
            index=index,
            doc="Display name",
        )
        return self

    def with_description(
        self, length: int = 500, nullable: bool = True
    ) -> ModelBuilder:
        """Add description column."""
        self.config.columns["description"] = ColumnConfig(
            name="description",
            type_=Text if length > 255 else String(length),
            nullable=nullable,
            doc="Description",
        )
        return self

    def with_email(
        self, unique: bool = True, index: bool = True, nullable: bool = False
    ) -> ModelBuilder:
        """Add email column."""
        self.config.columns["email"] = ColumnConfig(
            name="email",
            type_=String(StringLength.EMAIL),
            nullable=nullable,
            unique=unique,
            index=index,
            doc="Email address",
        )
        return self

    def with_phone(
        self, unique: bool = True, index: bool = True, nullable: bool = True
    ) -> ModelBuilder:
        """Add phone column."""
        self.config.columns["phone"] = ColumnConfig(
            name="phone",
            type_=String(StringLength.PHONE),
            nullable=nullable,
            unique=unique,
            index=index,
            doc="Phone number",
        )
        return self

    def with_password(self, length: int = 255) -> ModelBuilder:
        """Add password hash column."""
        self.config.columns["password"] = ColumnConfig(
            name="password", type_=String(StringLength.PASSWORD if length == 255 else length), nullable=False, doc="Password hash"
        )
        return self

    def with_status(self, default: str = "active") -> ModelBuilder:
        """Add status column."""
        self.config.columns["status"] = ColumnConfig(
            name="status",
            type_=String(StringLength.STATUS),
            nullable=False,
            default=default,
            server_default=default,
            index=True,
            doc="Status",
        )
        return self

    def with_boolean(
        self, name: str, default: bool = False, nullable: bool = False
    ) -> ModelBuilder:
        """Add boolean flag column."""
        self.config.columns[name] = ColumnConfig(
            name=name,
            type_=Boolean,
            nullable=nullable,
            default=default,
            server_default=ServerDefault.TRUE if default else ServerDefault.FALSE,
            doc=f"{name} flag",
        )
        return self

    def with_foreign_key(
        self,
        name: str,
        target: str,
        type_: Any = BigInteger,
        nullable: bool = False,
        index: bool = True,
    ) -> ModelBuilder:
        """Add foreign key column."""
        self.config.columns[name] = ColumnConfig(
            name=name,
            type_=type_,
            nullable=nullable,
            index=index,
            foreign_key=target,
            doc=f"Foreign key to {target}",
        )
        return self

    # ==================== Feature Mixins ====================

    def with_timestamps(self) -> ModelBuilder:
        """Add created_at and updated_at timestamps."""
        self.config.columns["created_at"] = ColumnConfig(
            name="created_at",
            type_=DateTime(timezone=True),
            nullable=False,
            default=datetime.utcnow,
            doc="Creation timestamp",
        )
        self.config.columns["updated_at"] = ColumnConfig(
            name="updated_at",
            type_=DateTime(timezone=True),
            nullable=True,
            onupdate=datetime.utcnow,
            doc="Last update timestamp",
        )
        self.config.features["timestamps"] = True
        return self

    def with_soft_delete(self) -> ModelBuilder:
        """Add soft delete columns."""
        self.config.columns["is_deleted"] = ColumnConfig(
            name="is_deleted",
            type_=String(StringLength.SOFT_DELETE_FLAG),
            nullable=False,
            default=SoftDeleteFlag.NO,
            server_default=SoftDeleteFlag.NO,
            doc="Soft delete flag",
        )
        self.config.columns["deleted_at"] = ColumnConfig(
            name="deleted_at",
            type_=DateTime(timezone=True),
            nullable=True,
            doc="Deletion timestamp",
        )
        self.config.features["soft_delete"] = True
        return self

    def with_audit(self, user_type: Any = BigInteger) -> ModelBuilder:
        """Add audit columns (created_by_id, updated_by_id)."""
        self.config.columns["created_by_id"] = ColumnConfig(
            name="created_by_id",
            type_=user_type,
            nullable=True,
            doc="User who created this record",
        )
        self.config.columns["updated_by_id"] = ColumnConfig(
            name="updated_by_id",
            type_=user_type,
            nullable=True,
            doc="User who last updated this record",
        )
        self.config.features["audit"] = True
        return self

    def with_tenant(
        self, type_: Any = BigInteger, nullable: bool = False
    ) -> ModelBuilder:
        """Add tenant_id column for multi-tenancy."""
        self.config.columns["tenant_id"] = ColumnConfig(
            name="tenant_id",
            type_=type_,
            nullable=nullable,
            index=True,
            doc="Tenant identifier",
        )
        self.config.features["tenant"] = True
        return self

    def with_organization(self, nullable: bool = False) -> ModelBuilder:
        """Add organization_id column."""
        self.config.columns["organization_id"] = ColumnConfig(
            name="organization_id",
            type_=BigInteger,
            nullable=nullable,
            index=True,
            foreign_key="organizations.id",
            doc="Organization identifier",
        )
        self.config.features["organization"] = True
        return self

    def with_version(self) -> ModelBuilder:
        """Add optimistic locking version column."""
        self.config.columns["version"] = ColumnConfig(
            name="version",
            type_=BigInteger,
            nullable=False,
            default=DEFAULT_VERSION,
            server_default=ServerDefault.ZERO,
            doc="Version for optimistic locking",
        )
        self.config.features["version"] = True
        return self

    def with_metadata(self, name: str = "meta", nullable: bool = True) -> ModelBuilder:
        """Add JSON metadata column."""
        from sqlalchemy import JSON

        self.config.columns[name] = ColumnConfig(
            name=name, type_=JSON, nullable=nullable, doc="JSON metadata"
        )
        return self

    # ==================== Custom Columns ====================

    def with_column(
        self,
        name: str,
        type_: Any,
        nullable: bool = True,
        unique: bool = False,
        index: bool = False,
        default: Any = None,
        server_default: Any = None,
        foreign_key: str | None = None,
        doc: str = "",
    ) -> ModelBuilder:
        """Add a custom column."""
        self.config.columns[name] = ColumnConfig(
            name=name,
            type_=type_,
            nullable=nullable,
            unique=unique,
            index=index,
            default=default,
            server_default=server_default,
            foreign_key=foreign_key,
            doc=doc,
        )
        return self

    def without_column(self, name: str) -> ModelBuilder:
        """Remove a column by name."""
        if name in self.config.columns:
            del self.config.columns[name]
        return self

    def with_index(
        self, name: str, columns: list[str], unique: bool = False
    ) -> ModelBuilder:
        """Add a table index."""
        self.config.indexes.append(
            IndexConfig(name=name, columns=columns, unique=unique)
        )
        return self

    def with_mixin(self, mixin_class: type) -> ModelBuilder:
        """Add a mixin class."""
        self.config.mixins.append(mixin_class)
        return self

    def with_attribute(self, name: str, value: Any) -> ModelBuilder:
        """Add a custom attribute/method to the model."""
        self.config.extra_attributes[name] = value
        return self

    # ==================== Build ====================

    def build(self) -> type:
        """Build and return the SQLAlchemy model class.

        Returns:
            SQLAlchemy model class

        """
        config = self.config

        # Create column dict
        columns = {}
        for col_name, col_config in config.columns.items():
            columns[col_name] = col_config.to_column()

        # Create index list
        indexes = []
        for idx_config in config.indexes:
            idx = Index(idx_config.name, *idx_config.columns, unique=idx_config.unique)
            indexes.append(idx)

        # Determine bases
        bases = tuple(config.mixins) + (Base,)

        # Create the class dict
        class_dict = {
            "__tablename__": config.table_name,
            "__table_args__": tuple(indexes) if indexes else {},
            **columns,
            **config.extra_attributes,
            "__config__": config,  # Store config for introspection
        }

        # Add to_dict method if timestamps feature is enabled
        if config.features.get("timestamps"):
            class_dict["to_dict"] = self._create_to_dict_method(config.columns.keys())

        # Create the class
        model_class = type(config.name, bases, class_dict)

        return model_class

    def _create_to_dict_method(self, column_names: list[str]) -> Callable:
        """Create a to_dict method for the model."""

        def to_dict(self) -> dict[str, Any]:
            """Execute to_dict operation.

            Returns:
                The result of the operation.
            """
            result = {}
            for name in column_names:
                value = getattr(self, name, None)
                if isinstance(value, datetime):
                    value = value.isoformat() if value else None
                result[name] = value
            return result

        return to_dict


# ==================== Pre-configured Model Templates ====================


class ModelTemplates:
    """Pre-configured model templates for common use cases."""

    @staticmethod
    def lookup_table(name: str, table_name: str | None = None) -> type:
        """Create a standard lookup table model."""
        return (
            ModelBuilder(name, table_name or f"{ModelBuilder._to_snake_case(name)}s")
            .with_id()
            .with_code()
            .with_name()
            .with_description(nullable=True)
            .with_timestamps()
            .build()
        )

    @staticmethod
    def tenant_scoped(name: str, table_name: str | None = None) -> ModelBuilder:
        """Create a tenant-scoped model builder with common columns."""
        return (
            ModelBuilder(name, table_name)
            .with_id()
            .with_urn()
            .with_tenant()
            .with_timestamps()
            .with_audit()
            .with_soft_delete()
        )

    @staticmethod
    def organization_scoped(name: str, table_name: str | None = None) -> ModelBuilder:
        """Create an organization-scoped model builder with common columns."""
        return (
            ModelBuilder(name, table_name)
            .with_id()
            .with_urn()
            .with_organization()
            .with_timestamps()
            .with_audit()
            .with_soft_delete()
        )

    @staticmethod
    def user_model(name: str = "User", table_name: str = "users") -> type:
        """Create a standard user model."""
        return (
            ModelBuilder(name, table_name)
            .with_id()
            .with_urn()
            .with_email()
            .with_phone(nullable=True)
            .with_password()
            .with_name()
            .with_boolean("email_verified", default=False)
            .with_timestamps()
            .with_audit()
            .with_soft_delete()
            .build()
        )

    @staticmethod
    def product_model(name: str = "Product", table_name: str = "products") -> type:
        """Create a standard product model."""
        return (
            ModelBuilder(name, table_name)
            .with_id()
            .with_urn()
            .with_code()
            .with_name(nullable=False)
            .with_description()
            .with_column("price", String(20), nullable=False, default="0.00")
            .with_column("currency", String(3), nullable=False, default="USD")
            .with_status(default="draft")
            .with_timestamps()
            .with_audit()
            .with_soft_delete()
            .build()
        )


# ==================== Decorator API ====================


def configurable_model(table_name: str | None = None, **features):
    """Decorator for creating configurable models.

    Example:
        >>> @configurable_model("custom_users", timestamps=True, soft_delete=True)
        >>> class MyUser:
        ...     email: str = column(String(255), unique=True)
        ...     name: str = column(String(100))

    """

    def decorator(cls: type) -> type:
        """Execute decorator operation.

        Returns:
            The result of the operation.
        """
        name = cls.__name__
        tbl_name = table_name or ModelBuilder._to_snake_case(name)

        builder = ModelBuilder(name, tbl_name)

        # Add standard features
        if features.get("id", True):
            builder.with_id()
        if features.get("urn", True):
            builder.with_urn()
        if features.get("timestamps", True):
            builder.with_timestamps()
        if features.get("soft_delete", False):
            builder.with_soft_delete()
        if features.get("audit", False):
            builder.with_audit()
        if features.get("tenant", False):
            builder.with_tenant()
        if features.get("organization", False):
            builder.with_organization()
        if features.get("version", False):
            builder.with_version()

        # Process class annotations for columns
        annotations = getattr(cls, "__annotations__", {})
        for attr_name, attr_type in annotations.items():
            if not attr_name.startswith("_"):
                # Check if there's a default value with column info
                default = getattr(cls, attr_name, None)
                if isinstance(default, ColumnConfig):
                    builder.config.columns[attr_name] = default
                elif isinstance(default, Column):
                    # Extract column info from existing Column
                    pass

        return builder.build()

    return decorator


def column(type_: Any, **kwargs) -> ColumnConfig:
    """Helper to create a ColumnConfig."""
    return ColumnConfig(name="", type_=type_, **kwargs)
