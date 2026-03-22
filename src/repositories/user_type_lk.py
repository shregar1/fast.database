"""
User Type Lookup Repository.

Data access for the UserTypeLk model (user type codes: e.g. candidate,
employer). IRepository wrapper; use inherited retrieve_record_by_id,
retrieve_records_by_filter, or list methods. Lookup data is typically
seed-loaded; read-heavy.

Usage:
    >>> from fast_database.repositories.user_type_lk import UserTypeLkRepository
    >>> repo = UserTypeLkRepository(session=db_session)
"""



from sqlalchemy.orm import Session

from fast_database.repositories.abstraction import IRepository
from fast_database.models.user_type_lk import UserTypeLk


class UserTypeLkRepository(IRepository):
    """
    Repository for UserTypeLk (user type lookup) records.

    Provides session and IRepository base. Use IRepository filter/retrieve
    methods to get records by id, code, or list all for dropdowns.
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
            model=UserTypeLk,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value

    def list_all(self):
        """Return all user type lookup entries ordered by code."""

        return (
            self.session.query(UserTypeLk)
            .order_by(UserTypeLk.code)
            .all()
        )
