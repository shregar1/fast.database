"""
Idempotency record — deduplicate mutating API calls and optionally cache responses.

Compute ``key_hash`` = HMAC/SHA-256 over (user or actor id, scope, client idempotency key)
so the same logical request replays the same outcome within ``expires_at``.

Usage:
    >>> from fast_database.models.idempotency_record import IdempotencyRecord
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text

from sqlalchemy.dialects.postgresql import JSONB

from fast_database.constants.table import Table
from fast_database.models import Base


class IdempotencyRecord(Base):
    """
    Stores idempotency keys for safe retries (payments, orders, webhooks).

    Attributes:
        id: Primary key.
        key_hash: Unique hash identifying the idempotent operation (see module docstring).
        user_id: Optional owner (FK ``user.id``); null for service/API-key-only flows.
        scope: Logical operation (e.g. ``payment.charge``, ``order.create``).
        response_status: Cached HTTP or app status from first execution.
        response_body: Cached JSON body for replay (optional; omit large payloads in prod).
        created_at: First request time.
        expires_at: After this time the row may be deleted and a new request allowed.
    """

    __tablename__ = Table.IDEMPOTENCY_RECORD

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    key_hash = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey(f"{Table.USER}.id", ondelete="SET NULL"), nullable=True, index=True)
    scope = Column(String(128), nullable=False, index=True)
    response_status = Column(Integer, nullable=True)
    response_body = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
