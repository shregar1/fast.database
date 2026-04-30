"""User notification preference: per-user toggles for channel and category.

One row per (user_id, channel, category); enabled = True/False.
Channels: email, push, slack. Categories: billing, security, product.
"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)

from fastx_database.core.constants.db import StringLength
from fastx_database.core.constants.table import Table
from fastx_database.persistence.models import Base


class UserNotificationPreference(Base):
    """Per-user preference: enable/disable a channel for a category.

    Unique on (user_id, channel, category). Default when missing: enabled=True.
    """

    __tablename__ = Table.USER_NOTIFICATION_PREFERENCE
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "channel",
            "category",
            name="uq_user_notification_preference_user_channel_category",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    channel = Column(String(StringLength.STATUS), nullable=False, index=True)
    category = Column(String(StringLength.STATUS), nullable=False, index=True)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow
    )

    def to_dict(self) -> dict:
        """Execute to_dict operation.

        Returns:
            The result of the operation.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "channel": self.channel,
            "category": self.category,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
