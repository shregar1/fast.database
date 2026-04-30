"""Tests for the model migration system."""

from __future__ import annotations

import pytest
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase

from fastx_database.migrations import (
    ModelMigration,
    get_model_migration,
    get_registered_models,
    register_model_migration,
    run_model_migrations,
)
from fastx_database.migrations.registry import MigrationRegistry


class TestBase(DeclarativeBase):
    """Test base class."""

    pass


class TestModelMigration:
    """Tests for the ModelMigration base class."""

    def test_model_migration_has_version(self):
        """Test that ModelMigration has a version attribute."""
        assert hasattr(ModelMigration, "version")
        assert ModelMigration.version == "001"

    def test_model_migration_has_description(self):
        """Test that ModelMigration has a description attribute."""
        assert hasattr(ModelMigration, "description")

    def test_model_migration_has_is_create(self):
        """Test that ModelMigration has is_create attribute."""
        assert hasattr(ModelMigration, "is_create")
        assert ModelMigration.is_create is True


class TestMigrationRegistry:
    """Tests for the MigrationRegistry."""

    def test_registry_is_singleton(self):
        """Test that registry is a singleton."""
        reg1 = MigrationRegistry()
        reg2 = MigrationRegistry()
        assert reg1 is reg2

    def test_register_model(self):
        """Test registering a model and its migration."""
        registry = MigrationRegistry()
        registry.clear()

        class TestModel(TestBase):
            """Represents the TestModel class."""

            __tablename__ = "test_model"
            id = Column(Integer, primary_key=True)

        class TestModelMigration(ModelMigration):
            """Represents the TestModelMigration class."""

            version = "001"

        registry.register(TestModel, TestModelMigration)

        assert "TestModel" in registry.get_all_models()
        assert registry.get_migration("TestModel") is TestModelMigration

    def test_get_ordered_migrations(self):
        """Test getting migrations in dependency order."""
        registry = MigrationRegistry()
        registry.clear()

        class ModelA(TestBase):
            """Represents the ModelA class."""

            __tablename__ = "model_a"
            id = Column(Integer, primary_key=True)

        class ModelB(TestBase):
            """Represents the ModelB class."""

            __tablename__ = "model_b"
            id = Column(Integer, primary_key=True)

        class ModelAMigration(ModelMigration):
            """Represents the ModelAMigration class."""

            version = "001"
            depends_on = []

        class ModelBMigration(ModelMigration):
            """Represents the ModelBMigration class."""

            version = "001"
            depends_on = ["ModelA"]

        registry.register(ModelA, ModelAMigration)
        registry.register(ModelB, ModelBMigration)

        ordered = registry.get_ordered_migrations()
        assert ordered[0] is ModelAMigration
        assert ordered[1] is ModelBMigration


class TestMigrationFunctions:
    """Tests for the migration utility functions."""

    def test_register_and_get_model_migration(self):
        """Test registering and retrieving a model migration."""
        from fastx_database.migrations.registry import _registry

        _registry.clear()

        class MyModel(TestBase):
            """Represents the MyModel class."""

            __tablename__ = "my_model"
            id = Column(Integer, primary_key=True)

        class MyModelMigration(ModelMigration):
            """Represents the MyModelMigration class."""

            version = "001"

        register_model_migration(MyModel, MyModelMigration)

        retrieved = get_model_migration(MyModel)
        assert retrieved is MyModelMigration

        _registry.clear()

    def test_get_registered_models(self):
        """Test getting all registered models."""
        from fastx_database.migrations.registry import _registry

        _registry.clear()

        class AnotherModel(TestBase):
            """Represents the AnotherModel class."""

            __tablename__ = "another_model"
            id = Column(Integer, primary_key=True)

        class AnotherModelMigration(ModelMigration):
            """Represents the AnotherModelMigration class."""

            version = "001"

        register_model_migration(AnotherModel, AnotherModelMigration)

        models = get_registered_models()
        assert "AnotherModel" in models

        _registry.clear()


