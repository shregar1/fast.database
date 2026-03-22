"""
Ledger debt and adjustment models (Pure.cam).

Maps `Debt`, `DebtPayment`, `DebtCredit`.

Usage:
    >>> from fast_database.models.ledger_debt import LedgerDebt, LedgerDebtPayment, LedgerDebtCredit
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint

from fast_database.constants.db.table import Table
from fast_database.models import Base


class LedgerDebt(Base):
    """Informal IOU (they owe me / I owe them)."""

    __tablename__ = Table.LEDGER_DEBT
    __table_args__ = (
        UniqueConstraint(
            "ledger_workspace_id",
            "client_debt_id",
            name="uq_ledger_debt_workspace_client",
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
    client_debt_id = Column(String(128), nullable=False)
    name = Column(String(512), nullable=False)
    direction = Column(String(32), nullable=False)  # THEY_OWE_ME | I_OWE_THEM
    initial_amount = Column(Numeric(18, 6), nullable=False)
    currency = Column(String(8), nullable=False, default="INR")
    due_date = Column(Date, nullable=True)
    note = Column(Text, nullable=True)
    phone = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.client_debt_id,
            "urn": self.urn,
            "name": self.name,
            "direction": self.direction,
            "initialAmount": float(self.initial_amount) if self.initial_amount is not None else None,
            "currency": self.currency,
            "dueDate": self.due_date.isoformat() if self.due_date else None,
            "note": self.note,
            "phone": self.phone,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class LedgerDebtPayment(Base):
    """Payment reducing or increasing debt balance."""

    __tablename__ = Table.LEDGER_DEBT_PAYMENT
    __table_args__ = (
        UniqueConstraint(
            "ledger_debt_id",
            "client_debt_payment_id",
            name="uq_ledger_debt_payment_debt_client",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    ledger_debt_id = Column(
        BigInteger,
        ForeignKey(Table.LEDGER_DEBT + ".id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_debt_payment_id = Column(String(128), nullable=False)
    client_debt_id = Column(String(128), nullable=False, index=True)
    amount = Column(Numeric(18, 6), nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=False)
    note = Column(Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.client_debt_payment_id,
            "debtId": self.client_debt_id,
            "amount": float(self.amount) if self.amount is not None else None,
            "paidAt": self.paid_at.isoformat() if self.paid_at else None,
            "note": self.note,
        }


class LedgerDebtCredit(Base):
    """Credit-style adjustment on a debt (lent more / received on credit)."""

    __tablename__ = Table.LEDGER_DEBT_CREDIT
    __table_args__ = (
        UniqueConstraint(
            "ledger_debt_id",
            "client_debt_credit_id",
            name="uq_ledger_debt_credit_debt_client",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    ledger_debt_id = Column(
        BigInteger,
        ForeignKey(Table.LEDGER_DEBT + ".id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_debt_credit_id = Column(String(128), nullable=False)
    client_debt_id = Column(String(128), nullable=False, index=True)
    amount = Column(Numeric(18, 6), nullable=False)
    added_at = Column(DateTime(timezone=True), nullable=False)
    note = Column(Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.client_debt_credit_id,
            "debtId": self.client_debt_id,
            "amount": float(self.amount) if self.amount is not None else None,
            "addedAt": self.added_at.isoformat() if self.added_at else None,
            "note": self.note,
        }
