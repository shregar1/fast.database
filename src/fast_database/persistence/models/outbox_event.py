"""
Transactional outbox — publish domain events after commit without losing messages.

Workers poll or subscribe to rows where ``published_at`` is null; on success set
``published_at``; on failure increment ``retry_count`` and set ``last_error``.

Usage:
    >>> from fast_database.persistence.models.outbox_event import OutboxEvent
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text

from sqlalchemy.dialects.postgresql import JSONB

from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class OutboxEvent(Base):
    """
    Outbox row written in the same DB transaction as business data.

    Attributes:
        id: Primary key.
        aggregate_type: Entity name (e.g. ``User``, ``Order``).
        aggregate_id: Stable id (string to support ULID/UUID).
        event_type: e.g. ``user.created``, ``order.paid``.
        payload: JSON event body.
        destination: Topic name, queue name, or webhook id (app-defined).
        headers: Optional routing/metadata JSON.
        created_at: When the row was inserted (UTC).
        published_at: When a worker successfully handed off the message; null if pending.
        retry_count: Failed delivery attempts.
        last_error: Last broker/HTTP error text for debugging.
    """

    __tablename__ = Table.OUTBOX_EVENT

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    aggregate_type = Column(String(64), nullable=False, index=True)
    aggregate_id = Column(String(128), nullable=False, index=True)
    event_type = Column(String(128), nullable=False, index=True)
    payload = Column(JSONB, nullable=False)
    destination = Column(String(256), nullable=False, index=True)
    headers = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    retry_count = Column(Integer, nullable=False, default=0)
    last_error = Column(Text, nullable=True)
