"""
One-time tokens for password reset, email verification, and magic links.

Store only a **hash** of the secret token; never store plaintext.

Usage:
    >>> from fast_database.persistence.models.user_one_time_token import UserOneTimeToken
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text

from sqlalchemy.dialects.postgresql import JSONB

from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class UserOneTimeToken(Base):
    """
    Single-use token row (password reset, email verify, invite).

    Attributes:
        id: Primary key.
        user_id: Subject (FK ``user.id``); required for most flows.
        purpose: ``password_reset``, ``email_verify``, ``magic_link``, ``invite``, …
        token_hash: Hash of the secret token (unique while active).
        expires_at: Token invalid after this time (UTC).
        consumed_at: Set when used (single-use); null if still valid or revoked.
        redirect_url: Optional safe relative path or token for post-verify redirect.
        extra: Optional JSON (e.g. device fingerprint).
        created_at: When the token was issued.
    """

    __tablename__ = Table.USER_ONE_TIME_TOKEN

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(f"{Table.USER}.id", ondelete="CASCADE"), nullable=False, index=True)
    purpose = Column(String(32), nullable=False, index=True)
    token_hash = Column(String(128), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    consumed_at = Column(DateTime(timezone=True), nullable=True, index=True)
    redirect_url = Column(Text, nullable=True)
    extra = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
