"""
Stellar hourly contract models (Pure.cam SQLite parity).

Maps `contracts`, `contract_hours`, `contract_payments` from API_AND_DATA_REFERENCE.md.

Usage:
    >>> from fast_database.models.stellar_contract import (
    ...     StellarContract,
    ...     StellarContractHours,
    ...     StellarContractPayment,
    ... )
"""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint

from sqlalchemy.dialects.postgresql import JSONB

from fast_database.constants.table import Table
from fast_database.models import Base


class StellarContract(Base):
    """Client / company contract with hourly billing rate (per workspace)."""

    __tablename__ = Table.STELLAR_CONTRACT
    __table_args__ = (
        UniqueConstraint(
            "ledger_workspace_id",
            "client_contract_id",
            name="uq_stellar_contract_workspace_client",
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
    client_contract_id = Column(String(128), nullable=True)
    organisation = Column(String(512), nullable=False)
    billing_rate = Column(Numeric(18, 6), nullable=False)
    currency = Column(String(8), nullable=False, default="INR")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    tags = Column(JSONB, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.client_contract_id or str(self.id),
            "organisation": self.organisation,
            "billing_rate": float(self.billing_rate) if self.billing_rate is not None else None,
            "currency": self.currency,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "notes": self.notes,
            "tags": self.tags,
        }


class StellarContractHours(Base):
    """Hours logged per contract for a calendar month."""

    __tablename__ = Table.STELLAR_CONTRACT_HOURS
    __table_args__ = (
        UniqueConstraint(
            "stellar_contract_id",
            "month",
            "year",
            name="uq_stellar_contract_hours_month_year",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    stellar_contract_id = Column(
        BigInteger,
        ForeignKey(Table.STELLAR_CONTRACT + ".id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    month = Column(BigInteger, nullable=False)
    year = Column(BigInteger, nullable=False)
    hours = Column(Numeric(18, 6), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "month": self.month,
            "year": self.year,
            "hours": float(self.hours) if self.hours is not None else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class StellarContractPayment(Base):
    """Payment recorded against a contract."""

    __tablename__ = Table.STELLAR_CONTRACT_PAYMENT

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    stellar_contract_id = Column(
        BigInteger,
        ForeignKey(Table.STELLAR_CONTRACT + ".id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount = Column(Numeric(18, 6), nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "amount": float(self.amount) if self.amount is not None else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
