"""
Payment Refund Model.

SQLAlchemy ORM model for a refund against a payment transaction. Each row is
one refund: amount, status, optional provider_refund_id and reason, plus
metadata. Unique on (payment_transaction_id, provider_refund_id).

Usage:
    >>> from fastmvc_db_models.models.payment_refund import PaymentRefund
    >>> # status_id -> payment_status_lk; payment_transaction_id -> payment_transaction
"""



from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from src.constants.db.table import Table
from src.models import Base


class PaymentRefund(Base):
    """
    Refund against a single payment transaction.

    Tracks refund amount, status, optional provider_refund_id for reconciliation,
    reason, and JSONB metadata. One transaction can have multiple refund rows
    (partial refunds). Unique per transaction and provider_refund_id.

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        payment_transaction_id: FK to payment_transaction.
        amount_cents: Refund amount in cents.
        status_id: FK to payment_status_lk.
        provider_refund_id: Provider's refund ID (optional).
        reason: Optional refund reason.
        refund_metadata: JSONB; DB column "metadata".
        created_at, updated_at, created_by, updated_by: Audit fields.
    """



    __tablename__ = Table.PAYMENT_REFUND
    __table_args__ = (
        UniqueConstraint(
            "payment_transaction_id",
            "provider_refund_id",
            name="uq_payment_refund_txn_provider",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    payment_transaction_id = Column(
        BigInteger,
        ForeignKey("payment_transaction.id"),
        nullable=False,
        index=True,
    )
    amount_cents = Column(BigInteger, nullable=False)
    status_id = Column(
        BigInteger, ForeignKey("payment_status_lk.id"), nullable=False, index=True
    )
    provider_refund_id = Column(String(128), nullable=True, index=True)
    reason = Column(String(255), nullable=True)
    refund_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    updated_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    def to_dict(self) -> dict:

        return {
            "urn": self.urn,
            "payment_transaction_id": self.payment_transaction_id,
            "amount_cents": self.amount_cents,
            "status_id": self.status_id,
            "provider_refund_id": self.provider_refund_id,
            "reason": self.reason,
            "metadata": self.refund_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
