# fast-database

**Shared SQLAlchemy 2.x ORM models** for FastMVC-based services: one declarative `Base`, consistent `urn` + audit columns where applicable, and centralized table name constants.

**PyPI name:** `fast-database`  
**Import package:** `fast_database`

---

## Overview

This package is meant to be imported by **multiple applications** (API workers, migration jobs, analytics) so there is a **single source of truth** for table shapes.

### Layout

| Path | Contents |
|------|----------|
| `fast_database.models` | `Base` and all ORM classes |
| `fast_database.constants.db.table` | `Table` class with `Final[str]` table names |

### Model groups (illustrative)

- **Identity & profile:** `User`, `Profile`, `UserDevice`, `RefreshToken`, lookup tables (`user_type_lk`, `status_lk`, …)
- **Organizations:** `Organization`, `OrganizationMember`, `OrganizationInvite`
- **Subscriptions & billing:** `Subscription`, `UserSubscription`, `Plan`, `PaymentTransaction`, provider `Invoice` (Stripe-style), `Coupon`
- **Conversations:** `Conversation`, `ConversationMessage`
- **Webhooks:** `Webhook`, `WebhookDelivery`
- **Audit:** `TransactionLog`, `AuditLog`
- **Commerce (generic):** `Product`, `Cart`, `CartItem`, `Order`, `OrderItem`, `Shipment`, `ShipmentTrackingLog`
- **Personal ledger (Pure.cam–aligned):** `LedgerWorkspace`, `LedgerTransaction`, debts, goals, EMI, `StellarContract`, … (see source under `models/ledger_*.py`, `stellar_contract.py`)

> **Note:** Some `models/__init__.py` imports assume every submodule exists in your checkout; trim or add stubs if you use a subset.

---

## Installation

```bash
python -m pip install -e ./fast_database
```

**Dependency:** `sqlalchemy>=2,<3`.

---

## Usage

```python
from fast_database.models import Base
from fast_database.models.user import User
from fast_database.constants.table import Table

# Alembic / create_all
# Base.metadata.create_all(engine)
```

Use the same `Base` in **`fast_db`** so Alembic sees every table your app registers.

---

## Conventions

- **Primary keys:** `BigInteger` autoincrement where not otherwise specified
- **External IDs:** `urn` (string) for stable public identifiers
- **Money:** often stored in **minor units** (`*_cents`) or `Numeric`; check each model
- **JSON:** PostgreSQL `JSONB` for flexible metadata (`metadata` column names may be mapped via SQLAlchemy `Column("metadata", JSONB)`)

---

## Development

```bash
cd fast_database
pytest  # if tests are present
```

---

## See also

- [../README.md](../README.md) — monorepo index
- `fast_database/models/README.md` — additional notes if present
