"""
Payment Transaction Model.

SQLAlchemy ORM model for a single payment charge with a payment provider. One
row per charge: amount, currency, status, provider IDs, optional failure info,
paid_at/refunded_at, and JSONB metadata. Unique on (provider_id, provider_payment_id).

Usage:
    >>> from fast_database.persistence.models.payment_transaction import PaymentTransaction
    >>> # status_id -> payment_status_lk; payment_method_type_id -> payment_method_type_lk
"""



from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class PaymentTransaction(Base):
    """
    Single payment charge (one per successful or attempted charge).

    Tracks amount, currency, status, provider payment id/customer id, optional
    payment method type, failure code/message, and paid_at/refunded_at. txn_metadata
    (DB column "metadata") holds provider-specific payload. Unique per provider
    and provider_payment_id for idempotency.

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        user_id: FK to user.
        provider_id: FK to payment_provider_lk.
        amount_cents, currency: Charge amount.
        status_id: FK to payment_status_lk.
        payment_method_type_id: Optional FK to payment_method_type_lk.
        provider_payment_id, provider_customer_id, provider_payment_method_id: Provider refs.
        failure_code, failure_message: If charge failed.
        paid_at, refunded_at: Lifecycle timestamps.
        txn_metadata: JSONB; DB column "metadata".
        created_at, updated_at, created_by, updated_by: Audit fields.
    """



    __tablename__ = Table.PAYMENT_TRANSACTION
    __table_args__ = (
        UniqueConstraint(
            "provider_id", "provider_payment_id", name="uq_payment_txn_provider_payment"
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    provider_id = Column(
        BigInteger, ForeignKey("payment_provider_lk.id"), nullable=False, index=True
    )
    amount_cents = Column(BigInteger, nullable=False)
    currency = Column(String(8), nullable=False, default="USD")
    status_id = Column(
        BigInteger, ForeignKey("payment_status_lk.id"), nullable=False, index=True
    )
    payment_method_type_id = Column(
        BigInteger, ForeignKey("payment_method_type_lk.id"), nullable=True
    )
    provider_payment_id = Column(String(128), nullable=True, index=True)
    provider_customer_id = Column(String(128), nullable=True, index=True)
    provider_payment_method_id = Column(String(128), nullable=True)
    failure_code = Column(String(64), nullable=True)
    failure_message = Column(String(512), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    txn_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    updated_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    def to_dict(self) -> dict:

        return {
            "urn": self.urn,
            "user_id": self.user_id,
            "provider_id": self.provider_id,
            "amount_cents": self.amount_cents,
            "currency": self.currency,
            "status_id": self.status_id,
            "payment_method_type_id": self.payment_method_type_id,
            "provider_payment_id": self.provider_payment_id,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "refunded_at": self.refunded_at.isoformat() if self.refunded_at else None,
            "metadata": self.txn_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
