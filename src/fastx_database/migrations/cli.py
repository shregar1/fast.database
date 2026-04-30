"""Migration CLI Commands.

Provides CLI commands for managing model migrations.

These commands can be integrated with the main fastmvc CLI or used standalone.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastx_database.core.constants.migration import (
    DEFAULT_MIGRATION_VERSION,
    MIGRATION_PREVIEW_MAX_LENGTH,
)


def create_cli_group() -> Any:
    """Create the migration CLI group.

    Returns:
        Click group for migration commands

    """
    try:
        import click
    except ImportError:
        raise ImportError(
            "click is required for CLI commands. Install with: pip install click"
        )

    @click.group(name="db-model")
    def db_model():
        """Model-specific database migration commands.

        These commands work with individual models and their migrations,
        complementing the standard Alembic workflow.
        """
        pass

    @db_model.command()
    @click.argument("model_name")
    @click.option(
        "--version",
        default=DEFAULT_MIGRATION_VERSION,
        help="Migration version (default: " + DEFAULT_MIGRATION_VERSION + ")",
    )
    @click.option(
        "--output",
        "-o",
        default=None,
        help="Output file path (default: auto-generated)",
    )
    def generate(model_name: str, version: str, output: str | None):
        """Generate a migration file for a model.

        Example:
            $ fastmvc db-model generate User
            $ fastmvc db-model generate Product --version 002

        """
        from fastx_database.migrations.discovery import discover_model_migrations
        from fastx_database.migrations.generator import generate_migration_file

        # Ensure models are discovered
        discover_model_migrations()

        # Find the model
        from fastx_database.migrations.registry import _registry

        model = _registry.get_model(model_name)

        if model is None:
            click.secho(f"✗ Model '{model_name}' not found", fg="red")
            click.echo("Make sure the model is imported before running this command.")
            sys.exit(1)

        try:
            output_path = generate_migration_file(model, output, version)
            click.secho(f"✓ Generated migration: {output_path}", fg="green")

            # Show migration preview
            from fastx_database.migrations.generator import generate_model_migration

            migration_code = generate_model_migration(model, version)
            click.echo("\nMigration preview:")
            click.echo("-" * 40)
            click.echo(
                migration_code[:MIGRATION_PREVIEW_MAX_LENGTH] + "..."
                if len(migration_code) > MIGRATION_PREVIEW_MAX_LENGTH
                else migration_code
            )

        except Exception as e:
            click.secho(f"✗ Failed to generate migration: {e}", fg="red")
            sys.exit(1)

    @db_model.command(name="list")
    @click.option(
        "--pending/--applied",
        default=None,
        help="Filter by migration status",
    )
    @click.option(
        "--database-url",
        envvar="DATABASE_URL",
        help="Database URL (or set DATABASE_URL env var)",
    )
    def list_models(pending: bool | None, database_url: str | None):
        """List all models and their migration status.

        Example:
            $ fastmvc db-model list
            $ fastmvc db-model list --pending
            $ fastmvc db-model list --applied

        """
        from fastx_database.migrations.discovery import discover_model_migrations
        from fastx_database.migrations.registry import _registry

        discover_model_migrations()

        models = _registry.get_all_models()

        if not models:
            click.echo("No models found.")
            return

        # Get migration status if database URL provided
        statuses = {}
        if database_url:
            from sqlalchemy import create_engine

            engine = create_engine(database_url)

            for name, model in models.items():
                migration = _registry.get_migration(name)
                if migration:
                    try:
                        statuses[name] = migration.is_applied(engine)
                    except Exception:
                        statuses[name] = None

        # Display
        click.echo(f"\n{'Model':<30} {'Version':<10} {'Status':<15}")
        click.echo("-" * 60)

        for name in sorted(models.keys()):
            migration = _registry.get_migration(name)
            version = migration.version if migration else "N/A"

            if name in statuses:
                if statuses[name]:
                    status = click.style("✓ applied", fg="green")
                else:
                    status = click.style("○ pending", fg="yellow")
            else:
                status = "unknown"

            # Filter if requested
            if pending is True and statuses.get(name) is True:
                continue
            if pending is False and statuses.get(name) is False:
                continue

            click.echo(f"{name:<30} {version:<10} {status:<15}")

        click.echo()

    @db_model.command()
    @click.argument("model_names", nargs=-1)
    @click.option(
        "--database-url",
        envvar="DATABASE_URL",
        required=True,
        help="Database URL (or set DATABASE_URL env var)",
    )
    @click.option(
        "--dry-run",
        is_flag=True,
        help="Show what would be done without executing",
    )
    def migrate(model_names: tuple[str, ...], database_url: str, dry_run: bool):
        """Run migrations for specific models (or all if none specified).

        Example:
            $ fastmvc db-model migrate
            $ fastmvc db-model migrate User Product
            $ fastmvc db-model migrate --dry-run

        """
        from fastx_database.migrations.discovery import discover_model_migrations
        from fastx_database.migrations.registry import run_model_migrations
        from sqlalchemy import create_engine

        discover_model_migrations()

        if dry_run:
            click.echo("[DRY RUN] Would execute the following migrations:")

        try:
            engine = create_engine(database_url)

            models_list = list(model_names) if model_names else None

            if dry_run:
                from fastx_database.migrations.registry import _registry

                pending = _registry.get_pending_migrations(engine)
                for migration in pending:
                    model_name = migration.get_model().__name__
                    if models_list is None or model_name in models_list:
                        click.echo(f"  - {model_name} (v{migration.version})")
                return

            results = run_model_migrations(engine, models_list)

            success_count = sum(1 for v in results.values() if v)
            fail_count = len(results) - success_count

            if success_count:
                click.secho(f"✓ {success_count} migration(s) applied", fg="green")
            if fail_count:
                click.secho(f"✗ {fail_count} migration(s) failed", fg="red")
                for name, success in results.items():
                    if not success:
                        click.echo(f"  - {name}")

            if fail_count:
                sys.exit(1)

        except Exception as e:
            click.secho(f"✗ Migration failed: {e}", fg="red")
            sys.exit(1)

    @db_model.command()
    @click.argument("model_names", nargs=-1)
    @click.option(
        "--database-url",
        envvar="DATABASE_URL",
        required=True,
        help="Database URL (or set DATABASE_URL env var)",
    )
    @click.option(
        "--force",
        is_flag=True,
        help="Skip confirmation prompt",
    )
    def rollback(model_names: tuple[str, ...], database_url: str, force: bool):
        """Rollback migrations for specific models.

        Example:
            $ fastmvc db-model rollback User
            $ fastmvc db-model rollback User Product --force

        """
        from fastx_database.migrations.discovery import discover_model_migrations
        from fastx_database.migrations.registry import rollback_model_migrations
        from sqlalchemy import create_engine

        discover_model_migrations()

        if not model_names:
            click.secho("✗ Please specify at least one model to rollback", fg="red")
            sys.exit(1)

        if not force:
            click.confirm(
                f"Rollback migrations for: {', '.join(model_names)}?",
                abort=True,
            )

        try:
            engine = create_engine(database_url)
            results = rollback_model_migrations(engine, list(model_names))

            for name, success in results.items():
                if success:
                    click.secho(f"✓ Rolled back {name}", fg="green")
                else:
                    click.secho(f"✗ Failed to rollback {name}", fg="red")

            if not all(results.values()):
                sys.exit(1)

        except Exception as e:
            click.secho(f"✗ Rollback failed: {e}", fg="red")
            sys.exit(1)

    @db_model.command()
    @click.argument("model_name")
    def sql(model_name: str):
        """Generate SQL for a model's migration.

        Example:
            $ fastmvc db-model sql User

        """
        from fastx_database.migrations.discovery import discover_model_migrations
        from fastx_database.migrations.registry import _registry

        discover_model_migrations()

        migration = _registry.get_migration(model_name)
        if migration is None:
            click.secho(f"✗ Model '{model_name}' not found", fg="red")
            sys.exit(1)

        try:
            sql = migration.get_sql()
            click.echo(f"-- SQL for {model_name} migration")
            click.echo(sql)
        except Exception as e:
            click.secho(f"✗ Failed to generate SQL: {e}", fg="red")
            sys.exit(1)

    return db_model


# Create the CLI group
migration_cli = create_cli_group()


if __name__ == "__main__":
    migration_cli()
