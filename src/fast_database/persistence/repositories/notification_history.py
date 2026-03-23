"""Notification history repository: create and list by user (e.g. last 30 days)."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from fast_database.persistence.repositories.abstraction import IRepository
from fast_database.persistence.models.notification_history import NotificationHistory


class NotificationHistoryRepository(IRepository):
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
            model=NotificationHistory,
            cache=None,
        )
        self._session = session
        if not self._session:
            raise RuntimeError("DB session not found")

    @property
    def session(self) -> Session:
        return self._session

    def create(
        self,
        user_id: int,
        channel: str = "in_app",
        category: str = "product",
        title: str | None = None,
        body: str | None = None,
    ) -> NotificationHistory:
        rec = NotificationHistory(
            user_id=user_id,
            channel=channel,
            category=category,
            title=title,
            body=body,
        )
        self.session.add(rec)
        self.session.commit()
        self.session.refresh(rec)
        return rec

    def list_by_user(
        self,
        user_id: int,
        days: int = 30,
        category: str | None = None,
        unread_only: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[NotificationHistory], int]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        q = self.session.query(NotificationHistory).filter(
            NotificationHistory.user_id == user_id,
            NotificationHistory.created_at >= since,
        )
        if category:
            q = q.filter(NotificationHistory.category == category)
        if unread_only is True:
            q = q.filter(NotificationHistory.read_at.is_(None))
        total = q.count()
        items = q.order_by(NotificationHistory.created_at.desc()).offset(skip).limit(limit).all()
        return list(items), total

    def mark_all_read(self, user_id: int) -> int:
        """Set read_at to now for all unread notifications for the user. Returns count updated."""
        now = datetime.now(timezone.utc)
        updated = (
            self.session.query(NotificationHistory)
            .filter(NotificationHistory.user_id == user_id, NotificationHistory.read_at.is_(None))
            .update({NotificationHistory.read_at: now}, synchronize_session=False)
        )
        self.session.commit()
        return updated

    def mark_read(self, notification_id: int, user_id: int) -> bool:
        from datetime import datetime, timezone
        n = (
            self.session.query(NotificationHistory)
            .filter(NotificationHistory.id == notification_id, NotificationHistory.user_id == user_id)
            .first()
        )
        if not n:
            return False
        n.read_at = datetime.now(timezone.utc)
        self.session.commit()
        return True
