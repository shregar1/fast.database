"""
Interview Reminder Model.

SQLAlchemy ORM model for user-scheduled interview reminders. Users set a
scheduled_at (when the interview is) and reminder_minutes_before; a nightly
job sends a notification when the reminder is due (scheduled_at - reminder_minutes_before <= now).

Usage:
    >>> from fast_database.persistence.models.interview_reminder import InterviewReminder
"""



from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String

from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class Reminder(Base):
    """
    User-scheduled reminder.

    Attributes:
        id: Primary key.
        user_id: FK to user (owner).
        scheduled_at: When the reminder is scheduled (UTC).
        reminder_minutes_before: Send reminder this many minutes before scheduled_at.
        title: Optional label (e.g. "Google PM reminder").
        sent_at: When the reminder was sent (NULL until job sends it).
        created_at, updated_at, created_by: Audit.
    """

    __tablename__ = Table.REMINDER

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    reminder_minutes_before = Column(Integer, nullable=False, default=60)
    title = Column(String(256), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "reminder_minutes_before": self.reminder_minutes_before,
            "title": self.title,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
