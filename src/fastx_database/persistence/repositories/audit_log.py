"""Audit Log Repository.

Data access for the AuditLog model (immutable audit trail: actor, action,
resource, metadata). Thin IRepository wrapper: session and base init only; use
IRepository or service-level methods for create_record and filtered queries.
Used where the audit table is mapped via models.audit_log.

Usage:
    >>> from fastx_database.persistence.repositories.audit_log import AuditLogRepository
    >>> repo = AuditLogRepository(session=db_session, urn="req-1")
"""

from sqlalchemy.orm import Session

from fastx_database.persistence.repositories.abstraction import IRepository
from fastx_database.persistence.models.audit_log import AuditLog


class AuditLogRepository(IRepository):
    """Repository for AuditLog (audit trail) table.

    Provides session and IRepository base (urn, user_urn, api_name, user_id,
    model=AuditLog). Use inherited or service-level methods for creating and
    querying audit records.
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
            model=AuditLog,
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
