"""
Ledger budget model (Pure.cam).

Maps `Budget` — category cap or total-expense cap (`category` empty string).

Usage:
    >>> from fast_database.persistence.models.ledger_budget import LedgerBudget
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Numeric, String, UniqueConstraint

from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class LedgerBudget(Base):
    """Spending cap for a category or overall expenses for a period."""

    __tablename__ = Table.LEDGER_BUDGET
    __table_args__ = (
        UniqueConstraint(
            "ledger_workspace_id",
            "client_budget_id",
            name="uq_ledger_budget_workspace_client",
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
    client_budget_id = Column(String(128), nullable=False)
    category = Column(String(256), nullable=False, default="")
    limit_amount = Column(Numeric(18, 6), nullable=False)
    period = Column(String(16), nullable=False)  # MONTHLY | WEEKLY
    alert_at_percent = Column(Numeric(9, 4), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "urn": self.urn,
            "user_id": self.user_id,
            "ledger_workspace_id": self.ledger_workspace_id,
            "client_budget_id": self.client_budget_id,
            "category": self.category,
            "limit": float(self.limit_amount) if self.limit_amount is not None else None,
            "period": self.period,
            "alertAtPercent": float(self.alert_at_percent) if self.alert_at_percent is not None else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
