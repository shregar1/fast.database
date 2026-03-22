"""
Notification history model for in-app "last 30 days" view.

Persisted notifications per user; list via GET /me/notifications.
"""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String

from fast_database.constants.db.table import Table
from fast_database.models import Base


class NotificationHistory(Base):
    """
    One row per in-app notification for a user (last 30 days or configurable).

    channel: in_app, email, push, slack (for display).
    category: billing, security, product (for filtering).
    read_at: when the user marked it read (null = unread).
    """

    __tablename__ = Table.NOTIFICATION_HISTORY

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    channel = Column(String(32), nullable=False, default="in_app", index=True)
    category = Column(String(32), nullable=False, default="product", index=True)
    title = Column(String(256), nullable=True)
    body = Column(String(2048), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def to_dict(self) -> dict:
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
