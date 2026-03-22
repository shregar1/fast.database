"""
Plan Model.

SQLAlchemy ORM model for plan definitions and entitlement limits keyed by plan_code.
Used by:
    - GET /api/v1/plans (catalog)
    - Entitlements, plan rate limits, and upgrade flows
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String
from sqlalchemy.types import JSON

from fast_database.constants.db.table import Table
from fast_database.models import Base


class Plan(Base):
    """
    Plan definition and limits.

    Attributes:
        id: Primary key.
        plan_code: Stable identifier (e.g. free, pro).
        name: Display name.
        sessions_per_month: Session allowance for the plan.
        models_allowed: List of allowed model identifiers (JSON array).
        is_active: Whether plan is currently offered.
        created_at, updated_at: Timestamps.
    """

    __tablename__ = Table.PLAN

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    plan_code = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(128), nullable=False)
    sessions_per_month = Column(Integer, nullable=False, default=0)
    models_allowed = Column(JSON, nullable=False, default=list)
    is_active = Column(Boolean, nullable=False, default=True, index=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "plan_code": self.plan_code,
            "name": self.name,
            "sessions_per_month": self.sessions_per_month,
            "models_allowed": self.models_allowed,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

