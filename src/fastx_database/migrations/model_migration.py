"""Model Migration Base Class.

Provides a way to define migrations alongside models. Each model can have
an associated migration that defines how to create, upgrade, and downgrade
the table for that model.
"""

from __future__ import annotations

import hashlib
import inspect
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable

from fastx_database.core.constants.migration import (
    DEFAULT_MIGRATION_VERSION,
    REVISION_ID_LENGTH,
)

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine
    from sqlalchemy.orm import DeclarativeBase


class ModelMigration:
    """Base class for model-specific migrations.

    Each model can define its migration by creating a subclass of ModelMigration
    and setting it as the ``__migration__`` attribute on the model class.

    Example:
        >>> from fastx_database.persistence.models import Base
        >>> from fastx_database.migrations import ModelMigration
        >>> from sqlalchemy import Column, Integer, String
        >>>
        >>> class User(Base):
        ...     __tablename__ = "users"
        ...     id = Column(Integer, primary_key=True)
        ...     email = Column(String(255), unique=True)
        ...
        ...     class __migration__(ModelMigration):
        ...         version = "001"
        ...
        ...         @classmethod
        ...         def upgrade(cls, engine):
        ...             # Custom upgrade logic
        ...             pass
        ...
        >>> # Migration is automatically registered when model is imported

    """

    # Migration version (e.g., "001", "002", etc.)
    version: str = DEFAULT_MIGRATION_VERSION

    # Migration description
    description: str = ""

    # Whether this migration creates the table
    is_create: bool = True

    # Dependencies - other model names that must be migrated first
    depends_on: list[str] = []

    # The model class this migration is for (set automatically)
    _model_class: type[DeclarativeBase] | None = None

    @classmethod
    def get_model(cls) -> type[DeclarativeBase]:
        """Get the model class associated with this migration."""
        if cls._model_class is None:
            raise RuntimeError(f"Migration {cls.__name__} is not bound to a model")
        return cls._model_class

    @classmethod
    def get_table_name(cls) -> str:
        """Get the table name for this migration."""
        model = cls.get_model()
        return model.__tablename__

    @classmethod
    def get_revision_id(cls) -> str:
        """Generate a unique revision ID based on model and version."""
        model = cls.get_model()
        content = f"{model.__name__}:{cls.version}:{cls.description}"
        return hashlib.sha256(content.encode()).hexdigest()[:REVISION_ID_LENGTH]

    @classmethod
    def upgrade(cls, engine: Engine) -> None:
        """Run the upgrade migration.

        Default implementation creates the table from the model metadata.
        Override for custom migration logic.

        Args:
            engine: SQLAlchemy engine to run the migration on

        """
        model = cls.get_model()
        model.__table__.create(engine, checkfirst=True)

    @classmethod
    def downgrade(cls, engine: Engine) -> None:
        """Run the downgrade migration.

        Default implementation drops the table.
        Override for custom migration logic.

        Args:
            engine: SQLAlchemy engine to run the migration on

        """
        model = cls.get_model()
        model.__table__.drop(engine, checkfirst=True)

    @classmethod
    def is_applied(cls, engine: Engine) -> bool:
        """Check if this migration has been applied.

        Default implementation checks if the table exists.
        Override for custom logic.

        Args:
            engine: SQLAlchemy engine to check

        Returns:
            True if migration has been applied, False otherwise

        """
        from sqlalchemy import inspect as sa_inspect

        inspector = sa_inspect(engine)
        return cls.get_table_name() in inspector.get_table_names()

    @classmethod
    def get_sql(cls, dialect: str = "postgresql") -> str:
        """Generate SQL for this migration without executing.

        Args:
            dialect: SQL dialect to generate for

        Returns:
            SQL string for the migration

        """
        from sqlalchemy import create_mock_engine
        from sqlalchemy.orm import DeclarativeBase

        model = cls.get_model()
        sql_statements = []

        def dump(sql, *multiparams, **params):
            sql_str = str(sql.compile(dialect=engine.dialect))
            sql_statements.append(sql_str)

        engine = create_mock_engine(f"{dialect}://", dump)

        # Generate CREATE TABLE statement
        model.__table__.create(engine, checkfirst=False)

        return ";\n".join(sql_statements) + ";"


class AutoModelMigration(ModelMigration):
    """Automatic migration that derives its operations from the model definition.

    This is the default migration type used when a model doesn't specify
    a custom migration.
    """

    description = "Auto-generated migration from model definition"
    is_create = True

    @classmethod
    def upgrade(cls, engine: Engine) -> None:
        """Create the table from model metadata."""
        model = cls.get_model()
        model.__table__.create(engine, checkfirst=True)

    @classmethod
    def downgrade(cls, engine: Engine) -> None:
        """Drop the table."""
        model = cls.get_model()
        model.__table__.drop(engine, checkfirst=True)


def migration_for_model(
    version: str = "001",
    description: str = "",
    depends_on: list[str] | None = None,
) -> Callable[[type[DeclarativeBase]], type[DeclarativeBase]]:
    """Decorator to attach a migration to a model class.

    This is an alternative to defining the ``__migration__`` class attribute.

    Args:
        version: Migration version
        description: Migration description
        depends_on: List of model names that must be migrated first

    Returns:
        Decorator function that attaches migration to model

    Example:
        >>> from fastx_database.migrations import migration_for_model
        >>>
        >>> @migration_for_model(version="001", description="Create users table")
        >>> class User(Base):
        ...     __tablename__ = "users"
        ...     id = Column(Integer, primary_key=True)

    """

    def decorator(model_class: type[DeclarativeBase]) -> type[DeclarativeBase]:
        # Create a new migration class for this model
        migration_class = type(
            f"{model_class.__name__}Migration",
            (AutoModelMigration,),
            {
                "version": DEFAULT_MIGRATION_VERSION,
                "description": description or f"Migration for {model_class.__name__}",
                "depends_on": depends_on or [],
                "_model_class": model_class,
            },
        )

        # Attach to model
        model_class.__migration__ = migration_class

        # Register the migration
        from fastx_database.migrations.registry import register_model_migration

        register_model_migration(model_class, migration_class)

        return model_class

    return decorator
