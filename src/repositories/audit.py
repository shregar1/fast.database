"""
Audit Repository.

Data access for the AuditLog model (actor, action, resource, resource_id,
metadata, created_at). Create records from middleware or services; list with
filters (actor_id, action, resource, resource_id, from_ts, to_ts) and
pagination. Uses IRepository base and ``fast_database.models.audit.AuditLog``.

Usage:
    >>> from fast_repositories.audit import AuditRepository
    >>> repo = AuditRepository(session=db_session)
    >>> repo.create_record(record=audit_log_instance)
    >>> items, total = repo.retrieve_records(actor_id=1, action="user.update", skip=0, limit=50)
"""



from datetime import datetime

from sqlalchemy.orm import Session

from fast_repositories.repository import IRepository
from fast_database.models.audit import AuditLog


class AuditRepository(IRepository):
    """
    Repository for AuditLog (audit trail) create and query.

    Append-only audit entries. create_record adds and commits; retrieve_records
    supports filtering by actor, action, resource, resource_id, and time range
    with skip/limit. Used for compliance and debugging APIs.

    Methods:
        create_record: Insert and commit an AuditLog instance.
        retrieve_records: Filtered, paginated list; returns (items, total).
    """



    def __init__(
        self,
        session: Session | None = None,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ) -> None:
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
    def session(self, value: Session) -> None:
        self._session = value

    def create_record(self, record: AuditLog) -> AuditLog:
        self.logger.debug(f"Creating audit: action={record.action}, resource={record.resource}")
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)

        return record

    def retrieve_records(
        self,
        actor_id: int | None = None,
        action: str | None = None,
        resource: str | None = None,
        resource_id: str | None = None,
        from_ts: datetime | None = None,
        to_ts: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[AuditLog], int]:
        query = self.session.query(AuditLog)
        if actor_id is not None:
            query = query.filter(AuditLog.actor_id == actor_id)
        if action is not None:
            query = query.filter(AuditLog.action == action)
        if resource is not None:
            query = query.filter(AuditLog.resource == resource)
        if resource_id is not None:
            query = query.filter(AuditLog.resource_id == resource_id)
        if from_ts is not None:
            query = query.filter(AuditLog.created_at >= from_ts)
        if to_ts is not None:
            query = query.filter(AuditLog.created_at <= to_ts)
        total = query.count()

        items = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

        return items, total
