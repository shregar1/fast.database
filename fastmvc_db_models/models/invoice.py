"""
Invoice Model.

SQLAlchemy ORM model for billing invoices. Each row is an invoice from a
payment provider, linked to a user and optionally to a payment transaction
or user subscription. Unique on (provider_id, external_id) for idempotency.

Usage:
    >>> from fastmvc_db_models.models.invoice import Invoice
    >>> # amount_cents and currency; status_id references status_lk
"""



from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from fastmvc_db_models.constants.db.table import Table
from fastmvc_db_models.models import Base


# Schema table name is "invoice" (singular)
_INVOICE_TABLE = "invoice"


class Invoice(Base):
    """
    Billing invoice from a payment provider, tied to user and optional txn/subscription.

    Represents an invoice record (e.g. from Stripe): amount, currency, status,
    optional period (period_start, period_end), and external_id for provider
    reconciliation. Unique constraint on (provider_id, external_id).

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        user_id: FK to user.
        payment_transaction_id: Optional FK to payment_transaction.
        user_subscription_id: Optional FK to user_subscription.
        provider_id: FK to payment_provider_lk.
        amount_cents, currency: Invoice amount.
        status_id: FK to status_lk.
        external_id: Provider's invoice ID.
        period_start, period_end: Optional billing period.
        created_at, updated_at: Timestamps.
    """



    __tablename__ = _INVOICE_TABLE
    __table_args__ = (
        UniqueConstraint("provider_id", "external_id", name="uq_invoice_provider_external"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    payment_transaction_id = Column(
        BigInteger, ForeignKey("payment_transaction.id"), nullable=True
    )
    user_subscription_id = Column(
        BigInteger, ForeignKey("user_subscription.id"), nullable=True
    )
    provider_id = Column(
        BigInteger, ForeignKey("payment_provider_lk.id"), nullable=True, index=True
    )
    amount_cents = Column(BigInteger, nullable=False)
    currency = Column(String(8), nullable=False)
    status_id = Column(BigInteger, ForeignKey("status_lk.id"), nullable=False, index=True)
    external_id = Column(String(128), nullable=True, index=True)
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:

        return {
            "urn": self.urn,
            "user_id": self.user_id,
            "payment_transaction_id": self.payment_transaction_id,
            "user_subscription_id": self.user_subscription_id,
            "provider_id": self.provider_id,
            "amount_cents": self.amount_cents,
            "currency": self.currency,
            "status_id": self.status_id,
            "external_id": self.external_id,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
