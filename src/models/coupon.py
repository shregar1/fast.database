"""
Coupon Model.

SQLAlchemy ORM model for discount codes used at checkout.

Currently used to map internal coupon codes to provider-specific promotion code IDs
(e.g. Stripe promotion code ID) and enforce simple validity windows and redemption limits.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String

from fast_database.constants.db.table import Table
from fast_database.models import Base


class Coupon(Base):
    """
    Discount coupon code.

    Attributes:
        id: Primary key.
        code: Human-facing coupon code (e.g. SAVE20).
        stripe_promotion_code_id: Stripe promotion code identifier (promo_xxx) to apply at checkout.
        is_active: Whether the code can be used.
        valid_from, valid_until: Optional window for validity (UTC).
        max_redemptions: Optional max total redemptions.
        redemptions_count: Current redemption count.
        created_at, updated_at: Timestamps.
    """

    __tablename__ = Table.COUPON

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String(64), nullable=False, unique=True, index=True)

    stripe_promotion_code_id = Column(String(128), nullable=True, index=True)

    is_active = Column(Boolean, nullable=False, default=True, index=True)
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    max_redemptions = Column(Integer, nullable=True)
    redemptions_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "code": self.code,
            "stripe_promotion_code_id": self.stripe_promotion_code_id,
            "is_active": self.is_active,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "max_redemptions": self.max_redemptions,
            "redemptions_count": self.redemptions_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

