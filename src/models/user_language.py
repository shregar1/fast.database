"""
User Language Model.

SQLAlchemy ORM model for the user–language association (many-to-many: users
can speak multiple languages). One row per (user_id, language_id). Unique
constraint on (user_id, language_id). language_id references language_lk.

Usage:
    >>> from fast_database.models.user_language import UserLanguage
    >>> # Used for profile languages spoken; is_deleted for soft remove
"""



from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint

from fast_database.constants.table import Table
from fast_database.models import Base


class UserLanguage(Base):
    """
    Join record: user speaks a language (many languages per user).

    Links user_id to language_id (language_lk). Unique on (user_id, language_id).
    is_deleted allows soft removal of a language from a profile.

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        user_id: FK to user.
        language_id: FK to language_lk.
        is_deleted: Soft-delete flag.
        created_at, updated_at, created_by, updated_by: Audit fields.
    """



    __tablename__ = Table.USER_LANGUAGE
    __table_args__ = (UniqueConstraint("user_id", "language_id", name="uq_user_language_user_lang"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    language_id = Column(BigInteger, ForeignKey("language_lk.id"), nullable=False, index=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    updated_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    def to_dict(self) -> dict:

        return {
            "urn": self.urn,
            "user_id": self.user_id,
            "language_id": self.language_id,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
