"""
Consent record model (ToS, privacy, marketing, cookies).

Immutable rows: each acceptance is a new row with document version and timestamp.
Used for compliance (GDPR audit trail, versioned policy acceptance).

Usage:
    >>> from fast_database.persistence.models.consent_record import ConsentRecord
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text

from sqlalchemy.dialects.postgresql import JSONB

from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class ConsentRecord(Base):
    """
    Records that a user accepted a policy version (legal/compliance).

    Attributes:
        id: Primary key.
        user_id: Subject (FK ``user.id``).
        consent_type: e.g. ``tos``, ``privacy``, ``marketing``, ``cookies``.
        document_version: Version string or hash of the document shown (e.g. ``2025-03-01``).
        ip_address: Optional client IP at acceptance time.
        user_agent: Optional UA string.
        consent_metadata: Optional JSON (locale, A/B bucket, etc.).
        accepted_at: When the user accepted (UTC).
    """

    __tablename__ = Table.CONSENT

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(f"{Table.USER}.id", ondelete="CASCADE"), nullable=False, index=True)
    consent_type = Column(String(64), nullable=False, index=True)
    document_version = Column(String(128), nullable=False)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(Text, nullable=True)
    consent_metadata = Column("metadata", JSONB, nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
