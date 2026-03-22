"""
Ledger EMI loan model (Pure.cam).

Maps `EmiLoan`.

Usage:
    >>> from fast_database.models.ledger_emi_loan import LedgerEmiLoan
"""

from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint

from fast_database.constants.table import Table
from fast_database.models import Base


class LedgerEmiLoan(Base):
    """Loan / EMI schedule tracker with optional reminders."""

    __tablename__ = Table.LEDGER_EMI_LOAN
    __table_args__ = (
        UniqueConstraint(
            "ledger_workspace_id",
            "client_emi_loan_id",
            name="uq_ledger_emi_workspace_client",
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
    client_emi_loan_id = Column(String(128), nullable=False)
    name = Column(String(512), nullable=False)
    lender = Column(String(512), nullable=True)
    principal_total = Column(Numeric(18, 6), nullable=True)
    monthly_emi = Column(Numeric(18, 6), nullable=False)
    total_months = Column(Integer, nullable=False)
    paid_months = Column(Integer, nullable=False, default=0)
    currency = Column(String(8), nullable=False, default="INR")
    start_date = Column(Date, nullable=True)
    note = Column(Text, nullable=True)
    reminder_enabled = Column(Boolean, nullable=False, default=False)
    reminder_day_of_month = Column(Integer, nullable=True)
    reminder_hour = Column(Integer, nullable=True)
    reminder_minute = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.client_emi_loan_id,
            "name": self.name,
            "lender": self.lender,
            "principalTotal": float(self.principal_total) if self.principal_total is not None else None,
            "monthlyEmi": float(self.monthly_emi) if self.monthly_emi is not None else None,
            "totalMonths": self.total_months,
            "paidMonths": self.paid_months,
            "currency": self.currency,
            "startDate": self.start_date.isoformat() if self.start_date else None,
            "note": self.note,
            "reminderEnabled": self.reminder_enabled,
            "reminderDayOfMonth": self.reminder_day_of_month,
            "reminderHour": self.reminder_hour,
            "reminderMinute": self.reminder_minute,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
