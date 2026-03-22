"""
Education Level Lookup Repository.

Data access for the EducationLevelLk model (education levels: e.g. high_school,
bachelor, master). IRepository wrapper; use for retrieve by id or code, list
all. Used by Profile for education_level_id.

Usage:
    >>> from fast_database.repositories.education_level_lk import EducationLevelLkRepository
    >>> repo = EducationLevelLkRepository(session=db_session)
"""



from sqlalchemy.orm import Session

from fast_database.repositories.abstraction import IRepository
from fast_database.models.education_level_lk import EducationLevelLk


class EducationLevelLkRepository(IRepository):
    """
    Repository for EducationLevelLk records.

    Provides session and IRepository base. Use for profile forms and
    resolving education_level_id by code.
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
            model=EducationLevelLk,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value

    def list_all(self):
        """Return all education level lookup entries ordered by code."""

        return (
            self.session.query(EducationLevelLk)
            .order_by(EducationLevelLk.code)
            .all()
        )
