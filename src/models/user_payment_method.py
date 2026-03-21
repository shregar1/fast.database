"""
User Payment Method Model.

SQLAlchemy ORM model for saved payment methods (e.g. cards) per user and
provider. One row per (user_id, provider_id, provider_payment_method_id).
Stores last4, brand, expiry, is_default, and is_deleted.

Usage:
    >>> from fastmvc_db_models.models.user_payment_method import UserPaymentMethod
    >>> # payment_method_type_id -> payment_method_type_lk; provider_id -> payment_provider_lk
"""



from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from src.constants.db.table import Table
from src.models import Base


class UserPaymentMethod(Base):
    """
    Saved payment method (e.g. card) for a user at a payment provider.

    Links user, provider, and provider_payment_method_id. Stores display info
    (last4, brand, expiry_month, expiry_year), is_default, and is_deleted.
    Unique on (user_id, provider_id, provider_payment_method_id).

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        user_id: FK to user.
        provider_id: FK to payment_provider_lk.
        payment_method_type_id: FK to payment_method_type_lk.
        provider_payment_method_id: Provider's method ID.
        last4, brand, expiry_month, expiry_year: Display/safety info.
        is_default: Default method for this user/provider.
        is_deleted: Soft-delete flag.
        created_at, updated_at: Timestamps.
    """



    __tablename__ = Table.USER_PAYMENT_METHOD
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "provider_id",
            "provider_payment_method_id",
            name="uq_user_payment_method_user_provider",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    provider_id = Column(
        BigInteger, ForeignKey("payment_provider_lk.id"), nullable=False, index=True
    )
    payment_method_type_id = Column(
        BigInteger, ForeignKey("payment_method_type_lk.id"), nullable=False
    )
    provider_payment_method_id = Column(String(128), nullable=False)
    last4 = Column(String(4), nullable=True)
    brand = Column(String(32), nullable=True)
    expiry_month = Column(Integer, nullable=True)
    expiry_year = Column(Integer, nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "urn": self.urn,
            "user_id": self.user_id,
            "provider_id": self.provider_id,
            "payment_method_type_id": self.payment_method_type_id,
            "provider_payment_method_id": self.provider_payment_method_id,
            "last4": self.last4,
            "brand": self.brand,
            "expiry_month": self.expiry_month,
            "expiry_year": self.expiry_year,
            "is_default": self.is_default,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_dict_masked(self) -> dict:
        """Safe for list response: id, last4, brand, expiry, is_default (no provider_payment_method_id)."""
        return {
            "id": self.id,
            "urn": self.urn,
            "last4": self.last4,
            "brand": self.brand,
            "expiry_month": self.expiry_month,
            "expiry_year": self.expiry_year,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
