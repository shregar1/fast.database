"""User Type Lookup Repository.

Data access for the UserTypeLk model (user type codes: e.g. candidate,
employer). Uses LookupRepositoryBase for standard lookup operations.
Referenced by user.user_type_id.

Usage:
    >>> from fastx_database.persistence.repositories.user_type_lk import UserTypeLkRepository
    >>> repo = UserTypeLkRepository(session=db_session)
    >>> all_types = repo.list_all()
    >>> candidate = repo.find_by_code("candidate")
"""

from sqlalchemy.orm import Session

from fastx_database.persistence.models.user_type_lk import UserTypeLk
from fastx_database.persistence.repositories.lookup_base import LookupRepositoryBase


class UserTypeLkRepository(LookupRepositoryBase[UserTypeLk]):
    """Repository for UserTypeLk (user type lookup) records.

    Provides standard lookup operations inherited from LookupRepositoryBase:
    - list_all(): Get all user types ordered by code
    - find_by_code(code): Find type by unique code
    - find_by_urn(urn): Find type by URN
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
            model=UserTypeLk,
            session=session,
            order_by="code",
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
        )
