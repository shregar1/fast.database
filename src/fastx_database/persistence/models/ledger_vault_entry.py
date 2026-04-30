"""Ledger vault entry metadata (Pure.cam).

Maps `VaultEntry` shape at the **metadata** level only. Secrets live encrypted
client-side; `encrypted_payload` can store an opaque blob for cloud backup.

Usage:
    >>> from fastx_database.persistence.models.ledger_vault_entry import LedgerVaultEntry
"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    LargeBinary,
    String,
    UniqueConstraint,
)

from sqlalchemy.dialects.postgresql import JSONB

from fastx_database.core.constants.table import Table
from fastx_database.persistence.models import Base


class LedgerVaultEntry(Base):
    """Vault entry row: type, name, folder link, optional ciphertext.

    Do not store plaintext passwords or card numbers in non-encrypted columns.
    """

    __tablename__ = Table.LEDGER_VAULT_ENTRY
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "ledger_workspace_id",
            "client_vault_entry_id",
            name="uq_ledger_vault_user_workspace_client",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ledger_workspace_id = Column(
        BigInteger,
        ForeignKey(Table.LEDGER_WORKSPACE + ".id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_vault_entry_id = Column(String(128), nullable=False)
    type = Column(String(32), nullable=False, index=True)
    name = Column(String(512), nullable=False)
    tags = Column(JSONB, nullable=True)
    folder_client_id = Column(String(128), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    encrypted_payload = Column(LargeBinary, nullable=True)
    field_metadata_json = Column(JSONB, nullable=True)

    def to_dict(self) -> dict:
        """Execute to_dict operation.

        Returns:
            The result of the operation.
        """
        return {
            "id": self.client_vault_entry_id,
            "type": self.type,
            "name": self.name,
            "tags": self.tags,
            "folderId": self.folder_client_id,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
