"""
Payment Method Type Lookup Model.

SQLAlchemy ORM model for payment method types (e.g. card, upi, netbanking,
wallet). Code is unique. Referenced by payment_transaction.payment_method_type_id
and user_payment_method.payment_method_type_id.

Usage:
    >>> from fastmvc_db_models.models.payment_method_type_lk import PaymentMethodTypeLk
    >>> # Identifies type of saved or used payment method
"""



from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String

from fastmvc_db_models.constants.db.table import Table
from fastmvc_db_models.models import Base


class PaymentMethodTypeLk(Base):
    """
    Lookup: payment method type (card, UPI, netbanking, wallet, etc.).

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        code: Unique code.
        description: Human-readable label.
        created_at, updated_at: Timestamps.
    """



    __tablename__ = Table.PAYMENT_METHOD_TYPE_LK

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    code = Column(String(64), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:

        return {
            "urn": self.urn,
            "code": self.code,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
