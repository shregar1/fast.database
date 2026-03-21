"""
Country Lookup Model.

SQLAlchemy ORM model for countries. Code is typically ISO 3166-1 alpha-2
(e.g. US, IN, GB). Used for profile country, location, or address data.

Usage:
    >>> from fastmvc_db_models.models.country_lk import CountryLk
    >>> # code is ISO 3166-1 alpha-2 country code
"""




from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String

from src.constants.db.table import Table
from src.models import Base


class CountryLk(Base):
    """
    Lookup: country (code and name).

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        code: Unique country code (e.g. US, IN, GB).
        name: Human-readable country name.
        created_at, updated_at: Timestamps.
    """




    __tablename__ = Table.COUNTRY_LK

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    code = Column(String(8), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:

        return {
            "urn": self.urn,
            "code": self.code,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
