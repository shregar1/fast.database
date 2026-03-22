"""
Conversation and ConversationMessage models.

SQLAlchemy ORM models for persisted LLM conversations: one conversation per
thread (user_id, optional session_id), with messages in order (role + content).

Usage:
    >>> from fast_database.models.conversation import Conversation, ConversationMessage
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text

from fast_database.constants.db.table import Table
from fast_database.models import Base


class Conversation(Base):
    """
    One conversation thread (e.g. per session or ad-hoc).

    Attributes:
        id: Primary key.
        user_id: FK to user.
        session_id: Optional FK to sessions (interview session).
        title: Optional title (e.g. first query truncated).
        created_at, updated_at: Timestamps.
    """

    __tablename__ = Table.CONVERSATION

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    session_id = Column(BigInteger, ForeignKey(Table.SESSION + ".id"), nullable=True, index=True)
    title = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ConversationMessage(Base):
    """
    One message in a conversation (user or assistant).

    Attributes:
        id: Primary key.
        conversation_id: FK to conversations.
        role: "user" | "assistant" | "system".
        content: Message text.
        created_at: When the message was added.
    """

    __tablename__ = Table.CONVERSATION_MESSAGE

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id = Column(
        BigInteger,
        ForeignKey(Table.CONVERSATION + ".id"),
        nullable=False,
        index=True,
    )
    role = Column(String(32), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
