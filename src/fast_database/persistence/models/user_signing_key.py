"""
User signing keypair (Ed25519) — separate table from ``user``.

PEM public key and Fernet-encrypted private key live here so the core ``user`` row
stays focused on credentials and profile linkage. At most one row per ``user_id``.

Usage:
    >>> from fast_database.persistence.models.user_signing_key import UserSigningKey
"""

from __future__ import annotations

from sqlalchemy import BigInteger, Column, ForeignKey, Text

from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class UserSigningKey(Base):
    """
    Ed25519 signing key material for a user account.

    Attributes:
        id: Primary key.
        user_id: Owner (FK ``user.id``); unique — one key row per user.
        public_key_pem: PEM-encoded Ed25519 public key (generated at signup).
        encrypted_private_key_pem: Fernet-encrypted PEM private key; plaintext
            shown once at registration if your app flow provides it.
    """

    __tablename__ = Table.USER_SIGNING_KEY

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger,
        ForeignKey(f"{Table.USER}.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    public_key_pem = Column(Text, nullable=True)
    encrypted_private_key_pem = Column(Text, nullable=True)
