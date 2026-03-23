"""
Ledger recurring transaction model (Pure.cam).

Maps `RecurringTransaction`.

Usage:
    >>> from fast_database.persistence.models.ledger_recurring_transaction import LedgerRecurringTransaction
"""

from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint

from sqlalchemy.dialects.postgresql import JSONB

from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class LedgerRecurringTransaction(Base):
    """Scheduled repeating income/expense (rent, subscriptions)."""

    __tablename__ = Table.LEDGER_RECURRING_TRANSACTION
    __table_args__ = (
        UniqueConstraint(
            "ledger_workspace_id",
            "client_recurring_id",
            name="uq_ledger_recurring_workspace_client",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    ledger_workspace_id = Column(
        BigInteger,
        ForeignKey(Table.LEDGER_WORKSPACE + ".id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_recurring_id = Column(String(128), nullable=False)
    type = Column(String(16), nullable=False)
    amount = Column(Numeric(18, 6), nullable=False)
    category = Column(String(256), nullable=False, default="")
    note = Column(Text, nullable=True)
    tags = Column(JSONB, nullable=True)
    frequency = Column(String(16), nullable=False)  # WEEKLY | MONTHLY
    next_due_date = Column(Date, nullable=False, index=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "urn": self.urn,
            "user_id": self.user_id,
            "ledger_workspace_id": self.ledger_workspace_id,
            "client_recurring_id": self.client_recurring_id,
            "type": self.type,
            "amount": float(self.amount) if self.amount is not None else None,
            "category": self.category,
            "note": self.note,
            "tags": self.tags,
            "frequency": self.frequency,
            "nextDueDate": self.next_due_date.isoformat() if self.next_due_date else None,
        }
