# Fast Database Model Migrations

Automatic migration system for SQLAlchemy models. Migrations are discovered and registered when models are imported.

## Quick Start

```python
# When you import a model, its migration is automatically registered
from fast_database.persistence.models import User
from fast_database.migrations import get_model_migration

# Get the migration for a model
migration = get_model_migration(User)
print(migration.version)  # "001"

# Run the migration
from sqlalchemy import create_engine
engine = create_engine("postgresql://user:pass@localhost/db")
migration.upgrade(engine)
```

## Features

- **Auto-discovery**: Migrations are automatically discovered when models are imported
- **Auto-registration**: Models automatically get an auto-generated migration if none is specified
- **Dependency ordering**: Migrations respect dependencies between models
- **Custom migrations**: Define custom migrations using the `__migration__` attribute
- **CLI integration**: Manage migrations via CLI commands

## Usage

### Basic Usage

```python
from fast_database.persistence.models import User, Product
from fast_database.migrations import run_model_migrations, get_registered_models
from sqlalchemy import create_engine

# Get all registered models
models = get_registered_models()
print(f"Registered models: {list(models.keys())}")

# Run all migrations
engine = create_engine("postgresql://user:pass@localhost/db")
results = run_model_migrations(engine)
print(results)  # {'User': True, 'Product': True, ...}
```

### Custom Model Migration

Define a custom migration for your model:

```python
from sqlalchemy import Column, Integer, String
from fast_database.persistence.models import Base
from fast_database.migrations import ModelMigration

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    
    class __migration__(ModelMigration):
        version = "001"
        description = "Create users table with indexes"
        depends_on = []  # List model names that must be migrated first
        
        @classmethod
        def upgrade(cls, engine):
            # Custom upgrade logic
            model = cls.get_model()
            model.__table__.create(engine, checkfirst=True)
            
            # Add custom indexes, seed data, etc.
            with engine.connect() as conn:
                conn.execute("CREATE INDEX idx_users_email ON users(email)")
        
        @classmethod
        def downgrade(cls, engine):
            model = cls.get_model()
            model.__table__.drop(engine, checkfirst=True)
```

### Migration Decorator

Alternative to `__migration__` class attribute:

```python
from fast_database.migrations import migration_for_model

@migration_for_model(version="001", description="Create products table")
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
```

### Check Migration Status

```python
from fast_database.migrations import get_model_migration
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:pass@localhost/db")
migration = get_model_migration(User)

if migration.is_applied(engine):
    print("Migration already applied")
else:
    print("Migration pending")
```

### Generate SQL Without Executing

```python
migration = get_model_migration(User)
sql = migration.get_sql(dialect="postgresql")
print(sql)
```

## CLI Commands

If using with the FastMVC CLI, the following commands are available:

```bash
# Generate a migration file for a model
fastmvc db-model generate User
fastmvc db-model generate Product --version 002

# List all models and their migration status
fastmvc db-model list
fastmvc db-model list --pending
fastmvc db-model list --applied

# Run migrations
fastmvc db-model migrate
fastmvc db-model migrate User Product
fastmvc db-model migrate --dry-run

# Rollback migrations
fastmvc db-model rollback User
fastmvc db-model rollback User Product --force

# Generate SQL for a migration
fastmvc db-model sql User
```

## Architecture

### Components

1. **ModelMigration**: Base class for model migrations
2. **MigrationRegistry**: Singleton registry for all model migrations
3. **AutoModelMigration**: Default auto-generated migration
4. **Discovery**: Automatic discovery of model migrations

### Auto-Discovery

When `fast_database.persistence.models` is imported:

1. All model classes are scanned
2. For each concrete model (has `__tablename__`):
   - Check if it has a `__migration__` attribute
   - If yes, use that migration
   - If no, create an `AutoModelMigration`
3. Register the migration with the global registry

### Migration Order

Migrations are executed in dependency order using topological sort:

```python
class Order(Base):
    __tablename__ = "orders"
    user_id = Column(Integer, ForeignKey("users.id"))
    
    class __migration__(ModelMigration):
        depends_on = ["User"]  # User must be migrated first
```

## API Reference

### Functions

- `get_model_migration(model)` - Get migration for a model
- `get_registered_models()` - Get all registered models
- `run_model_migrations(engine, models=None)` - Run migrations
- `register_model_migration(model, migration)` - Register a migration
- `generate_model_migration(model)` - Generate migration code

### Classes

- `ModelMigration` - Base migration class
- `AutoModelMigration` - Auto-generated migration
- `MigrationRegistry` - Migration registry singleton

## Environment Variables

- `FASTDB_AUTO_DISCOVER_MIGRATIONS` - Set to "0" to disable auto-discovery
