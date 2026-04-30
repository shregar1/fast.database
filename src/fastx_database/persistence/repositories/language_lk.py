"""Language Lookup Repository.

Data access for the LanguageLk model (language code and description). IRepository
wrapper; use for retrieve by id or code, list all. Used by UserLanguage and
profile language dropdowns.

Usage:
    >>> from fastx_database.persistence.repositories.language_lk import LanguageLkRepository
    >>> repo = LanguageLkRepository(session=db_session)
"""

from sqlalchemy.orm import Session

from fastx_database.persistence.repositories.abstraction import IRepository
from fastx_database.persistence.models.language_lk import LanguageLk


class LanguageLkRepository(IRepository):
    """Repository for LanguageLk (language) records.

    Provides session and IRepository base. Use for resolving language_id and
    listing languages for user profile and preferences.
    """

    def __init__(
        self,
        session: Session = None,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ):
        """Execute __init__ operation.

        Args:
            session: The session parameter.
            urn: The urn parameter.
            user_urn: The user_urn parameter.
            api_name: The api_name parameter.
            user_id: The user_id parameter.
        """
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
        """Execute session operation.

        Returns:
            The result of the operation.
        """
        return self._session

    @session.setter
    def session(self, value: Session):
        """Execute session operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._session = value

    def list_all(self):
        """Return all language lookup entries ordered by code."""
        return self.session.query(LanguageLk).order_by(LanguageLk.code).all()
