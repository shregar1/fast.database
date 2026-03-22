"""
Ledger savings goal models (Pure.cam).

Maps `Goal`, `GoalContribution`.

Usage:
    >>> from fast_database.models.ledger_goal import LedgerGoal, LedgerGoalContribution
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint

from fast_database.constants.db.table import Table
from fast_database.models import Base


class LedgerGoal(Base):
    """Savings target with optional deadline and category tag."""

    __tablename__ = Table.LEDGER_GOAL
    __table_args__ = (
        UniqueConstraint(
            "ledger_workspace_id",
            "client_goal_id",
            name="uq_ledger_goal_workspace_client",
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
    client_goal_id = Column(String(128), nullable=False)
    name = Column(String(512), nullable=False)
    target_amount = Column(Numeric(18, 6), nullable=False)
    deadline = Column(Date, nullable=True)
    category = Column(String(256), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.client_goal_id,
            "name": self.name,
            "targetAmount": float(self.target_amount) if self.target_amount is not None else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "category": self.category,
        }


class LedgerGoalContribution(Base):
    """Manual contribution toward a goal."""

    __tablename__ = Table.LEDGER_GOAL_CONTRIBUTION
    __table_args__ = (
        UniqueConstraint(
            "ledger_goal_id",
            "client_contribution_id",
            name="uq_ledger_goal_contrib_goal_client",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    ledger_goal_id = Column(
        BigInteger,
        ForeignKey(Table.LEDGER_GOAL + ".id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_contribution_id = Column(String(128), nullable=False)
    client_goal_id = Column(String(128), nullable=False, index=True)
    amount = Column(Numeric(18, 6), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.client_contribution_id,
            "goalId": self.client_goal_id,
            "amount": float(self.amount) if self.amount is not None else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
