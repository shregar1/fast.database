"""
API Key Model.

SQLAlchemy ORM model for server-to-server authentication. API keys are stored as
one-way hashes; the raw key is shown only at creation time. Scopes (e.g. read_only)
restrict what operations the key can perform.

Usage:
    >>> from fastmvc_db_models.models.api_key import ApiKey
    >>> # Keys are created via repository; auth middleware validates key_hash and scopes
"""



from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB

from src.constants.db.table import Table
from src.models import Base


class ApiKey(Base):
    """
    API key for server-to-server authentication.

    Stores a hash of the secret key; the plaintext is never persisted. Scopes
    (JSON array) limit which endpoints or actions the key can call. Optional
    last_used_at supports usage analytics; revoked_at supports key rotation.

    Attributes:
        id: Primary key.
        user_id: Owner of the key (FK to user).
        key_hash: One-way hash of the secret (e.g. SHA-256); unique, indexed.
        name: Human-readable label for the key.
        scopes: JSONB array of scope strings (e.g. ["read_only"]).
        last_used_at: Last time the key was used for a request.
        created_at: When the key was created.
        revoked_at: If set, key is invalid and must not be accepted.
    """



    __tablename__ = Table.API_KEY

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger,
        ForeignKey(Table.USER + ".id"),
        nullable=False,
        index=True,
    )
    key_hash = Column(String(128), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(512), nullable=True)
    scopes = Column(JSONB, nullable=False, server_default="[]")
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    last_used_ip = Column(String(45), nullable=True)  # IPv4 or IPv6
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "prefix": "kiv_***",
            "scopes": self.scopes or [],
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "last_used_ip": self.last_used_ip,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
        }
