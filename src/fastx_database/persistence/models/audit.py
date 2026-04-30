"""Audit Model (alternate).

SQLAlchemy ORM model for audit events: actor, action, resource, optional
resource_id, and JSONB metadata. Alternative or legacy definition for the
audit table; actor_id has no FK here. Used for compliance and debugging.

Usage:
    >>> from fastx_database.persistence.models.audit import AuditLog
    >>> # metadata_ holds optional diff or context; column name in DB is "metadata"

Note: Table name matches models.audit_log; extend_existing=True allows both
modules to be imported without "table already defined" error.
"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB

from fastx_database.core.constants.table import Table
from fastx_database.persistence.models import Base


class AuditLog(Base):
    """Audit log entry: actor, action, resource, and optional metadata.

    Same table as audit_log.AuditLog (Table.AUDIT). actor_id is optional (null
    for system). action and resource are indexed for querying. metadata_ (DB
    column "metadata") holds optional JSON diff or context.

    Attributes:
        id: Primary key.
        actor_id: Optional user id (no FK in this module).
        actor_urn: Optional actor URN.
        action: Action name (e.g. "session.create").
        resource: Resource type (e.g. "session").
        resource_id: Optional target ID.
        metadata_: JSONB; DB column name "metadata".
        created_at: Event timestamp.

    """

    __tablename__ = Table.AUDIT
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    actor_id = Column(
        BigInteger, nullable=True, index=True
    )  # user id or null for system
    actor_urn = Column(String(64), nullable=True, index=True)

    action = Column(
        String(64), nullable=False, index=True
    )  # e.g. "session.create", "document.upload"
    resource = Column(
        String(64), nullable=False, index=True
    )  # e.g. "session", "document"
    resource_id = Column(String(128), nullable=True, index=True)

    # Optional diff or extra context (JSON)
    metadata_ = Column("metadata", JSONB, nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    def to_dict(self) -> dict:
        """Execute to_dict operation.

        Returns:
            The result of the operation.
        """
        return {
            "actor_id": self.actor_id,
            "actor_urn": self.actor_urn,
            "action": self.action,
            "resource": self.resource,
            "resource_id": self.resource_id,
            "metadata": self.metadata_,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
