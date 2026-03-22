"""
Education Level Lookup Model.

SQLAlchemy ORM model for education level codes (e.g. high_school, bachelor,
master). Referenced by profile.education_level_id. Code is unique.

Usage:
    >>> from fast_database.models.education_level_lk import EducationLevelLk
    >>> # Used in profile for highest education level
"""



from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String

from fast_database.constants.db.table import Table
from fast_database.models import Base


class EducationLevelLk(Base):
    """
    Lookup: education level (e.g. high_school, bachelor, master).

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        code: Unique code.
        description: Human-readable label.
        created_at, updated_at: Timestamps.
    """



    __tablename__ = Table.EDUCATION_LEVEL_LK

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    code = Column(String(64), nullable=False, unique=True, index=True)
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
