"""
Session Repository.

Data access layer for the Session model. Works with both the shared
`fast_database` Session (minimal columns) and extended deployments that add
URN, job fields, soft-delete, etc.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func, literal
from sqlalchemy.orm import Session

from fast_database.repositories.abstraction import IRepository
from fast_database.soft_delete import filter_active
from fast_database.models.session import Session as SessionModel


def _owner_column():
    if hasattr(SessionModel, "created_by"):
        return SessionModel.created_by
    if hasattr(SessionModel, "user_id"):
        return SessionModel.user_id
    return None


def _range_time_column():
    """Prefer started_at for billing windows; fall back to created_at."""
    if hasattr(SessionModel, "started_at"):
        return SessionModel.started_at
    if hasattr(SessionModel, "created_at"):
        return SessionModel.created_at
    return None


def _apply_not_deleted(query):
    if hasattr(SessionModel, "is_deleted"):
        return filter_active(query, SessionModel.is_deleted)
    return query


def _apply_text_search(query, term: str):
    """Search JD/resume when present; otherwise title."""
    t = f"%{term.strip()}%"
    parts = []
    if hasattr(SessionModel, "job_description"):
        parts.append(SessionModel.job_description.ilike(t))
    if hasattr(SessionModel, "resume"):
        parts.append(SessionModel.resume.ilike(t))
    if hasattr(SessionModel, "title"):
        parts.append(SessionModel.title.ilike(t))
    if not parts:
        return query
    combined = parts[0]
    for p in parts[1:]:
        combined = combined | p
    return query.filter(combined)


class SessionRepository(IRepository):
    """
    Repository for Session database operations.
    """

    def __init__(
        self,
        session: Session | None = None,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        self._cache = None
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            cache=self._cache,
            model=SessionModel,
        )
        self._session = session

    @property
    def session(self) -> Session | None:
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        self._session = value

    def create_record(self, record: SessionModel) -> SessionModel:
        uid = getattr(record, "user_id", None)
        cb = getattr(record, "created_by", None)
        self.logger.debug(f"Creating session: user_id={uid}, created_by={cb}")
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        self.logger.info(f"Created session with ID: {record.id}")

        return record

    def retrieve_record_by_id(self, record_id: int) -> SessionModel | None:
        self.logger.debug(f"Retrieving session by ID: {record_id}")

        return (
            self.session.query(SessionModel)
            .filter(SessionModel.id == record_id)
            .first()
        )

    def retrieve_record_by_urn(self, urn: str) -> SessionModel | None:
        self.logger.debug(f"Retrieving session by URN: {urn}")
        if not hasattr(SessionModel, "urn"):
            self.logger.debug("Session model has no urn column; skipping URN lookup.")
            return None

        return (
            self.session.query(SessionModel)
            .filter(SessionModel.urn == urn)
            .first()
        )

    def retrieve_records(
        self,
        created_by: int | None = None,
        user_id: int | None = None,
        started_at_from: datetime | None = None,
        started_at_to: datetime | None = None,
        q: str | None = None,
        skip: int = 0,
        limit: int = 100,
        **kwargs: Any,
    ) -> tuple[list[SessionModel], int]:
        """
        List sessions with optional filters. Returns (items, total_count).
        user_id is an alias for created_by when the model uses created_by.
        """
        owner = created_by if created_by is not None else user_id
        self.logger.debug(
            f"Retrieving sessions: created_by={owner}, "
            f"started_at_from={started_at_from}, started_at_to={started_at_to}, q={q!r}, "
            f"skip={skip}, limit={limit}"
        )
        query = self.session.query(SessionModel)
        query = _apply_not_deleted(query)
        oc = _owner_column()
        if owner is not None and oc is not None:
            query = query.filter(oc == owner)
        tc = _range_time_column()
        if tc is not None:
            if started_at_from is not None:
                query = query.filter(tc >= started_at_from)
            if started_at_to is not None:
                query = query.filter(tc <= started_at_to)
        if q and q.strip():
            query = _apply_text_search(query, q)
        total = query.count()

        order_col = tc if tc is not None else SessionModel.id
        items = query.order_by(order_col.desc()).offset(skip).limit(limit).all()

        return items, total

    def count_sessions_for_user_in_month(self, created_by: int, year: int, month: int) -> int:
        """Count sessions for user in the given calendar month (for entitlements)."""
        from calendar import monthrange

        start = datetime(year, month, 1)
        _, last_day = monthrange(year, month)
        end = datetime(year, month, last_day, 23, 59, 59, 999999)

        q = self.session.query(SessionModel)
        q = _apply_not_deleted(q)
        oc = _owner_column()
        if oc is not None:
            q = q.filter(oc == created_by)
        tc = _range_time_column()
        if tc is not None:
            q = q.filter(tc >= start).filter(tc <= end)
        if hasattr(SessionModel, "consumes_session_credit"):
            q = q.filter(SessionModel.consumes_session_credit.is_(True))
        return q.count()

    def usage_for_user_in_month(
        self, created_by: int, year: int, month: int
    ) -> dict[str, Any]:
        """Aggregate usage for billing/limits for the calendar month."""
        from calendar import monthrange

        start = datetime(year, month, 1)
        _, last_day = monthrange(year, month)
        end = datetime(year, month, last_day, 23, 59, 59, 999999)

        q = self.session.query(SessionModel)
        q = _apply_not_deleted(q)
        oc = _owner_column()
        if oc is not None:
            q = q.filter(oc == created_by)
        tc = _range_time_column()
        if tc is not None:
            q = q.filter(tc >= start).filter(tc <= end)
        if hasattr(SessionModel, "consumes_session_credit"):
            q = q.filter(SessionModel.consumes_session_credit.is_(True))
        count = q.count()

        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_tokens = 0
        total_messages = 0
        total_cost_usd = 0.0
        if hasattr(SessionModel, "total_prompt_tokens"):
            agg_base = self.session.query(SessionModel)
            agg_base = _apply_not_deleted(agg_base)
            if oc is not None:
                agg_base = agg_base.filter(oc == created_by)
            if tc is not None:
                agg_base = agg_base.filter(tc >= start).filter(tc <= end)
            if hasattr(SessionModel, "consumes_session_credit"):
                agg_base = agg_base.filter(SessionModel.consumes_session_credit.is_(True))
            cols = [func.coalesce(func.sum(SessionModel.total_prompt_tokens), 0)]
            if hasattr(SessionModel, "total_completion_tokens"):
                cols.append(func.coalesce(func.sum(SessionModel.total_completion_tokens), 0))
            else:
                cols.append(literal(0))
            if hasattr(SessionModel, "total_tokens"):
                cols.append(func.coalesce(func.sum(SessionModel.total_tokens), 0))
            else:
                cols.append(literal(0))
            if hasattr(SessionModel, "total_messages"):
                cols.append(func.coalesce(func.sum(SessionModel.total_messages), 0))
            else:
                cols.append(literal(0))
            if hasattr(SessionModel, "total_cost_usd"):
                cols.append(func.coalesce(func.sum(SessionModel.total_cost_usd), 0))
            else:
                cols.append(literal(0))
            row = agg_base.with_entities(*cols).first()
            if row:
                total_prompt_tokens = int(row[0] or 0)
                total_completion_tokens = int(row[1] or 0)
                total_tokens = int(row[2] or 0)
                total_messages = int(row[3] or 0)
                try:
                    total_cost_usd = float(row[4] or 0)
                except (TypeError, ValueError):
                    total_cost_usd = 0.0

        return {
            "sessions_count": count,
            "total_prompt_tokens": total_prompt_tokens,
            "total_completion_tokens": total_completion_tokens,
            "total_tokens": total_tokens,
            "total_messages": total_messages,
            "total_cost_usd": total_cost_usd,
        }

    def list_feedback(
        self,
        created_by: int | None = None,
        started_at_from: datetime | None = None,
        started_at_to: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[SessionModel], int]:
        """List sessions (feedback-specific columns may be absent)."""
        query = self.session.query(SessionModel)
        query = _apply_not_deleted(query)
        oc = _owner_column()
        if created_by is not None and oc is not None:
            query = query.filter(oc == created_by)
        tc = _range_time_column()
        if tc is not None:
            if started_at_from is not None:
                query = query.filter(tc >= started_at_from)
            if started_at_to is not None:
                query = query.filter(tc <= started_at_to)
        total = query.count()

        order_col = tc if tc is not None else SessionModel.id
        items = query.order_by(order_col.desc()).offset(skip).limit(limit).all()

        return list(items), total

    def feedback_aggregate(
        self,
        created_by: int | None = None,
        started_at_from: datetime | None = None,
        started_at_to: datetime | None = None,
    ) -> dict[str, Any]:
        """Schema sessions have no feedback; return empty aggregate."""
        return {
            "count": 0,
            "average_rating": None,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        }

    def update_record(self, record: SessionModel) -> SessionModel:
        self.logger.debug(f"Updating session: {record.id}")
        self.session.commit()
        self.session.refresh(record)
        self.logger.info(f"Updated session: {record.id}")

        return record

    def delete_record(self, record_id: int) -> bool:
        """Hard delete a session record."""
        self.logger.debug(f"Deleting session: {record_id}")
        record = self.retrieve_record_by_id(record_id)
        if not record:
            return False
        self.session.delete(record)

        self.session.commit()
        self.logger.info(f"Deleted session: {record_id}")

        return True
