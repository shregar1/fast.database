"""
Interview Reminder Repository.

CRUD and list_due_for_reminder for InterviewReminder (user-scheduled
interview reminders). Used by the interview-reminder API and the
nightly reminder job.
"""



from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from fast_repositories.repository import IRepository
from fast_database.models.interview_reminder import InterviewReminder


class InterviewReminderRepository(IRepository):
    def __init__(
        self,
        session: Session | None = None,
        *,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            model=InterviewReminder,
            cache=None,
        )
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    @session.setter
    def session(self, value: Session) -> None:
        self._session = value

    def create(
        self,
        user_id: int,
        scheduled_at: datetime,
        reminder_minutes_before: int = 60,
        title: str | None = None,
        created_by: int | None = None,
    ) -> InterviewReminder:
        created_by = created_by or user_id
        record = InterviewReminder(
            user_id=user_id,
            scheduled_at=scheduled_at,
            reminder_minutes_before=reminder_minutes_before,
            title=title,
            sent_at=None,
            created_by=created_by,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        self.logger.info("Created interview reminder id=%s user_id=%s", record.id, user_id)
        return record

    def get_by_id(self, reminder_id: int, user_id: int | None = None) -> InterviewReminder | None:
        q = self.session.query(InterviewReminder).filter(InterviewReminder.id == reminder_id)
        if user_id is not None:
            q = q.filter(InterviewReminder.user_id == user_id)
        return q.first()

    def list_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        upcoming_only: bool = True,
    ) -> tuple[list[InterviewReminder], int]:
        q = self.session.query(InterviewReminder).filter(InterviewReminder.user_id == user_id)
        if upcoming_only:
            q = q.filter(InterviewReminder.sent_at.is_(None)).filter(
                InterviewReminder.scheduled_at >= datetime.now(timezone.utc)
            )
        total = q.count()
        items = q.order_by(InterviewReminder.scheduled_at.asc()).offset(skip).limit(limit).all()
        return items, total

    def list_due_for_reminder(
        self,
        now: datetime | None = None,
        max_past_minutes: int = 10,
        limit: int = 500,
    ) -> list[InterviewReminder]:
        """
        Reminders that are due to be sent: sent_at IS NULL, reminder_due_at <= now,
        and scheduled_at is not too far in the past (now <= scheduled_at + max_past_minutes).
        """
        now = now or datetime.now(timezone.utc)
        past_cutoff = now - timedelta(minutes=max_past_minutes)
        q = (
            self.session.query(InterviewReminder)
            .filter(InterviewReminder.sent_at.is_(None))
            .filter(InterviewReminder.scheduled_at >= past_cutoff)
        )
        candidates = q.order_by(InterviewReminder.scheduled_at.asc()).limit(limit * 2).all()
        due = []
        for r in candidates:
            reminder_due_at = r.scheduled_at - timedelta(minutes=r.reminder_minutes_before)
            if reminder_due_at <= now:
                due.append(r)
            if len(due) >= limit:
                break
        return due

    def mark_sent(self, reminder_id: int, sent_at: datetime | None = None) -> bool:
        sent_at = sent_at or datetime.now(timezone.utc)
        r = self.session.query(InterviewReminder).filter(InterviewReminder.id == reminder_id).first()
        if not r:
            return False
        r.sent_at = sent_at
        self.session.commit()
        self.session.refresh(r)
        return True

    def delete(self, reminder_id: int, user_id: int | None = None) -> bool:
        q = self.session.query(InterviewReminder).filter(InterviewReminder.id == reminder_id)
        if user_id is not None:
            q = q.filter(InterviewReminder.user_id == user_id)
        r = q.first()
        if not r:
            return False
        self.session.delete(r)
        self.session.commit()
        return True
