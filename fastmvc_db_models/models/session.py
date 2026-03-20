"""
Session Model.

SQLAlchemy ORM model for interview or processing sessions. Each session stores
a job description and resume (e.g. text or references), optional JSONB data
for derived/structured results, and started_at/ended_at for lifecycle.

Usage:
    >>> from fastmvc_db_models.models.session import Session
    >>> # Sessions are created/updated by services; data holds processing output
"""



from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB

from fastmvc_db_models.constants.db.table import Table
from fastmvc_db_models.models import Base


class Session(Base):
    """
    Interview or processing session (resume + job description + derived data).

    Represents one "run" of an interview or analysis: inputs (job_description,
    resume), optional structured output in data (JSONB), and time bounds.
    created_by/updated_by track ownership and audit.

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        job_description: Input job description (text or reference).
        resume: Input resume (text or reference).
        data: JSONB for derived/structured results (optional).
        is_deleted: Soft-delete flag.
        started_at, ended_at: Session time window.
        created_at, updated_at, created_by, updated_by: Audit fields.
    """



    __tablename__ = Table.SESSION

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    job_description = Column(String(512), nullable=False)
    resume = Column(String(512), nullable=False)
    data = Column(JSONB, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    updated_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)
    # When True, session counts toward monthly limit; when False (analysis engine or refunded), it does not.
    consumes_session_credit = Column(Boolean, nullable=False, default=True)

    def to_dict(self) -> dict:

        return {
            "urn": self.urn,
            "job_description": self.job_description,
            "resume": self.resume,
            "data": self.data,
            "is_deleted": self.is_deleted,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
