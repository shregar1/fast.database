# fastmvc-db-models

**Shared SQLAlchemy ORM models** for FastMVC applications: one declarative `Base`, table name constants, and models for users/auth, organizations, subscriptions, payments, commerce (cart/orders/shipments), webhooks, notifications, LLM **conversation** threads, **user messaging** (chats, messages, read receipts, notification delivery), personal ledger / Pure.cam–aligned tables, and audit logs.

**Python:** 3.10+ · **Dependency:** `sqlalchemy>=2,<3`

**Import package:** `fastmvc_db_models`  
**PyPI distribution name:** `fastmvc-db-models` (hyphenated)

## Layout

- **`fastmvc_db_models.models` — `Base`** and all table classes.
- **`fastmvc_db_models.constants.db.table` — `Table`** — centralized string names for `__tablename__`.

## Install

```bash
pip install -e ./fastmvc_db_models
```

Or from PyPI (when published):

```bash
pip install fastmvc-db-models
```

Pair with **`fastmvc_db`** so your app’s engine uses the same metadata for Alembic migrations.

## Related packages

- **`fastmvc_db`** — engine and sessions.
- Monorepo: [../README.md](../README.md).

## Tooling

See [CONTRIBUTING.md](CONTRIBUTING.md), [Makefile](Makefile), and [PUBLISHING.md](PUBLISHING.md).
