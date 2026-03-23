"""
User LLM provider API key model.

Stores **ciphertext** for third-party LLM credentials (OpenAI, Anthropic, OpenRouter,
Google Gemini, etc.) per user. Plaintext never appears in this table; the application
layer encrypts before insert and decrypts after read when using server-side Fernet.

When ``is_encrypted_by_client`` is True, ``secret_ciphertext`` is an opaque blob
supplied by the client (BYOK); the server does not decrypt it for inference unless
your product logic provides a key.

Usage:
    >>> from fast_database.persistence.models.user_provider_key import UserProviderKey
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, Text, UniqueConstraint

from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class UserProviderKey(Base):
    """
    One row per (user, provider) for BYOK / stored LLM credentials.

    Attributes:
        id: Primary key.
        user_id: Owner (FK ``user.id``).
        provider: Stable slug, e.g. ``openai``, ``anthropic``, ``openrouter``, ``google_gemini``.
        secret_ciphertext: Encrypted or opaque secret (text, typically Fernet token or base64 blob).
        is_encrypted_by_client: If True, ciphertext was provided by the client; server may not decrypt.
        key_last_four: Optional last 4 chars of original key for UI (set when server encrypts plaintext).
        created_at / updated_at: Timestamps (UTC).
    """

    __tablename__ = Table.USER_LLM_PROVIDER_KEY
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "provider",
            name="uq_user_llm_provider_key_user_provider",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger,
        ForeignKey(Table.USER + ".id"),
        nullable=False,
        index=True,
    )
    provider = Column(String(32), nullable=False)
    secret_ciphertext = Column(Text, nullable=False)
    is_encrypted_by_client = Column(Boolean, nullable=False, server_default="false")
    key_last_four = Column(String(4), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
