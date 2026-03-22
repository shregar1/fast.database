"""
Audit Log Repository.

Data access for the AuditLog model (immutable audit trail: actor, action,
resource, metadata). Thin IRepository wrapper: session and base init only; use
IRepository or service-level methods for create_record and filtered queries.
Used where the audit table is mapped via models.audit_log.

Usage:
    >>> from fast_repositories.audit_log import AuditLogRepository
    >>> repo = AuditLogRepository(session=db_session, urn="req-1")
"""



from sqlalchemy.orm import Session

from fast_repositories.repository import IRepository
from fast_database.models.audit_log import AuditLog


class AuditLogRepository(IRepository):
    """
    Repository for AuditLog (audit trail) table.

    Provides session and IRepository base (urn, user_urn, api_name, user_id,
    model=AuditLog). Use inherited or service-level methods for creating and
    querying audit records.
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
            model=AuditLog,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value
