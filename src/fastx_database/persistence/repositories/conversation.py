"""Conversation repository.

Data access for Conversation and ConversationMessage: list by user (optional
session_id filter, pagination), get by id with messages, create conversation
and append messages.
"""

from datetime import datetime, timezone

from sqlalchemy import nulls_last
from sqlalchemy.orm import Session

from fastx_database.core.constants.messages import ERROR_DB_SESSION_NOT_FOUND
from fastx_database.core.constants.pagination import Pagination
from fastx_database.persistence.repositories.abstraction import IRepository
from fastx_database.persistence.models.conversation import (
    Conversation,
    ConversationMessage,
)


class ConversationRepository(IRepository):
    """Represents the ConversationRepository class."""

    def __init__(
        self,
        session: Session | None = None,
        *,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            session: The session parameter.
            urn: The urn parameter.
            user_urn: The user_urn parameter.
            api_name: The api_name parameter.
            user_id: The user_id parameter.
        """
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            model=Conversation,
            cache=None,
        )
        self._session = session
        if not self._session:
            raise RuntimeError(ERROR_DB_SESSION_NOT_FOUND)

    @property
    def session(self) -> Session:
        """Execute session operation.

        Returns:
            The result of the operation.
        """
        return self._session

    def create(
        self, user_id: int, session_id: int | None = None, title: str | None = None
    ) -> Conversation:
        """Execute create operation.

        Args:
            user_id: The user_id parameter.
            session_id: The session_id parameter.
            title: The title parameter.

        Returns:
            The result of the operation.
        """
        conv = Conversation(user_id=user_id, session_id=session_id, title=title)
        self.session.add(conv)
        self.session.flush()
        return conv

    def get_by_id(
        self, conversation_id: int, user_id: int | None = None
    ) -> Conversation | None:
        """Execute get_by_id operation.

        Args:
            conversation_id: The conversation_id parameter.
            user_id: The user_id parameter.

        Returns:
            The result of the operation.
        """
        q = self.session.query(Conversation).filter(Conversation.id == conversation_id)
        if user_id is not None:
            q = q.filter(Conversation.user_id == user_id)
        return q.first()

    def list_by_user(
        self,
        user_id: int,
        session_id: int | None = None,
        skip: int = 0,
        limit: int = Pagination.CHAT_LIMIT,
    ) -> list[Conversation]:
        """Execute list_by_user operation.

        Args:
            user_id: The user_id parameter.
            session_id: The session_id parameter.
            skip: The skip parameter.
            limit: The limit parameter.

        Returns:
            The result of the operation.
        """
        q = self.session.query(Conversation).filter(Conversation.user_id == user_id)
        if session_id is not None:
            q = q.filter(Conversation.session_id == session_id)
        q = q.order_by(
            nulls_last(Conversation.updated_at.desc()), Conversation.created_at.desc()
        )
        return q.offset(skip).limit(limit).all()

    def count_by_user(self, user_id: int, session_id: int | None = None) -> int:
        """Execute count_by_user operation.

        Args:
            user_id: The user_id parameter.
            session_id: The session_id parameter.

        Returns:
            The result of the operation.
        """
        q = self.session.query(Conversation).filter(Conversation.user_id == user_id)
        if session_id is not None:
            q = q.filter(Conversation.session_id == session_id)
        return q.count()

    def add_message(
        self, conversation_id: int, role: str, content: str
    ) -> ConversationMessage:
        """Execute add_message operation.

        Args:
            conversation_id: The conversation_id parameter.
            role: The role parameter.
            content: The content parameter.

        Returns:
            The result of the operation.
        """
        msg = ConversationMessage(
            conversation_id=conversation_id, role=role, content=content
        )
        self.session.add(msg)
        self.session.flush()
        now = datetime.now(timezone.utc)
        self.session.query(Conversation).filter(
            Conversation.id == conversation_id
        ).update({"updated_at": now}, synchronize_session=False)
        return msg

    def get_messages_ordered(self, conversation_id: int) -> list[ConversationMessage]:
        """Execute get_messages_ordered operation.

        Args:
            conversation_id: The conversation_id parameter.

        Returns:
            The result of the operation.
        """
        return (
            self.session.query(ConversationMessage)
            .filter(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.created_at.asc())
            .all()
        )
