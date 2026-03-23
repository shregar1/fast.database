"""
Usage counters for quotas, metering, and fair-use analytics.

Increment idempotently in application code (e.g. ``INSERT ... ON CONFLICT`` in PostgreSQL
or select-for-update). One row per (user, metric, period_start) for daily windows.

Usage:
    >>> from fast_database.persistence.models.usage_counter import UsageCounter
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, String, UniqueConstraint

from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class UsageCounter(Base):
    """
    Aggregated usage bucket (typically UTC calendar day).

    Attributes:
        id: Primary key.
        user_id: Scoped user (FK ``user.id``); required for per-user metering.
        organization_id: Optional workspace scope (FK ``organizations.id``) for org quotas.
        metric_key: Stable name, e.g. ``api.requests``, ``llm.tokens``, ``storage.bytes``.
        period_start: Start of bucket (UTC date); use date-only for daily rollups.
        count: Monotonic counter for the window.
        updated_at: Last increment time (UTC).
    """

    __tablename__ = Table.USAGE_COUNTER
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "metric_key",
            "period_start",
            name="uq_usage_counter_user_metric_period",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger,
        ForeignKey(f"{Table.USER}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id = Column(
        BigInteger,
        ForeignKey(f"{Table.ORGANIZATION}.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    metric_key = Column(String(128), nullable=False, index=True)
    period_start = Column(Date, nullable=False, index=True)
    count = Column(BigInteger, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
