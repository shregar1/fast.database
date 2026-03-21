"""
User Subscription Model.

SQLAlchemy ORM model linking a user to a subscription plan and a billing period.
Stores start/end dates, usage (number_of_session_used), active flag, and the
payment transaction that created the subscription.

Usage:
    >>> from fastmvc_db_models.models.user_subscription import UserSubscription
    >>> # subscription_plan_id -> subscription_plan_lk; one payment_transaction per subscription
"""



from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String

from src.constants.db.table import Table
from src.models import Base


class UserSubscription(Base):
    """
    User's subscription to a plan for a given billing period.

    Links user, plan (subscription_plan_lk), and the payment transaction that
    paid for it. number_of_session_used tracks consumption; is_active indicates
    whether the subscription is currently valid (e.g. within end_date).

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        user_id: FK to user.
        subscription_plan_id: FK to subscription_plan_lk.
        number_of_session_used: Sessions consumed in this period.
        start_date, end_date: Billing period.
        is_active: Whether subscription is currently active.
        payment_transaction_id: FK to payment_transaction (unique).
        created_at, updated_at, created_by, updated_by: Audit fields.
    """



    __tablename__ = Table.USER_SUBSCRIPTION

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    subscription_plan_id = Column(
        BigInteger, ForeignKey("subscription_plan_lk.id"), nullable=False, index=True
    )
    number_of_session_used = Column(Integer, nullable=False, default=0)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    payment_transaction_id = Column(
        BigInteger,
        ForeignKey("payment_transaction.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    updated_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    def to_dict(self) -> dict:

        return {
            "urn": self.urn,
            "user_id": self.user_id,
            "subscription_plan_id": self.subscription_plan_id,
            "number_of_session_used": self.number_of_session_used,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "is_active": self.is_active,
            "payment_transaction_id": self.payment_transaction_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
