"""
Interview session model.

SQLAlchemy ORM for interview sessions (linked from documents and conversations).

Usage:
    >>> from fast_database.persistence.models.session import Session
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String

from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class Session(Base):
    """
    Interview session record.

    Attributes:
        id: Primary key.
        user_id: Owner FK.
        title: Optional session label.
        created_at, updated_at: Timestamps.
    """

    __tablename__ = Table.SESSION

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    title = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
