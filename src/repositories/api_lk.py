"""
API Lookup Repository.

Data access for the ApiLk model (API definitions: method, endpoint, name, for
transaction logging). IRepository wrapper; use for retrieve by id or
method+endpoint, list all. Used by TransactionLog and API catalog.

Usage:
    >>> from fast_database.repositories.api_lk import ApiLkRepository
    >>> repo = ApiLkRepository(session=db_session)
"""



from sqlalchemy.orm import Session

from fast_database.repositories.abstraction import IRepository
from fast_database.models.api_lk import ApiLk


class ApiLkRepository(IRepository):
    """
    Repository for ApiLk (API endpoint lookup) records.

    Provides session and IRepository base. Use for looking up API id by
    method+endpoint or listing APIs for transaction log resolution.
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
            model=ApiLk,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value

    def list_all(self):
        """Return all API lookup entries ordered by name."""

        return (
            self.session.query(ApiLk)
            .order_by(ApiLk.name)
            .all()
        )
