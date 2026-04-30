"""Migration Discovery.

Automatically discovers and registers migrations from model classes.
"""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import TYPE_CHECKING

from fastx_database.core.constants.migration import DEFAULT_MIGRATION_VERSION

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase
    from fastx_database.migrations.model_migration import ModelMigration


def discover_model_migration(
    model_class: type[DeclarativeBase],
) -> type[ModelMigration] | None:
    """Discover the migration for a single model class.

    Checks for:
    1. ``__migration__`` attribute on the model class
    2. Auto-generates a migration if none found

    Args:
        model_class: SQLAlchemy model class to check

    Returns:
        Migration class or None

    """
    # Check if model already has a migration registered
    from fastx_database.migrations.registry import _registry

    existing = _registry.get_migration(model_class.__name__)
    if existing:
        return existing

    # Check for __migration__ attribute
    migration = getattr(model_class, "__migration__", None)
    if migration is not None:
        if inspect.isclass(migration):
            return migration

    # No migration found, create auto-migration
    from fastx_database.migrations.model_migration import AutoModelMigration

    auto_migration = type(
        f"{model_class.__name__}AutoMigration",
        (AutoModelMigration,),
        {
            "version": DEFAULT_MIGRATION_VERSION,
            "description": f"Auto-generated migration for {model_class.__name__}",
            "_model_class": model_class,
        },
    )

    return auto_migration


def discover_model_migrations(
    models_package: str = "fastx_database.persistence.models",
    auto_register: bool = True,
) -> dict[str, type[ModelMigration]]:
    """Discover all model migrations in a package.

    Scans the models package for SQLAlchemy model classes and discovers
    or creates migrations for each.

    Args:
        models_package: Import path to the models package
        auto_register: Whether to auto-register discovered migrations

    Returns:
        Dictionary mapping model names to migration classes

    """
    from fastx_database.migrations.registry import register_model_migration

    discovered: dict[str, type[ModelMigration]] = {}

    try:
        package = importlib.import_module(models_package)
    except ImportError:
        return discovered

    # Get package path
    if not hasattr(package, "__path__"):
        return discovered

    package_path = Path(package.__path__[0])

    # Scan for model modules
    for module_file in package_path.glob("*.py"):
        if module_file.name.startswith("_"):
            continue

        module_name = f"{models_package}.{module_file.stem}"

        try:
            module = importlib.import_module(module_name)
        except ImportError:
            continue

        # Find model classes in module
        for name, obj in inspect.getmembers(module):
            if not inspect.isclass(obj):
                continue

            # Check if it's a SQLAlchemy model
            if not hasattr(obj, "__tablename__"):
                continue

            # Skip the Base class itself
            if obj.__name__ == "Base":
                continue

            # Skip abstract base classes (but only if they don't have their own table)
            # Note: SQLAlchemy declarative_base sets __abstract__ = True on the base,
            # but concrete models inherit from it
            if getattr(obj, "__abstract__", False) and not hasattr(obj, "__table__"):
                continue

            # Skip lookup tables that are just aliases
            if name.endswith("Lk") and not hasattr(obj, "__migration__"):
                continue

            # Discover migration
            migration = discover_model_migration(obj)
            if migration:
                discovered[name] = migration

                if auto_register:
                    register_model_migration(obj, migration)

    return discovered


def auto_discover_on_import():
    """Auto-discover and register migrations when models are imported.

    This is called automatically when the migrations package is imported
    to ensure all models have their migrations registered.
    """
    from fastx_database.migrations.registry import _registry

    # Only run if registry is empty
    if _registry.get_all_models():
        return

    discover_model_migrations()


# Hook into SQLAlchemy's declarative base to auto-register on model definition
_original_declarative_base = None


def _patch_declarative_base():
    """Patch SQLAlchemy's declarative_base to auto-register migrations.

    This ensures that any model defined after migrations are set up
    will automatically have its migration registered.
    """
    global _original_declarative_base

    try:
        from sqlalchemy.orm import declarative_base as original
    except ImportError:
        return

    if _original_declarative_base is not None:
        return  # Already patched

    _original_declarative_base = original

    def patched_declarative_base(*args, **kwargs):
        """Patched version that auto-registers migrations."""
        base = original(*args, **kwargs)

        # Store original __init_subclass__ if it exists
        original_init_subclass = base.__init_subclass__

        @classmethod
        def __init_subclass__(cls, **kwargs):
            """Auto-register migration when a model is defined."""
            result = original_init_subclass.__func__(cls, **kwargs)

            # Skip abstract classes
            if getattr(cls, "__abstract__", False):
                return result

            # Skip if no table name
            if not hasattr(cls, "__tablename__"):
                return result

            # Discover and register migration
            migration = discover_model_migration(cls)
            if migration:
                from fastx_database.migrations.registry import register_model_migration

                register_model_migration(cls, migration)

            return result

        base.__init_subclass__ = __init_subclass__

        return base

    # Replace the original
    import sqlalchemy.orm

    sqlalchemy.orm.declarative_base = patched_declarative_base


# Optional: Enable auto-discovery on import
# This can be controlled via environment variable
import os

if os.environ.get("FASTDB_AUTO_DISCOVER_MIGRATIONS", "1") == "1":
    auto_discover_on_import()
