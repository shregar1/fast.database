"""Ledger transaction model (Pure.cam).

Maps `Transaction` in API_AND_DATA_REFERENCE.md (sync API).

Usage:
    >>> from fastx_database.persistence.models.ledger_transaction import LedgerTransaction
"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.dialects.postgresql import JSONB

from fastx_database.core.constants.currency import Currency
from fastx_database.core.constants.db import StringLength
from fastx_database.core.constants.status import LedgerType, SourceType
from fastx_database.core.constants.table import Table
from fastx_database.persistence.models import Base


class LedgerTransaction(Base):
    """Income or expense line with optional category splits and SMS link.

    `client_transaction_id` matches the mobile `Transaction.id` for idempotent sync.
    """

    __tablename__ = Table.LEDGER_TRANSACTION
    __table_args__ = (
        UniqueConstraint(
            "ledger_workspace_id",
            "client_transaction_id",
            name="uq_ledger_txn_workspace_client",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(StringLength.URN), nullable=False, unique=True, index=True)
    user_id = Column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ledger_workspace_id = Column(
        BigInteger,
        ForeignKey(Table.LEDGER_WORKSPACE + ".id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_transaction_id = Column(String(StringLength.URN), nullable=False)
    type = Column(String(StringLength.CODE), nullable=False, default=LedgerType.EXPENSE, index=True)  # INCOME | EXPENSE
    amount = Column(Numeric(18, 6), nullable=False)
    category = Column(String(StringLength.NAME), nullable=False, default="")
    note = Column(Text, nullable=True)
    tags = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)
    source = Column(
        String(StringLength.STATUS), nullable=False, default=SourceType.MANUAL
    )  # MANUAL | SMS | NOTIFICATION
    linked_account_client_id = Column(String(StringLength.URN), nullable=True)
    currency = Column(String(StringLength.CODE), nullable=True, default=Currency.INR)
    splits = Column(JSONB, nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self) -> dict:
        """Execute to_dict operation.

        Returns:
            The result of the operation.
        """
        return {
            "id": self.id,
            "urn": self.urn,
            "user_id": self.user_id,
            "ledger_workspace_id": self.ledger_workspace_id,
            "client_transaction_id": self.client_transaction_id,
            "type": self.type,
            "amount": float(self.amount) if self.amount is not None else None,
            "category": self.category,
            "note": self.note,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "source": self.source,
            "linked_account_client_id": self.linked_account_client_id,
            "currency": self.currency,
            "splits": self.splits,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
