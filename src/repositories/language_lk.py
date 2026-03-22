"""
Language Lookup Repository.

Data access for the LanguageLk model (language code and description). IRepository
wrapper; use for retrieve by id or code, list all. Used by UserLanguage and
profile language dropdowns.

Usage:
    >>> from fast_repositories.language_lk import LanguageLkRepository
    >>> repo = LanguageLkRepository(session=db_session)
"""



from sqlalchemy.orm import Session

from fast_repositories.repository import IRepository
from fast_database.models.language_lk import LanguageLk


class LanguageLkRepository(IRepository):
    """
    Repository for LanguageLk (language) records.

    Provides session and IRepository base. Use for resolving language_id and
    listing languages for user profile and preferences.
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
            model=LanguageLk,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value

    def list_all(self):
        """Return all language lookup entries ordered by code."""

        return (
            self.session.query(LanguageLk)
            .order_by(LanguageLk.code)
            .all()
        )
