"""
Gender Lookup Model.

SQLAlchemy ORM model for gender options (e.g. Male, Female, Non-binary). Code
is unique. Referenced by profile.gender_id.

Usage:
    >>> from fast_database.persistence.models.gender_lk import GenderLk
    >>> # Used in profile for user's gender
"""



from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String

from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class GenderLk(Base):
    """
    Lookup: gender (e.g. Male, Female, Non-binary).

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        code: Unique code.
        description: Human-readable label.
        created_at, updated_at: Timestamps.
    """



    __tablename__ = Table.GENDER_LK

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    code = Column(String(32), nullable=False, unique=True, index=True)
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
