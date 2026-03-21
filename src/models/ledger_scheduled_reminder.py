"""
Ledger scheduled reminder model (Pure.cam).

Maps `ScheduledReminder`.

Usage:
    >>> from fastmvc_db_models.models.ledger_scheduled_reminder import LedgerScheduledReminder
"""

from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, UniqueConstraint

from sqlalchemy.dialects.postgresql import JSONB

from src.constants.db.table import Table
from src.models import Base


class LedgerScheduledReminder(Base):
    """Local notification schedule (daily/monthly) with optional EMI link."""

    __tablename__ = Table.LEDGER_SCHEDULED_REMINDER
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "client_reminder_id",
            name="uq_ledger_scheduled_reminder_user_client",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    ledger_workspace_id = Column(
        BigInteger,
        ForeignKey(Table.LEDGER_WORKSPACE + ".id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    client_reminder_id = Column(String(128), nullable=False)
    type = Column(String(16), nullable=False)  # daily | monthly
    title = Column(String(512), nullable=False)
    body = Column(String(2048), nullable=False, default="")
    screen = Column(String(256), nullable=False)
    emi_client_loan_id = Column(String(128), nullable=True)
    hour = Column(Integer, nullable=False)
    minute = Column(Integer, nullable=False)
    day_of_month = Column(Integer, nullable=True)
    identifiers = Column(JSONB, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.client_reminder_id,
            "type": self.type,
            "title": self.title,
            "body": self.body,
            "screen": self.screen,
            "emiId": self.emi_client_loan_id,
            "hour": self.hour,
            "minute": self.minute,
            "dayOfMonth": self.day_of_month,
            "identifiers": self.identifiers or [],
        }
