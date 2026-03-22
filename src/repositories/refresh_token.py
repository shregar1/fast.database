"""
Refresh Token Repository.

Data access for RefreshToken (jti, user_id, family_id, revoked_at).
Create, get by jti, list by user, revoke by jti, revoke all for user except jti.
Used for refresh token rotation and session/device list and revoke.
"""



from datetime import datetime, timezone

from sqlalchemy.orm import Session

from fast_database.repositories.abstraction import IRepository
from fast_database.models.refresh_token import RefreshToken


class RefreshTokenRepository(IRepository):
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
            model=RefreshToken,
            cache=None,
        )
        self._session = session
        if not self._session:
            raise RuntimeError("DB session not found")

    @property
    def session(self) -> Session:
        return self._session

    def create(self, jti: str, user_id: int, family_id: str, expires_at: datetime) -> RefreshToken:
        record = RefreshToken(
            jti=jti,
            user_id=user_id,
            family_id=family_id,
            expires_at=expires_at,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def get_by_jti(self, jti: str) -> RefreshToken | None:
        return (
            self.session.query(RefreshToken)
            .filter(RefreshToken.jti == jti)
            .first()
        )

    def list_by_user(
        self,
        user_id: int,
        include_revoked: bool = False,
        limit: int = 100,
    ) -> list[RefreshToken]:
        q = self.session.query(RefreshToken).filter(RefreshToken.user_id == user_id)
        if not include_revoked:
            q = q.filter(RefreshToken.revoked_at.is_(None))
        now = datetime.now(timezone.utc)
        q = q.filter(RefreshToken.expires_at > now)
        return q.order_by(RefreshToken.created_at.desc()).limit(limit).all()

    def revoke_by_jti(self, jti: str) -> bool:
        now = datetime.now(timezone.utc)
        n = (
            self.session.query(RefreshToken)
            .filter(RefreshToken.jti == jti)
            .update({"revoked_at": now}, synchronize_session="fetch")
        )
        self.session.commit()
        return n > 0

    def revoke_all_for_user_except_jti(self, user_id: int, except_jti: str) -> int:
        now = datetime.now(timezone.utc)
        subq = (
            self.session.query(RefreshToken.id)
            .filter(RefreshToken.user_id == user_id)
            .filter(RefreshToken.jti != except_jti)
            .filter(RefreshToken.revoked_at.is_(None))
        )
        # Update by id to avoid dialect issues
        count = (
            self.session.query(RefreshToken)
            .filter(RefreshToken.user_id == user_id)
            .filter(RefreshToken.jti != except_jti)
            .filter(RefreshToken.revoked_at.is_(None))
            .update({"revoked_at": now}, synchronize_session="fetch")
        )
        self.session.commit()
        return count
