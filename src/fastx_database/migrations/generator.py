"""Migration Generator.

Generates migration code from SQLAlchemy models.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from fastx_database.core.constants.migration import DEFAULT_MIGRATION_VERSION

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase


def generate_model_migration(
    model_class: type[DeclarativeBase],
    version: str = DEFAULT_MIGRATION_VERSION,
    description: str = "",
) -> str:
    """Generate migration code for a model.

    Creates Python code for a ModelMigration subclass that can be
    saved to a file and customized.

    Args:
        model_class: SQLAlchemy model to generate migration for
        version: Migration version
        description: Migration description

    Returns:
        Python code string for the migration

    """
    model_name = model_class.__name__
    table_name = model_class.__tablename__
    description = description or f"Create {table_name} table"

    # Get column information
    columns_info = []
    for column in model_class.__table__.columns:
        col_type = column.type
        col_str = f"        # {column.name}: {col_type}"
        if column.primary_key:
            col_str += " (PK)"
        if column.foreign_keys:
            fk_list = [fk.target_fullname for fk in column.foreign_keys]
            col_str += f" (FK: {', '.join(fk_list)})"
        columns_info.append(col_str)

    columns_comment = (
        "\n".join(columns_info) if columns_info else "        # No columns defined"
    )

    # Get index information
    indexes_info = []
    for index in model_class.__table__.indexes:
        idx_cols = ", ".join(col.name for col in index.columns)
        indexes_info.append(f"        # Index: {index.name} ({idx_cols})")

    indexes_comment = (
        "\n".join(indexes_info) if indexes_info else "        # No additional indexes"
    )

    # Get foreign key constraints
    fk_info = []
    for fk in model_class.__table__.foreign_keys:
        fk_info.append(f"        # FK: {fk.parent.name} -> {fk.target_fullname}")

    fk_comment = "\n".join(fk_info) if fk_info else "        # No foreign keys"

    template = f'''"""
Migration for {model_name} model.

Generated: {datetime.now().isoformat()}
"""

from sqlalchemy import Engine
from fastx_database.migrations import ModelMigration


class {model_name}Migration(ModelMigration):
    """
    Migration for {model_name} ({table_name} table).
    
    Description: {description}
    """
    
    version = "{version}"
    description = "{description}"
    is_create = True
    
    # Dependencies - list model names that must be migrated first
    depends_on = []
    
    @classmethod
    def upgrade(cls, engine: Engine) -> None:
        """
        Create the {table_name} table.
        
{columns_comment}

{indexes_comment}

{fk_comment}
        """
        model = cls.get_model()
        
        # Create table with all constraints and indexes
        model.__table__.create(engine, checkfirst=True)
        
        # Add any custom post-creation logic here
        # e.g., seed data, create triggers, etc.
    
    @classmethod
    def downgrade(cls, engine: Engine) -> None:
        """
        Drop the {table_name} table.
        """
        model = cls.get_model()
        model.__table__.drop(engine, checkfirst=True)
    
    @classmethod
    def is_applied(cls, engine: Engine) -> bool:
        """
        Check if the table exists.
        
        Override for custom detection logic.
        """
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        return "{table_name}" in inspector.get_table_names()
'''

    return template


def generate_migration_file(
    model_class: type[DeclarativeBase],
    output_path: str | None = None,
    version: str = DEFAULT_MIGRATION_VERSION,
) -> str:
    """Generate and save migration file for a model.

    Args:
        model_class: SQLAlchemy model to generate migration for
        output_path: Path to save the migration file (default: auto-generated)
        version: Migration version

    Returns:
        Path to the generated file

    """
    from pathlib import Path

    migration_code = generate_model_migration(model_class, version)

    if output_path is None:
        # Auto-generate path in migrations/versions directory
        model_file = Path(inspect.getfile(model_class))
        migrations_dir = model_file.parent.parent.parent / "migrations" / "versions"
        migrations_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{model_class.__tablename__}_v{version}.py"
        output_path = migrations_dir / filename
    else:
        output_path = Path(output_path)

    output_path.write_text(migration_code)
    return str(output_path)


import inspect  # Import at end to avoid circular issues


def generate_all_migrations(
    models_package: str = "fastx_database.persistence.models",
    output_dir: str | None = None,
) -> list[str]:
    """Generate migration files for all models in a package.

    Args:
        models_package: Import path to the models package
        output_dir: Directory to save migration files

    Returns:
        List of paths to generated files

    """
    from pathlib import Path
    import importlib

    generated = []

    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "migrations" / "versions"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        package = importlib.import_module(models_package)
    except ImportError:
        return generated

    if not hasattr(package, "__path__"):
        return generated

    package_path = Path(package.__path__[0])

    for module_file in package_path.glob("*.py"):
        if module_file.name.startswith("_"):
            continue

        module_name = f"{models_package}.{module_file.stem}"

        try:
            module = importlib.import_module(module_name)
        except ImportError:
            continue

        for name, obj in inspect.getmembers(module):
            if not inspect.isclass(obj):
                continue

            if not hasattr(obj, "__tablename__"):
                continue

            if getattr(obj, "__abstract__", False):
                continue

            # Generate migration
            output_path = output_dir / f"{obj.__tablename__}_migration.py"
            file_path = generate_migration_file(obj, output_path)
            generated.append(file_path)

    return generated
