"""
User usage alert preference repository: get or upsert per-user threshold and channels.
"""

from sqlalchemy.orm import Session

from fast_repositories.repository import IRepository
from fast_database.models.user_usage_alert_preference import UserUsageAlertPreference


class UserUsageAlertPreferenceRepository(IRepository):
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
            model=UserUsageAlertPreference,
            cache=None,
        )
        self._session = session
        if not self._session:
            raise RuntimeError("DB session not found")

    @property
    def session(self) -> Session:
        return self._session

    def get_by_user_id(self, user_id: int) -> UserUsageAlertPreference | None:
        return (
            self.session.query(UserUsageAlertPreference)
            .filter(UserUsageAlertPreference.user_id == user_id)
            .first()
        )

    def upsert(
        self,
        user_id: int,
        threshold_percent: float | None = None,
        channels: list[str] | None = None,
    ) -> UserUsageAlertPreference:
        rec = self.get_by_user_id(user_id)
        if rec is None:
            rec = UserUsageAlertPreference(
                user_id=user_id,
                threshold_percent=threshold_percent if threshold_percent is not None else 80.0,
                channels=channels if channels is not None else ["email", "in_app"],
            )
            self.session.add(rec)
        else:
            if threshold_percent is not None:
                rec.threshold_percent = max(1.0, min(100.0, threshold_percent))
            if channels is not None:
                rec.channels = channels
        self.session.commit()
        self.session.refresh(rec)
        return rec

