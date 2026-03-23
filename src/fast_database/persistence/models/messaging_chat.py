"""
User-to-user messaging models (chats, messages, read receipts, notification delivery).

Distinct from :class:`Conversation` / :class:`ConversationMessage`, which model
LLM threads (role + content). These tables support direct/group chat, delivery
tracking, and per-recipient read status.

Usage:
    >>> from fast_database.persistence.models.messaging_chat import Chat, ChatMessage
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class Chat(Base):
    """
    A chat thread: direct (two participants), group, or channel-style.

    ``kind`` is a short string (e.g. ``direct``, ``group``, ``channel``).
    ``last_message_at`` can be denormalized for sort order; update in application code.
    """

    __tablename__ = Table.CHAT

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    kind = Column(String(32), nullable=False, index=True)
    title = Column(String(512), nullable=True)
    organization_id = Column(
        BigInteger,
        ForeignKey(Table.ORGANIZATION + ".id"),
        nullable=True,
        index=True,
    )
    created_by_user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    last_message_at = Column(DateTime(timezone=True), nullable=True, index=True)
    is_archived = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": self.kind,
            "title": self.title,
            "organization_id": self.organization_id,
            "created_by_user_id": self.created_by_user_id,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ChatParticipant(Base):
    """
    User membership in a chat: role, mute, notification rules, last-read cursor.

    ``notification_level``: ``all`` (every message), ``mentions`` (only @mentions),
    ``mute`` (no notifications).
    ``last_read_message_id`` points to the newest message this user has consumed
    for unread counts; per-message receipts live in :class:`MessageReadReceipt`.
    """

    __tablename__ = Table.CHAT_PARTICIPANT
    __table_args__ = (
        UniqueConstraint("chat_id", "user_id", name="uq_chat_participant_chat_user"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(
        BigInteger,
        ForeignKey(Table.CHAT + ".id"),
        nullable=False,
        index=True,
    )
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    role = Column(String(32), nullable=False, default="member", index=True)
    notification_level = Column(String(32), nullable=False, default="all", index=True)
    joined_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    left_at = Column(DateTime(timezone=True), nullable=True, index=True)
    muted_until = Column(DateTime(timezone=True), nullable=True)
    last_read_message_id = Column(
        BigInteger,
        ForeignKey(Table.CHAT_MESSAGE + ".id"),
        nullable=True,
        index=True,
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "user_id": self.user_id,
            "role": self.role,
            "notification_level": self.notification_level,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "left_at": self.left_at.isoformat() if self.left_at else None,
            "muted_until": self.muted_until.isoformat() if self.muted_until else None,
            "last_read_message_id": self.last_read_message_id,
        }


class ChatMessage(Base):
    """
    A single user-authored (or system) message inside a chat.

    ``content_type``: ``text``, ``image``, ``file``, ``audio``, ``video``, ``system``, etc.
    ``body`` may be null for attachment-only messages; use ``message_metadata`` for keys/URLs.
    """

    __tablename__ = Table.CHAT_MESSAGE

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(
        BigInteger,
        ForeignKey(Table.CHAT + ".id"),
        nullable=False,
        index=True,
    )
    sender_user_id = Column(BigInteger, ForeignKey("user.id"), nullable=True, index=True)
    content_type = Column(String(32), nullable=False, default="text", index=True)
    body = Column(Text, nullable=True)
    reply_to_message_id = Column(
        BigInteger,
        ForeignKey(Table.CHAT_MESSAGE + ".id"),
        nullable=True,
        index=True,
    )
    message_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    read_receipts = relationship(
        "MessageReadReceipt",
        back_populates="message",
        cascade="all, delete-orphan",
    )
    notification_deliveries = relationship(
        "ChatMessageNotification",
        back_populates="message",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "sender_user_id": self.sender_user_id,
            "content_type": self.content_type,
            "body": self.body,
            "reply_to_message_id": self.reply_to_message_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "edited_at": self.edited_at.isoformat() if self.edited_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }


class MessageReadReceipt(Base):
    """
    Read / seen receipt: when ``user_id`` first read ``message_id``.

    One row per (message, user). Use for blue ticks and “seen by” lists.
    """

    __tablename__ = Table.MESSAGE_READ_RECEIPT
    __table_args__ = (
        UniqueConstraint("message_id", "user_id", name="uq_message_read_receipt_msg_user"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    message_id = Column(
        BigInteger,
        ForeignKey(Table.CHAT_MESSAGE + ".id"),
        nullable=False,
        index=True,
    )
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)

    message = relationship("ChatMessage", back_populates="read_receipts")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "message_id": self.message_id,
            "user_id": self.user_id,
            "read_at": self.read_at.isoformat() if self.read_at else None,
        }


class ChatMessageNotification(Base):
    """
    Outbound notification attempt for a chat message (push, email, SMS).

    Tracks provider idempotency and delivery state separate from
    :class:`NotificationHistory` (in-app feed).
    """

    __tablename__ = Table.CHAT_MESSAGE_NOTIFICATION
    __table_args__ = (
        UniqueConstraint(
            "message_id",
            "recipient_user_id",
            "channel",
            name="uq_chat_msg_notification_msg_recipient_channel",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    message_id = Column(
        BigInteger,
        ForeignKey(Table.CHAT_MESSAGE + ".id"),
        nullable=False,
        index=True,
    )
    recipient_user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    channel = Column(String(32), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="pending", index=True)
    provider_message_id = Column(String(255), nullable=True, index=True)
    error_message = Column(String(1024), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    message = relationship("ChatMessage", back_populates="notification_deliveries")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "message_id": self.message_id,
            "recipient_user_id": self.recipient_user_id,
            "channel": self.channel,
            "status": self.status,
            "provider_message_id": self.provider_message_id,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