class TestAutoMigration:
    """Tests for auto-generated migrations."""

    def test_auto_migration_creates_table(self):
        """Test that auto-migration creates the table."""
        from fastx_database.migrations.model_migration import AutoModelMigration

        class AutoModel(TestBase):
            """Represents the AutoModel class."""

            __tablename__ = "auto_model"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        class AutoModelMigration(AutoModelMigration):
            """Represents the AutoModelMigration class."""

            _model_class = AutoModel

        engine = create_engine("sqlite:///:memory:")

        # Migration should create the table
        AutoModelMigration.upgrade(engine)

        # Check table exists
        from sqlalchemy import inspect

        inspector = inspect(engine)
        assert "auto_model" in inspector.get_table_names()

    def test_auto_migration_is_applied(self):
        """Test that auto-migration can check if applied."""
        from fastx_database.migrations.model_migration import AutoModelMigration

        class CheckModel(TestBase):
            """Represents the CheckModel class."""

            __tablename__ = "check_model"
            id = Column(Integer, primary_key=True)

        class CheckModelMigration(AutoModelMigration):
            """Represents the CheckModelMigration class."""

            _model_class = CheckModel

        engine = create_engine("sqlite:///:memory:")

        # Should not be applied initially
        assert not CheckModelMigration.is_applied(engine)

        # Apply migration
        CheckModelMigration.upgrade(engine)

        # Should now be applied
        assert CheckModelMigration.is_applied(engine)


class TestMigrationDiscovery:
    """Tests for migration discovery."""

    def test_discover_model_migration_returns_migration(self):
        """Test discovering migration for a model."""
        from fastx_database.migrations.discovery import discover_model_migration

        class DiscoverModel(TestBase):
            """Represents the DiscoverModel class."""

            __tablename__ = "discover_model"
            id = Column(Integer, primary_key=True)

        migration = discover_model_migration(DiscoverModel)
        assert migration is not None

    def test_discover_model_migration_uses_existing(self):
        """Test that discovery uses existing __migration__ attribute."""
        from fastx_database.migrations.discovery import discover_model_migration

        class ExistingMigrationModel(TestBase):
            """Represents the ExistingMigrationModel class."""

            __tablename__ = "existing_migration_model"
            id = Column(Integer, primary_key=True)

            class __migration__(ModelMigration):
                """Represents the __migration__ class."""

                version = "custom"

        migration = discover_model_migration(ExistingMigrationModel)
        assert migration.version == "custom"


class TestMigrationGenerator:
    """Tests for migration generation."""

    def test_generate_model_migration_returns_string(self):
        """Test that migration generator returns a string."""
        from fastx_database.migrations.generator import generate_model_migration

        class GenModel(TestBase):
            """Represents the GenModel class."""

            __tablename__ = "gen_model"
            id = Column(Integer, primary_key=True)
            email = Column(String(255), unique=True)

        code = generate_model_migration(GenModel)
        assert isinstance(code, str)
        assert "class GenModelMigration" in code
        assert "gen_model" in code

    def test_generate_model_migration_includes_columns(self):
        """Test that generated migration includes column info."""
        from fastx_database.migrations.generator import generate_model_migration

        class ColModel(TestBase):
            """Represents the ColModel class."""

            __tablename__ = "col_model"
            id = Column(Integer, primary_key=True)
            name = Column(String(100))

        code = generate_model_migration(ColModel)
        assert "id:" in code or "id" in code
        assert "name:" in code or "name" in code


class TestIntegration:
    """Integration tests for the full migration system."""

    def test_full_migration_workflow(self):
        """Test the complete migration workflow."""
        from fastx_database.migrations.registry import _registry

        _registry.clear()

        class WorkflowModel(TestBase):
            """Represents the WorkflowModel class."""

            __tablename__ = "workflow_model"
            id = Column(Integer, primary_key=True)
            data = Column(String(100))

        class WorkflowModelMigration(ModelMigration):
            """Represents the WorkflowModelMigration class."""

            version = "001"
            _model_class = WorkflowModel

        # Register
        register_model_migration(WorkflowModel, WorkflowModelMigration)

        # Create engine and run migration
        engine = create_engine("sqlite:///:memory:")
        results = run_model_migrations(engine)

        assert "WorkflowModel" in results
        assert results["WorkflowModel"] is True

        # Verify table exists
        from sqlalchemy import inspect

        inspector = inspect(engine)
        assert "workflow_model" in inspector.get_table_names()

        _registry.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
