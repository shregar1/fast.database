"""
API Key Repository.

Data access for API keys (server-to-server auth). Extends :class:`~fast_repositories.repository.IRepository`.
Supports create (with key_hash, name, scopes),
lookup by key_hash (active only), list by user_id (optional include_revoked),
revoke single key or all keys for a user, and update_last_used for usage tracking.

Usage:
    >>> from fast_repositories.api_key import ApiKeyRepository
    >>> repo = ApiKeyRepository(session=db_session)
    >>> key = repo.create(user_id=1, key_hash=hash, name="CI", scopes=["read_only"])
    >>> key = repo.get_by_key_hash(key_hash)
    >>> keys = repo.list_by_user_id(user_id=1)
    >>> repo.revoke(key_id=1, user_id=1)
"""



from datetime import datetime, timezone

from sqlalchemy.orm import Session

from fast_repositories.repository import IRepository
from fast_database.models.api_key import ApiKey


class ApiKeyRepository(IRepository):
    """
    Repository for API key CRUD and lookup.

    Create keys with hashed secret and scopes; look up by key_hash (active only);
    list by user; revoke by key id or revoke all for user; update last_used_at
    for analytics. Revoked keys are excluded from get_by_key_hash and list unless
    include_revoked=True.

    Methods:
        create: Insert new ApiKey (user_id, key_hash, name, scopes).
        get_by_key_hash: Find active key by hash.
        list_by_user_id: List keys for user (optional include_revoked).
        revoke: Set revoked_at for one key (returns bool).
        revoke_all_for_user: Revoke all active keys for user (returns count).
        update_last_used: Set last_used_at for key id.
    """



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
            model=ApiKey,
            cache=None,
        )
        self._session = session
        if not self._session:
            raise RuntimeError("DB session not found")

    @property
    def session(self) -> Session:

        return self._session

    def create(self, user_id: int, key_hash: str, name: str, scopes: list[str]) -> ApiKey:
        rec = ApiKey(
            user_id=user_id,
            key_hash=key_hash,
            name=name,
            scopes=scopes or ["full"],
        )
        rec.created_at = datetime.now(timezone.utc)
        self.session.add(rec)
        self.session.commit()
        self.session.refresh(rec)

        return rec

    def get_by_key_hash(self, key_hash: str) -> ApiKey | None:

        return (
            self.session.query(ApiKey)
            .filter(ApiKey.key_hash == key_hash, ApiKey.revoked_at.is_(None))
            .first()
        )

    def get_by_id(self, key_id: int, user_id: int) -> ApiKey | None:
        return (
            self.session.query(ApiKey)
            .filter(ApiKey.id == key_id, ApiKey.user_id == user_id)
            .first()
        )

    def list_by_user_id(self, user_id: int, include_revoked: bool = False) -> list[ApiKey]:
        q = self.session.query(ApiKey).filter(ApiKey.user_id == user_id)
        if not include_revoked:
            q = q.filter(ApiKey.revoked_at.is_(None))

        return list(q.order_by(ApiKey.created_at.desc()).all())

    def update(
        self,
        key_id: int,
        user_id: int,
        name: str | None = None,
        description: str | None = None,
        scopes: list[str] | None = None,
        expires_at: datetime | None = None,
    ) -> ApiKey | None:
        rec = self.get_by_id(key_id, user_id)
        if not rec or rec.revoked_at is not None:
            return None
        if name is not None:
            rec.name = name
        if description is not None:
            rec.description = description
        if scopes is not None:
            rec.scopes = scopes
        if expires_at is not None:
            rec.expires_at = expires_at
        self.session.commit()
        self.session.refresh(rec)
        return rec

    def revoke(self, key_id: int, user_id: int) -> bool:
        rec = (
            self.session.query(ApiKey)
            .filter(ApiKey.id == key_id, ApiKey.user_id == user_id)
            .first()
        )
        if not rec:

            return False
        rec.revoked_at = datetime.now(timezone.utc)

        self.session.commit()

        return True

    def revoke_all_for_user(self, user_id: int) -> int:
        count = (
            self.session.query(ApiKey)
            .filter(ApiKey.user_id == user_id, ApiKey.revoked_at.is_(None))
            .update({"revoked_at": datetime.now(timezone.utc)})
        )
        self.session.commit()

        return count

    def update_last_used(self, key_id: int, ip: str | None = None) -> None:
        rec = self.session.query(ApiKey).filter(ApiKey.id == key_id).first()
        if rec:
            rec.last_used_at = datetime.now(timezone.utc)
            if hasattr(rec, "last_used_ip"):
                rec.last_used_ip = (ip[:45] if ip else None)
            self.session.commit()
