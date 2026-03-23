"""
Audit Log Model.

SQLAlchemy ORM model for an immutable audit trail. Each row records an actor
(user or system), an action (e.g. create, update), a resource type and optional
resource_id, plus optional JSONB metadata. Used for compliance and debugging.

Usage:
    >>> from fast_database.persistence.models.audit_log import AuditLog
    >>> # Written by middleware or services; actor_id/actor_urn identify who performed the action
"""



from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB

from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class AuditLog(Base):
    """
    Immutable audit trail entry: who did what to which resource.

    Captures actor (user id/URN or null for system), action (e.g. "user.update"),
    resource type and optional resource_id, and optional metadata (diff, context).
    Do not update or delete rows; append-only.

    Attributes:
        id: Primary key.
        actor_id: FK to user (null for system actions).
        actor_urn: Optional URN for actor.
        action: Action identifier (e.g. "session.create").
        resource: Resource type (e.g. "session", "document").
        resource_id: Optional target entity ID.
        audit_metadata: JSONB; column name in DB is "metadata".
        created_at: When the event occurred.
    """



    __tablename__ = Table.AUDIT

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    actor_id = Column(BigInteger, ForeignKey("user.id"), nullable=True, index=True)
    actor_urn = Column(String(128), nullable=True, index=True)
    action = Column(String(64), nullable=False, index=True)
    resource = Column(String(64), nullable=False, index=True)
    resource_id = Column(String(128), nullable=True, index=True)
    audit_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def to_dict(self) -> dict:

        return {
            "actor_id": self.actor_id,
            "actor_urn": self.actor_urn,
            "action": self.action,
            "resource": self.resource,
            "resource_id": self.resource_id,
            "metadata": self.audit_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
