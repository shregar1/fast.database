"""
Webhook Models.

SQLAlchemy ORM models for outbound webhooks:
- Webhook: endpoint configuration (URL, secret, subscribed events, enabled).
- WebhookDelivery: delivery log for idempotency and retries.

Used by:
    - Webhook CRUD APIs under /api/v1/webhooks
    - Webhook dispatcher (services/webhooks/dispatcher.py)
    - Repositories (repositories/webhook.py)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.types import JSON

from src.constants.db.table import Table
from src.models import Base


class Webhook(Base):
    """
    Outbound webhook endpoint configuration.

    Attributes:
        id: Primary key.
        user_id: Owner user ID; nullable for global/system webhooks.
        url: Destination URL.
        secret: Signing secret (HMAC SHA256).
        description: Optional label.
        events: List of event types (stored as JSON array of strings).
        enabled: Whether this webhook is active.
        created_at, updated_at: Timestamps.
    """

    __tablename__ = Table.WEBHOOK

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(Table.USER + ".id"), nullable=True, index=True)

    url = Column(String(1024), nullable=False)
    secret = Column(String(255), nullable=False)
    description = Column(String(512), nullable=True)

    # Stored as JSON array to support `.contains([event_type])` queries on Postgres.
    events = Column(JSON, nullable=False)

    enabled = Column(Boolean, nullable=False, default=True, index=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "url": self.url,
            "description": self.description,
            "events": self.events,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class WebhookDelivery(Base):
    """
    Delivery attempt record for an outbound webhook.

    Unique per (webhook_id, event_id) to make deliveries idempotent.
    """

    __tablename__ = Table.WEBHOOK_DELIVERY

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    webhook_id = Column(
        BigInteger,
        ForeignKey(Table.WEBHOOK + ".id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_id = Column(String(128), nullable=False, index=True)
    event_type = Column(String(128), nullable=False, index=True)
    payload = Column(JSON, nullable=True)

    status = Column(String(32), nullable=False, default="pending", index=True)
    attempts = Column(Integer, nullable=False, default=0)

    response_code = Column(Integer, nullable=True)
    error_message = Column(String(512), nullable=True)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)

    __table_args__ = (
        UniqueConstraint("webhook_id", "event_id", name="uq_webhook_delivery_webhook_id_event_id"),
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "webhook_id": self.webhook_id,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "status": self.status,
            "attempts": self.attempts,
            "response_code": self.response_code,
            "error_message": self.error_message,
            "last_attempt_at": self.last_attempt_at.isoformat() if self.last_attempt_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

