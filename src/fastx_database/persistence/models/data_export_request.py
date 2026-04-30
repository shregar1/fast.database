"""Data export / portability requests (GDPR Art. 20 style).

Track async jobs that bundle user data; store only storage keys or signed URLs, not raw PII in this row.

Usage:
    >>> from fastx_database.persistence.models.data_export_request import DataExportRequest
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text

from fastx_database.core.constants.db import StringLength
from fastx_database.core.constants.status import Status
from fastx_database.core.constants.table import Table
from fastx_database.persistence.models import Base


class DataExportRequest(Base):
    """Lifecycle of a user-requested data export package.

    Attributes:
        id: Primary key.
        user_id: Subject (FK ``user.id``).
        status: ``pending``, ``processing``, ``ready``, ``failed``, ``expired``, ``downloaded``.
        storage_key: Object store key or path to encrypted archive (no public URL in DB).
        download_expires_at: Link/artifact invalid after this time (UTC).
        error_message: Last failure reason for ``failed`` status.
        requested_at: When the user requested the export.
        completed_at: When the archive became available (UTC).

    """

    __tablename__ = Table.DATA_EXPORT_REQUEST

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger,
        ForeignKey(f"{Table.USER}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(String(StringLength.STATUS), nullable=False, default=Status.PENDING, index=True)
    storage_key = Column(Text, nullable=True)
    download_expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    error_message = Column(Text, nullable=True)
    requested_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)
