"""Status Lookup Repository.

Data access for the StatusLk model (generic status codes: e.g. draft, paid,
cancelled). Uses LookupRepositoryBase for standard lookup operations.
Referenced by Invoice and other status-carrying entities.

Usage:
    >>> from fastx_database.persistence.repositories.status_lk import StatusLkRepository
    >>> repo = StatusLkRepository(session=db_session)
    >>> all_statuses = repo.list_all()
    >>> active_status = repo.find_by_code("active")
"""

from sqlalchemy.orm import Session

from fastx_database.persistence.models.status_lk import StatusLk
from fastx_database.persistence.repositories.lookup_base import LookupRepositoryBase


class StatusLkRepository(LookupRepositoryBase[StatusLk]):
    """Repository for StatusLk (generic status) records.

    Provides standard lookup operations inherited from LookupRepositoryBase:
    - list_all(): Get all statuses ordered by code
    - find_by_code(code): Find status by unique code
    - find_by_urn(urn): Find status by URN
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
            model=StatusLk,
            session=session,
            order_by="code",
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
        )
