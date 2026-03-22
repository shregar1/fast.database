# Changelog

All notable changes to **fast-database** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] — 2025-03-22

### Changed (breaking)

- **Renamed the Python package** from `fast_db_models` to **`fast_database`**. PyPI distribution remains hyphenated as **`fast-database`** (was `fast-db-models`).
- Update imports: `from fast_database import Base`, `from fast_database.models.user import User`, etc.

## [0.2.0] — 2025-03-22

### Changed

- **Merged `fast-repositories` into this distribution.** Install only `fast-database` (version ≥0.2.0); import paths stay `fast_database.repositories.*` and `fast_database.*`.
- **Dependencies:** added `loguru` and `cachetools` (required by `IRepository`).
- **Source layout:** packages live under `src/fast_database/` and `src/fast_database.repositories/` (setuptools `packages.find`).

### Added

- Tests for soft-delete helpers and orphan model modules (coverage gate for ORM code remains ≥95%).

## [0.1.0]

### Added

- **Mixins:** `OrganizationScopedMixin`, `TenantIdMixin`, `OptimisticLockMixin`, `AuditActorMixin` (plus `TimestampMixin`, `UUIDPrimaryKeyMixin`, `SoftDeleteMixin`).
- **Optimistic locking helpers:** `assert_version_matches`, `expected_version`, `StaleVersionError` (`optimistic_lock.py`).
- **factory_boy example:** `PlanFactory` in `fast_database.factories` (optional `[dev]` extra includes `factory-boy`).
- **Soft-delete helpers:** `where_not_deleted`, `select_active`, `mark_soft_deleted`, `restore_soft_deleted`, `filter_active` (`soft_delete.py`).
- **README:** Alembic notes, tenant composite-index recipe, optimistic lock / audit / factory examples.
- Tooling aligned with the FastMVC monorepo (`Makefile`, pre-commit, Ruff, etc.).

