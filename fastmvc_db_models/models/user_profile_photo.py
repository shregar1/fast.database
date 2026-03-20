"""
User Profile Photo Model.

SQLAlchemy ORM model for profile photos. Schema allows one user_id per row
(unique); order_sequence and primary designation are typically enforced by
profile.primary_photo_id pointing to the main photo.

Usage:
    >>> from fastmvc_db_models.models.user_profile_photo import UserProfilePhoto
    >>> # profile.primary_photo_id references this; order_sequence for display order
"""



from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String

from fastmvc_db_models.constants.db.table import Table
from fastmvc_db_models.models import Base


class UserProfilePhoto(Base):
    """
    Profile photo record for a user (photo URL and optional order/description).

    Stores photo_url, optional description, order_sequence for sorting, and
    is_deleted. Profile.primary_photo_id references the main avatar; multiple
    rows per user allowed for galleries, with user_id unique in current schema.

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        user_id: FK to user (unique in schema).
        photo_url: URL or path to the image.
        description: Optional caption.
        order_sequence: Display order.
        is_deleted: Soft-delete flag.
        created_at, updated_at, created_by, updated_by: Audit fields.
    """



    __tablename__ = Table.USER_PROFILE_PHOTO

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, unique=True, index=True)
    photo_url = Column(String(1024), nullable=False)
    description = Column(String(255), nullable=True)
    order_sequence = Column(Integer, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    updated_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    def to_dict(self) -> dict:
        return {
            "urn": self.urn,
            "user_id": self.user_id,
            "photo_url": self.photo_url,
            "description": self.description,
            "order_sequence": self.order_sequence,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
