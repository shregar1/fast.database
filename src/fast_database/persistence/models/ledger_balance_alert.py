"""
Ledger balance alert model (Pure.cam).

Maps `BalanceAlert` — at most one row per workspace (sync payload).

Usage:
    >>> from fast_database.persistence.models.ledger_balance_alert import LedgerBalanceAlert
"""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Numeric, String, UniqueConstraint

from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class LedgerBalanceAlert(Base):
    """Notify when balance drops below threshold."""

    __tablename__ = Table.LEDGER_BALANCE_ALERT
    __table_args__ = (UniqueConstraint("ledger_workspace_id", name="uq_ledger_balance_alert_workspace"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    ledger_workspace_id = Column(
        BigInteger,
        ForeignKey(Table.LEDGER_WORKSPACE + ".id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    client_balance_alert_id = Column(String(128), nullable=True)
    threshold = Column(Numeric(18, 6), nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "urn": self.urn,
            "user_id": self.user_id,
            "ledger_workspace_id": self.ledger_workspace_id,
            "client_balance_alert_id": self.client_balance_alert_id,
            "threshold": float(self.threshold) if self.threshold is not None else None,
            "enabled": self.enabled,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
