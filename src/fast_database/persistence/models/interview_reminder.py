"""
Alias for the interview reminder ORM class (table `reminder`).

The implementation lives in `reminder.py` as `Reminder`.
"""

from fast_database.persistence.models.reminder import Reminder as InterviewReminder

__all__ = ["InterviewReminder"]
