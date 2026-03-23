"""
Status Lookup Repository.

Data access for the StatusLk model (generic status codes: e.g. draft, paid,
cancelled). IRepository wrapper; use for retrieve by id or code, list all.
Referenced by Invoice and other status-carrying entities.

Usage:
    >>> from fast_database.persistence.repositories.status_lk import StatusLkRepository
    >>> repo = StatusLkRepository(session=db_session)
"""



from sqlalchemy.orm import Session

from fast_database.persistence.repositories.abstraction import IRepository
from fast_database.persistence.models.status_lk import StatusLk


class StatusLkRepository(IRepository):
    """
    Repository for StatusLk (generic status) records.

    Provides session and IRepository base. Use for resolving status_id by
    code or listing statuses for dropdowns.
    """



    def __init__(
        self,
        session: Session = None,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ):
        self._cache = None
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            cache=self._cache,
            model=StatusLk,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value

    def list_all(self):
        """Return all status lookup entries ordered by code."""

        return (
            self.session.query(StatusLk)
            .order_by(StatusLk.code)
            .all()
        )
