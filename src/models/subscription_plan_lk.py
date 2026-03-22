"""
Subscription Plan Lookup Model.

SQLAlchemy ORM model for subscription plan definitions: name, number_sessions,
price_usd, description, and optional JSONB features. Referenced by
user_subscription.subscription_plan_id. Seed data defines available plans.

Usage:
    >>> from fast_database.models.subscription_plan_lk import SubscriptionPlanLk
    >>> # number_sessions and price_usd drive billing and limits
"""



from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from fast_database.constants.table import Table
from fast_database.models import Base


class SubscriptionPlanLk(Base):
    """
    Lookup: subscription plan (sessions allowance, price, features).

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        name: Plan name (unique).
        number_sessions: Sessions included in plan.
        price_usd: Price (Numeric).
        description: Optional text.
        features: Optional JSONB (feature flags or list).
        created_at, updated_at: Timestamps.
    """



    __tablename__ = Table.SUBSCRIPTION_PLAN_LK

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    name = Column(String(128), nullable=False, unique=True, index=True)
    number_sessions = Column(Integer, nullable=False)
    price_usd = Column(Numeric(10, 2), nullable=False)
    description = Column(Text, nullable=True)
    features = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:

        return {
            "urn": self.urn,
            "name": self.name,
            "number_sessions": self.number_sessions,
            "price_usd": str(self.price_usd) if self.price_usd is not None else None,
            "description": self.description,
            "features": self.features,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
