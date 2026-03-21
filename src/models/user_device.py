"""
User Device Model.

SQLAlchemy ORM model for devices associated with a user account. One row per
distinct device (identified by device_fingerprint): type, OS, user agent, IP,
last_seen_at, and is_current for the active device. Unique on (user_id, device_fingerprint).

Usage:
    >>> from fastmvc_db_models.models.user_device import UserDevice
    >>> # Used for device management and security (e.g. list/revoke devices)
"""



from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint

from src.constants.db.table import Table
from src.models import Base


class UserDevice(Base):
    """
    One registered device per user (identified by fingerprint).

    Tracks device_fingerprint, device_type, os, user_agent, ip_address,
    last_seen_at, and is_current (current session's device). Unique constraint
    on (user_id, device_fingerprint). is_deleted for soft delete.

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        user_id: FK to user.
        device_fingerprint: Stable device identifier.
        device_type, os, user_agent: Client info.
        ip_address: Last known IP.
        last_seen_at: Last activity on this device.
        is_current: True for the device used in current session.
        is_deleted: Soft-delete flag.
        created_at, updated_at, created_by, updated_by: Audit fields.
    """



    __tablename__ = Table.USER_DEVICE
    __table_args__ = (
        UniqueConstraint("user_id", "device_fingerprint", name="uq_user_device_user_fingerprint"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    device_fingerprint = Column(String(256), nullable=False, index=True)
    device_type = Column(String(64), nullable=True)
    os = Column(String(128), nullable=True)
    user_agent = Column(String(512), nullable=True)
    ip_address = Column(String(64), nullable=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    is_current = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    updated_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    def to_dict(self) -> dict:
        return {
            "urn": self.urn,
            "user_id": self.user_id,
            "device_fingerprint": self.device_fingerprint,
            "device_type": self.device_type,
            "os": self.os,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
            "last_seen_at": self.last_seen_at.isoformat() if self.last_seen_at else None,
            "is_current": self.is_current,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
