"""
Consent Repository.

Data access for ConsentRecord (ToS/Privacy acceptance). Extends
:class:`~fast_repositories.repository.IRepository`. Get by user and type, list all consents for a user, and accept
(upsert: update version and accepted_at if record exists, else create). Used
by registration and legal-compliance flows.

Usage:
    >>> from fast_repositories.consent import ConsentRepository
    >>> repo = ConsentRepository(session=db_session)
    >>> rec = repo.get_by_user_and_type(user_id=1, type="tos")
    >>> repo.accept(user_id=1, type="privacy", version="2024-01")
"""



from datetime import datetime, timezone

from sqlalchemy.orm import Session

from fast_repositories.repository import IRepository
from fast_database.models.consent import ConsentRecord


class ConsentRepository(IRepository):
    """
    Repository for consent records (ToS/Privacy acceptance per user).

    Methods:
        get_by_user_and_type: Fetch one consent for user and type (e.g. "tos", "privacy").
        list_by_user: List all consents for user, newest first.
        accept: Record acceptance: update existing or create; returns ConsentRecord.
    """



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
            model=ConsentRecord,
            cache=None,
        )
        self._session = session
        if not self._session:
            raise RuntimeError("DB session not found")

    @property
    def session(self) -> Session:

        return self._session

    def get_by_user_and_type(self, user_id: int, type: str) -> ConsentRecord | None:

        return (
            self.session.query(ConsentRecord)
            .filter(ConsentRecord.user_id == user_id, ConsentRecord.type == type)
            .first()
        )

    def list_by_user(self, user_id: int) -> list[ConsentRecord]:

        return list(
            self.session.query(ConsentRecord)
            .filter(ConsentRecord.user_id == user_id)
            .order_by(ConsentRecord.accepted_at.desc())
            .all()
        )

    def accept(self, user_id: int, type: str, version: str) -> ConsentRecord:
        now = datetime.now(timezone.utc)
        rec = self.get_by_user_and_type(user_id, type)
        if rec:
            rec.version = version
            rec.accepted_at = now
            self.session.commit()
            self.session.refresh(rec)

            return rec
        rec = ConsentRecord(user_id=user_id, type=type, version=version, accepted_at=now)

        self.session.add(rec)
        self.session.commit()
        self.session.refresh(rec)

        return rec
