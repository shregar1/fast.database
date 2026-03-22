"""
Login attempt audit — success and failure rows for security monitoring.

Use for rate limiting, account lockout, anomaly detection, and compliance.
Do not store passwords or raw tokens.

Usage:
    >>> from fast_database.models.user_login_event import UserLoginEvent
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, Text

from fast_database.constants.table import Table
from fast_database.models import Base


class UserLoginEvent(Base):
    """
    Append-only record of a login attempt (password, OTP, SSO callback, etc.).

    Attributes:
        id: Primary key.
        user_id: Resolved user on success; null if email did not match any user.
        email_attempt: Identifier used to log in (email or username); optional for privacy tuning.
        ip_address: Client IP (hashed at edge if required by policy).
        user_agent: Optional client UA.
        success: Whether authentication succeeded.
        failure_reason: e.g. ``bad_password``, ``locked``, ``mfa_failed`` (no PII).
        auth_method: e.g. ``password``, ``oauth_google``, ``webauthn``.
        created_at: Event time (UTC).
    """

    __tablename__ = Table.USER_LOGIN_EVENT

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(f"{Table.USER}.id", ondelete="SET NULL"), nullable=True, index=True)
    email_attempt = Column(String(255), nullable=True, index=True)
    ip_address = Column(String(64), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, nullable=False, index=True)
    failure_reason = Column(String(64), nullable=True)
    auth_method = Column(String(32), nullable=False, default="password", index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
