"""
Language Lookup Model.

SQLAlchemy ORM model for supported languages. Code (e.g. en, hi) is unique.
Referenced by user_language.language_id for languages a user speaks.

Usage:
    >>> from fastmvc_db_models.models.language_lk import LanguageLk
    >>> # code is typically ISO 639 or similar
"""



from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String

from src.constants.db.table import Table
from src.models import Base


class LanguageLk(Base):
    """
    Lookup: language (code and description).

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        code: Unique language code (e.g. en, hi).
        description: Human-readable name.
        created_at, updated_at: Timestamps.
    """



    __tablename__ = Table.LANGUAGE_LK

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    code = Column(String(16), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:

        return {
            "urn": self.urn,
            "code": self.code,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
