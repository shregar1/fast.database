"""User notification preferences: get/upsert per (user_id, channel, category)."""

from sqlalchemy.orm import Session

from fast_repositories.repository import IRepository
from fast_database.models.user_notification_preference import UserNotificationPreference

CHANNELS = ("email", "push", "slack")
CATEGORIES = ("billing", "security", "product")


class UserNotificationPreferenceRepository(IRepository):
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
            model=UserNotificationPreference,
            cache=None,
        )
        self._session = session
        if not self._session:
            raise RuntimeError("DB session not found")

    @property
    def session(self) -> Session:
        return self._session

    def get(self, user_id: int, channel: str, category: str) -> UserNotificationPreference | None:
        return (
            self.session.query(UserNotificationPreference)
            .filter(
                UserNotificationPreference.user_id == user_id,
                UserNotificationPreference.channel == channel,
                UserNotificationPreference.category == category,
            )
            .first()
        )

    def list_by_user(self, user_id: int) -> list[UserNotificationPreference]:
        return (
            self.session.query(UserNotificationPreference)
            .filter(UserNotificationPreference.user_id == user_id)
            .all()
        )

    def set_enabled(self, user_id: int, channel: str, category: str, enabled: bool) -> UserNotificationPreference:
        rec = self.get(user_id, channel, category)
        if rec:
            rec.enabled = enabled
            self.session.commit()
            self.session.refresh(rec)
            return rec
        rec = UserNotificationPreference(
            user_id=user_id,
            channel=channel,
            category=category,
            enabled=enabled,
        )
        self.session.add(rec)
        self.session.commit()
        self.session.refresh(rec)
        return rec

    def is_enabled(self, user_id: int, channel: str, category: str) -> bool:
        """Default True if no row exists (opt-out model)."""
        rec = self.get(user_id, channel, category)
        return rec.enabled if rec else True
