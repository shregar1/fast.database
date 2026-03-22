"""
Subscription Model.

SQLAlchemy ORM model for subscription lifecycle: user, plan_code, status,
start/end dates, grace period. Used by v1 subscription API and billing.

Usage:
    >>> from fast_database.models.subscription import Subscription
"""



from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, ForeignKey, String

from fast_database.constants.table import Table
from fast_database.models import Base


class Subscription(Base):
    """
    Subscription lifecycle record (user, plan, status, period).

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
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    organization_id = Column(BigInteger, nullable=True, index=True)
    plan_code = Column(String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="ACTIVE", index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    grace_period_ends_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    updated_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    def to_dict(self) -> dict:

        return {
            "id": self.id,
            "urn": self.urn,
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "plan_code": self.plan_code,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "grace_period_ends_at": (
                self.grace_period_ends_at.isoformat() if self.grace_period_ends_at else None
            ),
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
