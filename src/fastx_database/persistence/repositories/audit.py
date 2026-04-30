"""Audit Repository.

Data access for the AuditLog model (actor, action, resource, resource_id,
metadata, created_at). Create records from middleware or services; list with
filters (actor_id, action, resource, resource_id, from_ts, to_ts) and
pagination. Uses IRepository base and ``fastx_database.persistence.models.audit.AuditLog``.

Usage:
    >>> from fastx_database.persistence.repositories.audit import AuditRepository
    >>> repo = AuditRepository(session=db_session)
    >>> repo.create_record(record=audit_log_instance)
    >>> items, total = repo.retrieve_records(actor_id=1, action="user.update", skip=0, limit=50)
"""

from datetime import datetime

from sqlalchemy.orm import Session

from fastx_database.persistence.repositories.abstraction import IRepository
from fastx_database.persistence.models.audit import AuditLog


class AuditRepository(IRepository):
    """Repository for AuditLog (audit trail) create and query.

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
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
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
    def session(self, value: Session) -> None:
        """Execute session operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._session = value

    def create_record(self, record: AuditLog) -> AuditLog:
        """Execute create_record operation.

        Args:
            record: The record parameter.

        Returns:
            The result of the operation.
        """
        self.logger.debug(
            f"Creating audit: action={record.action}, resource={record.resource}"
        )
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
        """Execute retrieve_records operation.

        Args:
            actor_id: The actor_id parameter.
            action: The action parameter.
            resource: The resource parameter.
            resource_id: The resource_id parameter.
            from_ts: The from_ts parameter.
            to_ts: The to_ts parameter.
            skip: The skip parameter.
            limit: The limit parameter.

        Returns:
            The result of the operation.
        """
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

        items = (
            query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
        )

        return items, total
