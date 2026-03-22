"""
User Model.

SQLAlchemy ORM model for the core user (account) table. Represents a single
identity: login credentials (email, phone, hashed password), user type (e.g.
candidate, employer via user_type_lk), and soft-delete / audit timestamps.

Usage:
    >>> from fast_database.models.user import User
    >>> # Typically accessed via repositories; created_by/updated_by track audit
"""



from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String

from fast_database.constants.table import Table
from fast_database.models import Base


class User(Base):
    """
    Core user account and authentication entity.

    One row per user. URN is the stable external identifier; email and phone
    are unique and used for login. user_type_id references user_type_lk (e.g.
    candidate, employer). is_deleted enables soft delete; last_login supports
    security and analytics.

    Attributes:
        id: Primary key.
        urn: Unique Resource Name (stable external ID).
        email: Unique email; used for login.
        password: Bcrypt (or similar) hash; never store plaintext.
        phone: Unique phone; used for login/MFA.
        user_type_id: FK to user_type_lk.
        is_deleted: Soft-delete flag.
        last_login: Last successful login timestamp.
        created_at,         updated_at: Audit timestamps.
        created_by, updated_by: FK to user.id (audit).
        Signing key material (Ed25519 PEM) lives in :class:`~fast_database.models.user_signing_key.UserSigningKey`.
    """



    __tablename__ = Table.USER

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(32), nullable=False, unique=True, index=True)
    user_type_id = Column(BigInteger, ForeignKey("user_type_lk.id"), nullable=False, index=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    updated_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    def to_dict(self) -> dict:

        return {
            "urn": self.urn,
            "email": self.email,
            "phone": self.phone,
            "user_type_id": self.user_type_id,
            "is_deleted": self.is_deleted,
            "email_verified_at": self.email_verified_at.isoformat() if self.email_verified_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
