"""Runtime system settings — feature flags and operational knobs stored in DB.

Use for values that must change without redeploying; keep secrets in KMS/Vault when
``is_secret`` is True and store only ciphertext or references in ``value_text``.

Usage:
    >>> from fastx_database.persistence.models.system_setting import SystemSetting
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.dialects.postgresql import JSONB

from fastx_database.core.constants.table import Table
from fastx_database.persistence.models import Base


class SystemSetting(Base):
    """Key/value (or JSON) setting scoped by ``namespace`` (e.g. ``app``, ``billing``).

    Attributes:
        id: Primary key.
        namespace: Logical group; default ``default``.
        key: Setting name (unique per namespace).
        value_text: Plain string value (small config).
        value_json: Structured value (limits, allowlists).
        is_secret: If True, ``value_*`` should be ciphertext or a vault reference only.
        updated_by_user_id: Optional admin who last changed the row.
        created_at / updated_at: Audit timestamps (UTC).

    """

    __tablename__ = Table.SYSTEM_SETTING
    __table_args__ = (
        UniqueConstraint("namespace", "key", name="uq_system_settings_namespace_key"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    namespace = Column(String(64), nullable=False, default="default", index=True)
    key = Column(String(128), nullable=False, index=True)
    value_text = Column(Text, nullable=True)
    value_json = Column(JSONB, nullable=True)
    is_secret = Column(Boolean, nullable=False, default=False)
    updated_by_user_id = Column(BigInteger, nullable=True, index=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
