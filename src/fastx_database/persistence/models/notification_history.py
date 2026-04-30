"""Notification history model for in-app "last 30 days" view.

Persisted notifications per user; list via GET /me/notifications.
"""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String

from fastx_database.core.constants.db import StringLength
from fastx_database.core.constants.status import Category, Channel
from fastx_database.core.constants.table import Table
from fastx_database.persistence.models import Base


class NotificationHistory(Base):
    """One row per in-app notification for a user (last 30 days or configurable).

    channel: in_app, email, push, slack (for display).
    category: billing, security, product (for filtering).
    read_at: when the user marked it read (null = unread).
    """

    __tablename__ = Table.NOTIFICATION_HISTORY

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    channel = Column(String(StringLength.STATUS), nullable=False, default=Channel.IN_APP, index=True)
    category = Column(String(StringLength.STATUS), nullable=False, default=Category.PRODUCT, index=True)
    title = Column(String(StringLength.NAME), nullable=True)
    body = Column(String(StringLength.LONG_TEXT), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
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
            "title": self.title,
            "body": self.body,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
