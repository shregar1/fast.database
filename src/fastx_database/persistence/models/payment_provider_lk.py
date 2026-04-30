"""Payment Provider Lookup Model.

SQLAlchemy ORM model for payment providers (e.g. Stripe, Link, Razorpay).
Code is unique; is_active allows disabling a provider. Referenced by
payment_transaction, user_payment_method, invoice.

Usage:
    >>> from fastx_database.persistence.models.payment_provider_lk import PaymentProviderLk
    >>> # code used in integrations (e.g. 'stripe', 'razorpay')
"""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, String

from fastx_database.core.constants.table import Table
from fastx_database.persistence.models import Base


class PaymentProviderLk(Base):
    """Lookup: payment provider (e.g. Stripe, Link, Razorpay).

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        code: Unique provider code.
        name: Display name.
        description: Optional.
        is_active: Whether provider is enabled.
        created_at, updated_at: Timestamps.

    """

    __tablename__ = Table.PAYMENT_PROVIDER_LK

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    code = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(128), nullable=False)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow
    )

    def to_dict(self) -> dict:
        """Execute to_dict operation.

        Returns:
            The result of the operation.
        """
        return {
            "urn": self.urn,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
