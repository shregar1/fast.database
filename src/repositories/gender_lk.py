"""
Gender Lookup Repository.

Data access for the GenderLk model (gender options: e.g. Male, Female,
Non-binary). IRepository wrapper; use for retrieve by id or code, list all.
Used by Profile for gender_id.

Usage:
    >>> from fast_repositories.gender_lk import GenderLkRepository
    >>> repo = GenderLkRepository(session=db_session)
"""



from sqlalchemy.orm import Session

from fast_repositories.repository import IRepository
from fast_database.models.gender_lk import GenderLk


class GenderLkRepository(IRepository):
    """
    Repository for GenderLk (gender) records.

    Provides session and IRepository base. Use for profile forms and
    resolving gender_id by code.
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
            model=GenderLk,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value

    def list_all(self):
        """Return all gender lookup entries ordered by code."""

        return (
            self.session.query(GenderLk)
            .order_by(GenderLk.code)
            .all()
        )
