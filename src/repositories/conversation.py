"""
Conversation repository.

Data access for Conversation and ConversationMessage: list by user (optional
session_id filter, pagination), get by id with messages, create conversation
and append messages.
"""

from datetime import datetime, timezone

from sqlalchemy import nulls_last
from sqlalchemy.orm import Session

from fast_repositories.repository import IRepository
from fast_database.models.conversation import Conversation, ConversationMessage


class ConversationRepository(IRepository):
    def __init__(
        self,
        session: Session | None = None,
        *,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
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
            raise RuntimeError("DB session not found")

    @property
    def session(self) -> Session:
        return self._session

    def create(self, user_id: int, session_id: int | None = None, title: str | None = None) -> Conversation:
        conv = Conversation(user_id=user_id, session_id=session_id, title=title)
        self.session.add(conv)
        self.session.flush()
        return conv

    def get_by_id(self, conversation_id: int, user_id: int | None = None) -> Conversation | None:
        q = self.session.query(Conversation).filter(Conversation.id == conversation_id)
        if user_id is not None:
            q = q.filter(Conversation.user_id == user_id)
        return q.first()

    def list_by_user(
        self,
        user_id: int,
        session_id: int | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Conversation]:
        q = self.session.query(Conversation).filter(Conversation.user_id == user_id)
        if session_id is not None:
            q = q.filter(Conversation.session_id == session_id)
        q = q.order_by(nulls_last(Conversation.updated_at.desc()), Conversation.created_at.desc())
        return q.offset(skip).limit(limit).all()

    def count_by_user(self, user_id: int, session_id: int | None = None) -> int:
        q = self.session.query(Conversation).filter(Conversation.user_id == user_id)
        if session_id is not None:
            q = q.filter(Conversation.session_id == session_id)
        return q.count()

    def add_message(self, conversation_id: int, role: str, content: str) -> ConversationMessage:
        msg = ConversationMessage(conversation_id=conversation_id, role=role, content=content)
        self.session.add(msg)
        self.session.flush()
        now = datetime.now(timezone.utc)
        self.session.query(Conversation).filter(Conversation.id == conversation_id).update(
            {"updated_at": now}, synchronize_session=False
        )
        return msg

    def get_messages_ordered(self, conversation_id: int) -> list[ConversationMessage]:
        return (
            self.session.query(ConversationMessage)
            .filter(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.created_at.asc())
            .all()
        )
