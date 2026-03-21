"""
Ledger linked account model (Pure.cam).

Maps `LinkedAccount` — SMS/notification import rules.

Usage:
    >>> from fastmvc_db_models.models.ledger_linked_account import LedgerLinkedAccount
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, UniqueConstraint

from fastmvc_db_models.constants.db.table import Table
from fastmvc_db_models.models import Base


class LedgerLinkedAccount(Base):
    """Rule matching sender/body patterns to categorize imported transactions."""

    __tablename__ = Table.LEDGER_LINKED_ACCOUNT
    __table_args__ = (
        UniqueConstraint(
            "ledger_workspace_id",
            "client_linked_account_id",
            name="uq_ledger_linked_workspace_client",
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
    client_linked_account_id = Column(String(128), nullable=False)
    name = Column(String(512), nullable=False)
    provider_label = Column(String(256), nullable=False)
    sender_address_pattern = Column(String(512), nullable=False)
    body_must_contain = Column(String(512), nullable=False, default="")
    default_category = Column(String(256), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "urn": self.urn,
            "user_id": self.user_id,
            "ledger_workspace_id": self.ledger_workspace_id,
            "client_linked_account_id": self.client_linked_account_id,
            "name": self.name,
            "provider_label": self.provider_label,
            "sender_address_pattern": self.sender_address_pattern,
            "body_must_contain": self.body_must_contain,
            "default_category": self.default_category,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
