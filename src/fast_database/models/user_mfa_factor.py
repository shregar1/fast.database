"""
Multi-factor authentication factors bound to a user (TOTP, WebAuthn, backup codes).

Store only **opaque or encrypted** material; never plaintext TOTP seeds in logs.

Usage:
    >>> from fast_database.models.user_mfa_factor import UserMfaFactor
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, Text

from sqlalchemy.dialects.postgresql import JSONB

from fast_database.constants.table import Table
from fast_database.models import Base


class UserMfaFactor(Base):
    """
    One enrolled second factor (user may have several: phone TOTP + security keys).

    Attributes:
        id: Primary key.
        user_id: Owner (FK ``user.id``).
        factor_type: ``totp``, ``webauthn``, ``sms``, ``backup_codes``, …
        label: User-visible name (e.g. "Work YubiKey").
        credential_data: Encrypted secret, WebAuthn credential JSON, or opaque blob.
        webauthn_credential_id: Optional base64url id for WebAuthn lookups.
        is_verified: Enrollment completed (e.g. TOTP confirmed).
        is_enabled: User or admin can disable without deleting history.
        last_used_at: Last successful MFA use (UTC).
        created_at: Enrollment time (UTC).
    """

    __tablename__ = Table.USER_MFA_FACTOR

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger,
        ForeignKey(f"{Table.USER}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    factor_type = Column(String(32), nullable=False, index=True)
    label = Column(String(128), nullable=False, default="Authenticator")
    credential_data = Column(Text, nullable=True)
    webauthn_credential_id = Column(String(512), nullable=True, index=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_enabled = Column(Boolean, nullable=False, default=True, index=True)
    extra = Column(JSONB, nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
