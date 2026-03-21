"""
Ledger custom category model (Pure.cam).

Maps `CustomCategory`.

Usage:
    >>> from fastmvc_db_models.models.ledger_custom_category import LedgerCustomCategory
"""

from sqlalchemy import BigInteger, Column, ForeignKey, String, UniqueConstraint

from src.constants.db.table import Table
from src.models import Base


class LedgerCustomCategory(Base):
    """User-defined category label and optional icon key."""

    __tablename__ = Table.LEDGER_CUSTOM_CATEGORY
    __table_args__ = (
        UniqueConstraint(
            "ledger_workspace_id",
            "client_category_id",
            name="uq_ledger_category_workspace_client",
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
    client_category_id = Column(String(128), nullable=False)
    name = Column(String(256), nullable=False)
    icon = Column(String(128), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.client_category_id,
            "name": self.name,
            "icon": self.icon,
        }
