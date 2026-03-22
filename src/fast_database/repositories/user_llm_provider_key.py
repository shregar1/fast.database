"""
Repository for per-user LLM provider API keys (encrypted at rest).

Usage:
    >>> from fast_database.repositories.user_llm_provider_key import UserLlmProviderKeyRepository
    >>> repo = UserLlmProviderKeyRepository(session=db_session)
    >>> row = repo.upsert(...)
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from fast_database.models.user_provider_key import UserProviderKey
from fast_database.repositories.abstraction import IRepository


class UserLlmProviderKeyRepository(IRepository):
    """CRUD for :class:`~fast_database.models.user_provider_key.UserProviderKey`."""

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
            model=UserProviderKey,
            cache=None,
        )
        self._session = session
        if not self._session:
            raise RuntimeError("DB session not found")

    @property
    def session(self) -> Session:
        return self._session

    def get_by_user_and_provider(self, user_id: int, provider: str) -> UserProviderKey | None:
        return (
            self.session.query(UserProviderKey)
            .filter(
                UserProviderKey.user_id == user_id,
                UserProviderKey.provider == provider,
            )
            .first()
        )

    def list_by_user_id(self, user_id: int) -> list[UserProviderKey]:
        return list(
            self.session.query(UserProviderKey)
            .filter(UserProviderKey.user_id == user_id)
            .order_by(UserProviderKey.provider.asc())
            .all()
        )

    def upsert(
        self,
        user_id: int,
        provider: str,
        secret_ciphertext: str,
        *,
        is_encrypted_by_client: bool = False,
        key_last_four: str | None = None,
    ) -> UserProviderKey:
        now = datetime.now(timezone.utc)
        existing = self.get_by_user_and_provider(user_id, provider)
        if existing:
            existing.secret_ciphertext = secret_ciphertext
            existing.is_encrypted_by_client = is_encrypted_by_client
            existing.key_last_four = key_last_four
            existing.updated_at = now
            self.session.commit()
            self.session.refresh(existing)
            return existing

        rec = UserProviderKey(
            user_id=user_id,
            provider=provider,
            secret_ciphertext=secret_ciphertext,
            is_encrypted_by_client=is_encrypted_by_client,
            key_last_four=key_last_four,
            created_at=now,
            updated_at=now,
        )
        self.session.add(rec)
        self.session.commit()
        self.session.refresh(rec)
        return rec

    def delete(self, user_id: int, provider: str) -> bool:
        rec = self.get_by_user_and_provider(user_id, provider)
        if not rec:
            return False
        self.session.delete(rec)
        self.session.commit()
        return True
