"""
Ledger workspace model (Pure.cam / Stellar).

Maps `Workspace` from API_AND_DATA_REFERENCE.md. `client_workspace_id` is the
stable id from the client (e.g. `default`, `biz`).

Usage:
    >>> from fast_database.models.ledger_workspace import LedgerWorkspace
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, UniqueConstraint

from fast_database.constants.db.table import Table
from fast_database.models import Base


class LedgerWorkspace(Base):
    """
    Named workspace owned by a user; scopes all ledger_* rows.

    Attributes:
        id: Primary key.
        urn: Server-side stable identifier.
        user_id: Owner FK.
        client_workspace_id: Client `Workspace.id` (sync key).
        name: Display name.
        updated_at: Last mutation from client or server.
    """

    __tablename__ = Table.LEDGER_WORKSPACE
    __table_args__ = (
        UniqueConstraint("user_id", "client_workspace_id", name="uq_ledger_workspace_user_client"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    client_workspace_id = Column(String(128), nullable=False)
    name = Column(String(512), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "urn": self.urn,
            "user_id": self.user_id,
            "client_workspace_id": self.client_workspace_id,
            "name": self.name,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
