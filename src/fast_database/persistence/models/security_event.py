"""
Security-relevant events for monitoring, alerting, and post-incident review.

Complements :class:`~fast_database.persistence.models.user_login_event.UserLoginEvent` (auth attempts)
with higher-level signals: lockouts, admin actions, anomaly flags.

Usage:
    >>> from fast_database.persistence.models.security_event import SecurityEvent
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text

from sqlalchemy.dialects.postgresql import JSONB

from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class SecurityEvent(Base):
    """
    Append-only security event (do not update rows; insert new state changes).

    Attributes:
        id: Primary key.
        user_id: Affected user if applicable (FK ``user.id``); null for global/system.
        actor_user_id: Who caused the event (admin id); optional.
        event_type: Stable code, e.g. ``account.locked``, ``password.changed``, ``api_key.revoked``.
        severity: ``info``, ``warning``, ``critical``.
        source_ip: Client IP or anonymized hash per policy.
        context: JSON metadata (geo, device id, rule id) — avoid PII unless required.
        created_at: Event time (UTC).
    """

    __tablename__ = Table.SECURITY_EVENT

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger,
        ForeignKey(f"{Table.USER}.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    actor_user_id = Column(
        BigInteger,
        ForeignKey(f"{Table.USER}.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_type = Column(String(64), nullable=False, index=True)
    severity = Column(String(16), nullable=False, default="info", index=True)
    source_ip = Column(String(64), nullable=True)
    context = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
