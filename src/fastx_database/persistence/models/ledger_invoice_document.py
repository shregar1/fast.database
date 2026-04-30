"""Ledger invoice/bill document and business info (Pure.cam).

Maps `Invoice` and `BusinessInfo` from API_AND_DATA_REFERENCE.md. Distinct from
provider billing `Invoice` (Stripe) in `invoice.py`.

Usage:
    >>> from fastx_database.persistence.models.ledger_invoice_document import (
    ...     LedgerInvoiceDocument,
    ...     LedgerBusinessInfo,
    ... )
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
from fastx_database.core.constants.table import Table
from fastx_database.persistence.models import Base


class LedgerInvoiceDocument(Base):
    """User-generated invoice or bill with line items stored as JSON."""

    __tablename__ = Table.LEDGER_INVOICE_DOCUMENT
    __table_args__ = (
        UniqueConstraint(
            "ledger_workspace_id",
            "client_invoice_id",
            name="uq_ledger_invoice_document_workspace_client",
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
    client_invoice_id = Column(String(StringLength.URN), nullable=False)
    number = Column(String(StringLength.CODE), nullable=False)
    type = Column(String(StringLength.CODE), nullable=False)  # invoice | bill
    date = Column(DateTime(timezone=True), nullable=False)
    from_name = Column(String(StringLength.DESCRIPTION), nullable=False)
    from_address = Column(Text, nullable=True)
    from_phone = Column(String(StringLength.PHONE), nullable=True)
    from_email = Column(String(StringLength.EMAIL), nullable=True)
    to_name = Column(String(StringLength.DESCRIPTION), nullable=False)
    to_address = Column(Text, nullable=True)
    to_phone = Column(String(StringLength.PHONE), nullable=True)
    to_email = Column(String(StringLength.EMAIL), nullable=True)
    line_items = Column(JSONB, nullable=False)
    tax_percent = Column(Numeric(9, 4), nullable=True)
    notes = Column(Text, nullable=True)
    currency = Column(String(StringLength.CODE), nullable=False, default=Currency.INR)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    def to_dict(self) -> dict:
        """Execute to_dict operation.

        Returns:
            The result of the operation.
        """
        return {
            "id": self.client_invoice_id,
            "number": self.number,
            "type": self.type,
            "date": self.date.isoformat() if self.date else None,
            "fromName": self.from_name,
            "fromAddress": self.from_address,
            "fromPhone": self.from_phone,
            "fromEmail": self.from_email,
            "toName": self.to_name,
            "toAddress": self.to_address,
            "toPhone": self.to_phone,
            "toEmail": self.to_email,
            "lineItems": self.line_items,
            "taxPercent": float(self.tax_percent)
            if self.tax_percent is not None
            else None,
            "notes": self.notes,
            "currency": self.currency,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class LedgerBusinessInfo(Base):
    """Seller block for invoices (`ledger-invoice-business-info` — one row per user)."""

    __tablename__ = Table.LEDGER_BUSINESS_INFO
    __table_args__ = (UniqueConstraint("user_id", name="uq_ledger_business_info_user"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(StringLength.URN), nullable=False, unique=True, index=True)
    user_id = Column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    business_json = Column(JSONB, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow
    )

    def to_dict(self) -> dict:
        """Execute to_dict operation.

        Returns:
            The result of the operation.
        """
        return self.business_json if isinstance(self.business_json, dict) else {}
