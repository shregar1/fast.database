"""Migration Registry.

Central registry for tracking model migrations. Provides discovery,
ordering, and execution of migrations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine
    from sqlalchemy.orm import DeclarativeBase
    from fastx_database.migrations.model_migration import ModelMigration


class MigrationRegistry:
    """Central registry for model migrations.

    This class tracks all registered models and their migrations,
    provides dependency ordering, and manages migration execution.
    """

    _instance: MigrationRegistry | None = None

    def __new__(cls) -> MigrationRegistry:
        """Singleton pattern to ensure one global registry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._migrations: dict[str, type[ModelMigration]] = {}
            cls._instance._models: dict[str, type[DeclarativeBase]] = {}
        return cls._instance

    def register(
        self,
        model_class: type[DeclarativeBase],
        migration_class: type[ModelMigration],
    ) -> None:
        """Register a model and its migration.

        Args:
            model_class: The SQLAlchemy model class
            migration_class: The migration class for the model

        """
        model_name = model_class.__name__

        # Bind migration to model
        migration_class._model_class = model_class

        # Store in registry
        self._models[model_name] = model_class
        self._migrations[model_name] = migration_class

    def get_migration(
        self,
        model: type[DeclarativeBase] | str,
    ) -> type[ModelMigration] | None:
        """Get the migration for a model.

        Args:
            model: Model class or model name

        Returns:
            Migration class or None if not found

        """
        if isinstance(model, type):
            model_name = model.__name__
        else:
            model_name = model
        return self._migrations.get(model_name)

    def get_model(self, model_name: str) -> type[DeclarativeBase] | None:
        """Get a registered model by name.

        Args:
            model_name: Name of the model class

        Returns:
            Model class or None if not found

        """
        return self._models.get(model_name)

    def get_all_models(self) -> dict[str, type[DeclarativeBase]]:
        """Get all registered models.

        Returns:
            Dictionary mapping model names to model classes

        """
        return self._models.copy()

    def get_ordered_migrations(self) -> list[type[ModelMigration]]:
        """Get migrations in dependency order.

        Uses topological sort to order migrations based on dependencies.

        Returns:
            List of migration classes in execution order

        """
        from collections import deque

        # Build dependency graph
        in_degree: dict[str, int] = {name: 0 for name in self._migrations}
        graph: dict[str, list[str]] = {name: [] for name in self._migrations}

        for model_name, migration in self._migrations.items():
            for dep in migration.depends_on:
                if dep in self._migrations:
                    graph[dep].append(model_name)
                    in_degree[model_name] += 1

        # Kahn's algorithm for topological sort
        queue = deque([name for name, degree in in_degree.items() if degree == 0])
        ordered = []

        while queue:
            model_name = queue.popleft()
            ordered.append(self._migrations[model_name])

            for dependent in graph[model_name]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(ordered) != len(self._migrations):
            # Cycle detected, return in registration order
            return list(self._migrations.values())

        return ordered

    def run_migrations(
        self,
        engine: Engine,
        models: list[type[DeclarativeBase] | str] | None = None,
    ) -> dict[str, bool]:
        """Run migrations for registered models.

        Args:
            engine: SQLAlchemy engine to run migrations on
            models: Optional list of specific models to migrate (default: all)

        Returns:
            Dictionary mapping model names to success status

        """
        results = {}

        if models:
            # Run specific models
            migrations_to_run = []
            for model in models:
                migration = self.get_migration(model)
                if migration:
                    migrations_to_run.append(migration)
        else:
            # Run all in dependency order
            migrations_to_run = self.get_ordered_migrations()

        for migration in migrations_to_run:
            model_name = migration.get_model().__name__
            try:
                if not migration.is_applied(engine):
                    migration.upgrade(engine)
                    results[model_name] = True
                else:
                    results[model_name] = True  # Already applied
            except Exception as e:
                results[model_name] = False
                # Log error but continue with other migrations
                print(f"Migration failed for {model_name}: {e}")

        return results

    def rollback_migrations(
        self,
        engine: Engine,
        models: list[type[DeclarativeBase] | str] | None = None,
    ) -> dict[str, bool]:
        """Rollback migrations for registered models.

        Args:
            engine: SQLAlchemy engine to run rollbacks on
            models: Optional list of specific models to rollback (default: all)

        Returns:
            Dictionary mapping model names to success status

        """
        results = {}

        if models:
            migrations_to_rollback = []
            for model in models:
                migration = self.get_migration(model)
                if migration:
                    migrations_to_rollback.append(migration)
        else:
            # Rollback in reverse dependency order
            migrations_to_rollback = list(reversed(self.get_ordered_migrations()))

        for migration in migrations_to_rollback:
            model_name = migration.get_model().__name__
            try:
                migration.downgrade(engine)
                results[model_name] = True
            except Exception as e:
                results[model_name] = False
                print(f"Rollback failed for {model_name}: {e}")

        return results

    def get_pending_migrations(self, engine: Engine) -> list[type[ModelMigration]]:
        """Get list of migrations that haven't been applied yet.

        Args:
            engine: SQLAlchemy engine to check

        Returns:
            List of pending migration classes

        """
        pending = []
        for migration in self.get_ordered_migrations():
            if not migration.is_applied(engine):
                pending.append(migration)
        return pending

    def clear(self) -> None:
        """Clear all registered migrations (mainly for testing)."""
        self._migrations.clear()
        self._models.clear()


# Global registry instance
_registry = MigrationRegistry()


def register_model_migration(
    model_class: type[DeclarativeBase],
    migration_class: type[ModelMigration],
) -> None:
    """Register a model and its migration with the global registry.

    Args:
        model_class: The SQLAlchemy model class
        migration_class: The migration class for the model

    """
    _registry.register(model_class, migration_class)


def get_model_migration(
    model: type[DeclarativeBase] | str,
) -> type[ModelMigration] | None:
    """Get the migration for a specific model.

    Args:
        model: Model class or model name

    Returns:
        Migration class or None if not found

    """
    return _registry.get_migration(model)


def get_registered_models() -> dict[str, type[DeclarativeBase]]:
    """Get all registered models.

    Returns:
        Dictionary mapping model names to model classes

    """
    return _registry.get_all_models()


def run_model_migrations(
    engine: Engine,
    models: list[type[DeclarativeBase] | str] | None = None,
) -> dict[str, bool]:
    """Run migrations for models.

    Args:
        engine: SQLAlchemy engine to run migrations on
        models: Optional list of specific models to migrate (default: all)

    Returns:
        Dictionary mapping model names to success status

    """
    return _registry.run_migrations(engine, models)


def rollback_model_migrations(
    engine: Engine,
    models: list[type[DeclarativeBase] | str] | None = None,
) -> dict[str, bool]:
    """Rollback migrations for models.

    Args:
        engine: SQLAlchemy engine to run rollbacks on
        models: Optional list of specific models to rollback (default: all)

    Returns:
        Dictionary mapping model names to success status

    """
    return _registry.rollback_migrations(engine, models)


def get_pending_model_migrations(engine: Engine) -> list:
    """Get list of migrations that haven't been applied yet.

    Args:
        engine: SQLAlchemy engine to check

    Returns:
        List of pending migration classes

    """
    return _registry.get_pending_migrations(engine)
