"""Fast Database Migrations Package.

Provides automatic migration discovery and registration for models.
Each model can define its migration inline, and migrations are automatically
discovered when the model is imported.

Usage:
    >>> from fastx_database.persistence.models import User
    >>> from fastx_database.migrations import get_model_migration, run_model_migrations
    >>>
    >>> # Get migration for a specific model
    >>> migration = get_model_migration(User)
    >>>
    >>> # Run all pending model migrations
    >>> run_model_migrations(engine)
"""

from __future__ import annotations

from fastx_database.migrations.registry import (
    MigrationRegistry,
    get_model_migration,
    get_registered_models,
    register_model_migration,
    run_model_migrations,
)
from fastx_database.migrations.model_migration import ModelMigration
from fastx_database.migrations.discovery import discover_model_migrations
from fastx_database.migrations.generator import generate_model_migration

__all__ = [
    "MigrationRegistry",
    "ModelMigration",
    "discover_model_migrations",
    "generate_model_migration",
    "get_model_migration",
    "get_registered_models",
    "register_model_migration",
    "run_model_migrations",
]
