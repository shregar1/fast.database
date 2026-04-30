"""Gender Lookup Repository.

Data access for the GenderLk model (gender options: e.g. Male, Female,
Non-binary). Uses LookupRepositoryBase for standard lookup operations.
Used by Profile for gender_id.

Usage:
    >>> from fastx_database.persistence.repositories.gender_lk import GenderLkRepository
    >>> repo = GenderLkRepository(session=db_session)
    >>> all_genders = repo.list_all()
    >>> male = repo.find_by_code("male")
"""

from sqlalchemy.orm import Session

from fastx_database.persistence.models.gender_lk import GenderLk
from fastx_database.persistence.repositories.lookup_base import LookupRepositoryBase


class GenderLkRepository(LookupRepositoryBase[GenderLk]):
    """Repository for GenderLk (gender) records.

    Provides standard lookup operations inherited from LookupRepositoryBase:
    - list_all(): Get all genders ordered by code
    - find_by_code(code): Find gender by unique code
    - find_by_urn(urn): Find gender by URN
    - All IRepository CRUD methods
    """

    def __init__(
        self,
        session: Session,
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
        super().__init__(
            model=GenderLk,
            session=session,
            order_by="code",
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
        )
