"""User notification preferences: get/upsert per (user_id, channel, category)."""

from sqlalchemy.orm import Session

from fastx_database.persistence.repositories.abstraction import IRepository
from fastx_database.persistence.models.user_notification_preference import (
    UserNotificationPreference,
)

CHANNELS = ("email", "push", "slack")
CATEGORIES = ("billing", "security", "product")


class UserNotificationPreferenceRepository(IRepository):
    """Represents the UserNotificationPreferenceRepository class."""

    def __init__(
        self,
        session: Session | None = None,
        *,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            session: The session parameter.
            urn: The urn parameter.
            user_urn: The user_urn parameter.
            api_name: The api_name parameter.
            user_id: The user_id parameter.
        """
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
        """Execute session operation.

        Returns:
            The result of the operation.
        """
        return self._session

    def get(
        self, user_id: int, channel: str, category: str
    ) -> UserNotificationPreference | None:
        """Execute get operation.

        Args:
            user_id: The user_id parameter.
            channel: The channel parameter.
            category: The category parameter.

        Returns:
            The result of the operation.
        """
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
        """Execute list_by_user operation.

        Args:
            user_id: The user_id parameter.

        Returns:
            The result of the operation.
        """
        return (
            self.session.query(UserNotificationPreference)
            .filter(UserNotificationPreference.user_id == user_id)
            .all()
        )

    def set_enabled(
        self, user_id: int, channel: str, category: str, enabled: bool
    ) -> UserNotificationPreference:
        """Execute set_enabled operation.

        Args:
            user_id: The user_id parameter.
            channel: The channel parameter.
            category: The category parameter.
            enabled: The enabled parameter.

        Returns:
            The result of the operation.
        """
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
