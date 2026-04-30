"""Subscription Model.

SQLAlchemy ORM model for subscription lifecycle: user, plan_code, status,
start/end dates, grace period. Used by v1 subscription API and billing.

Usage:
    >>> from fastx_database.persistence.models.subscription import Subscription
"""

from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, ForeignKey, String

from fastx_database.core.constants.db import StringLength
from fastx_database.core.constants.status import Status
from fastx_database.core.constants.table import Table
from fastx_database.persistence.models import Base


class Subscription(Base):
    """Subscription lifecycle record (user, plan, status, period).

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        user_id: FK to user.
        organization_id: Optional FK to organization.
        plan_code: Plan identifier (e.g. free, pro).
        status: ACTIVE, trialing, past_due, CANCELLED, etc.
        start_date, end_date: Billing period.
        grace_period_ends_at: Optional end of grace (for past_due).
        is_deleted: Soft delete flag.
        created_at, updated_at, created_by, updated_by: Audit fields.

    """

    __tablename__ = Table.SUBSCRIPTION

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(StringLength.URN), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    organization_id = Column(BigInteger, nullable=True, index=True)
    plan_code = Column(String(StringLength.CODE), nullable=False, index=True)
    status = Column(String(StringLength.STATUS), nullable=False, default=Status.ACTIVE.upper(), index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    grace_period_ends_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    created_by = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow
    )
    updated_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)
