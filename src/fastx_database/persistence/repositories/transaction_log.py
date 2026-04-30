"""Transaction Log Repository.

Data access for the TransactionLog model (API request/response audit: api_id,
reference_number, payloads, timestamps, http_status_code). IRepository
wrapper; use for create and query by api_id/reference_number or filters.
Used by API logging and idempotency flows.

Usage:
    >>> from fastx_database.persistence.repositories.transaction_log import TransactionLogRepository
    >>> repo = TransactionLogRepository(session=db_session)
"""

from sqlalchemy.orm import Session

from fastx_database.persistence.repositories.abstraction import IRepository
from fastx_database.persistence.models.transaction_log import TransactionLog


class TransactionLogRepository(IRepository):
    """Repository for TransactionLog (API request/response log) records.

    Provides session and IRepository base for TransactionLog. Use for
    appending log entries and querying by api_id, reference_number, or
    other filters in services.
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
            model=TransactionLog,
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
