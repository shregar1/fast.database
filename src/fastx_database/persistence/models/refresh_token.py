"""Refresh Token Model.

SQLAlchemy ORM model for refresh token rotation and revocation. Stores jti
(unique token id) and family (chain id for rotation); revoked_at for
invalidation. Used for refresh token rotation and "log out all devices".

Usage:
    >>> from fastx_database.persistence.models.refresh_token import RefreshToken
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String

from fastx_database.core.constants.table import Table
from fastx_database.persistence.models import Base


class RefreshToken(Base):
    """Stored refresh token for rotation and revocation.

    jti: Unique token id (in JWT); used to validate and revoke.
    family_id: Same for a chain of rotated tokens; revoke family to revoke all.
    revoked_at: Set when token is used (rotation) or explicitly revoked.
    """

    __tablename__ = Table.REFRESH_TOKEN

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    jti = Column(String(64), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    family_id = Column(String(64), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
