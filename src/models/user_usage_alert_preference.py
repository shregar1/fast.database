"""
User usage alert preference: threshold and channels for usage alerts (e.g. email at 80% of plan).

One row per user (user_id unique). Stores threshold_percent and channels (email, in_app, slack).
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from fast_database.constants.table import Table
from fast_database.models import Base


class UserUsageAlertPreference(Base):
    """
    Per-user usage alert preference: at what % of plan to alert, and which channels.

    user_id unique. threshold_percent: 1–100 (e.g. 80 = alert at 80% of plan).
    channels: list of strings, e.g. ["email", "in_app", "slack"].
    """

    __tablename__ = Table.USER_USAGE_ALERT_PREFERENCE
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_usage_alert_preference_user_id"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, unique=True, index=True)
    threshold_percent = Column(Float, nullable=False, default=80.0)  # 1–100
    channels = Column(JSONB, nullable=False, server_default="[]")  # ["email", "in_app", "slack"]
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "threshold_percent": self.threshold_percent,
            "channels": self.channels or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
