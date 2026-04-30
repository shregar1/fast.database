"""Reaction Type Lookup Model.

SQLAlchemy ORM model for announcement reaction types (e.g. Like, Love, Celebrate).
Code and emoji identify the reaction; display_order controls UI ordering.

Usage:
    >>> from fastx_database.persistence.models.reaction_type_lk import ReactionTypeLk
    >>> # Used for announcement reactions (emoji, description, display_order)
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, String

from fastx_database.core.constants.table import Table
from fastx_database.persistence.models import Base


class ReactionTypeLk(Base):
    """Lookup: reaction type (code, emoji, description, display order).

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        code: Unique code (e.g. LIKE, LOVE).
        emoji: Emoji character(s).
        description: Human-readable label.
        display_order: Sort order for UI.
        created_at, updated_at: Timestamps.

    """

    __tablename__ = Table.REACTION_TYPE_LK

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    code = Column(String(32), nullable=False, unique=True, index=True)
    emoji = Column(String(32), nullable=False)
    description = Column(String(255), nullable=False)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow
    )

    def to_dict(self) -> dict:
        """Execute to_dict operation.

        Returns:
            The result of the operation.
        """
        return {
            "urn": self.urn,
            "code": self.code,
            "emoji": self.emoji,
            "description": self.description,
            "display_order": self.display_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
