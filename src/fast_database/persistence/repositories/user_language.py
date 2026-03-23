"""
User Language Repository.

Data access for the UserLanguage model (user–language association: which
languages a user speaks). IRepository wrapper; use for list by user, add,
remove (soft delete). Used by profile and onboarding flows.

Usage:
    >>> from fast_database.persistence.repositories.user_language import UserLanguageRepository
    >>> repo = UserLanguageRepository(session=db_session)
"""



from sqlalchemy.orm import Session

from fast_database.persistence.repositories.abstraction import IRepository
from fast_database.persistence.models.user_language import UserLanguage


class UserLanguageRepository(IRepository):
    """
    Repository for UserLanguage (user–language) records.

    Provides session and IRepository base for UserLanguage. Use for listing
    languages per user, adding a language, and soft delete in services.
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
            model=UserLanguage,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value
