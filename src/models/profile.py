"""
Profile Model.

SQLAlchemy ORM model for extended user profile data. One profile per user:
demographics (name, gender, DoB, education, location), verification and
visibility flags, and optional primary photo reference.

Usage:
    >>> from fast_database.models.profile import Profile
    >>> # Linked to User via user_id; gender_id, education_level_id, location_id use lk tables
"""



from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, ForeignKey, String, Text

from fast_database.constants.db.table import Table
from fast_database.models import Base


class Profile(Base):
    """
    Extended user profile (one-to-one with User).

    Holds display name, bio, date of birth, education level, organisation,
    location, and verification/premium/visibility flags. primary_photo_id
    references user_profile_photo for the main avatar.

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        user_id: FK to user (unique); one profile per user.
        is_verified: Whether profile has been verified.
        first_name, middle_name, last_name: Display name components.
        primary_photo_id: FK to user_profile_photo (optional).
        gender_id: FK to gender_lk.
        date_of_birth: Date of birth.
        bio: Free-text biography.
        education_level_id: FK to education_level_lk.
        current_organisation: Organisation name.
        location_id: FK to location_lk (optional).
        is_premium, is_hidden, is_deleted: Feature and visibility flags.
        created_at, updated_at, created_by, updated_by: Audit fields.
    """



    __tablename__ = Table.PROFILE

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, unique=True, index=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    first_name = Column(String(128), nullable=False)
    middle_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    primary_photo_id = Column(BigInteger, ForeignKey("user_profile_photo.id"), nullable=True)
    gender_id = Column(BigInteger, ForeignKey("gender_lk.id"), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    bio = Column(Text, nullable=True)
    education_level_id = Column(BigInteger, ForeignKey("education_level_lk.id"), nullable=False)
    current_organisation = Column(String(255), nullable=False)
    location_id = Column(BigInteger, ForeignKey("location_lk.id"), nullable=True)
    is_premium = Column(Boolean, nullable=False, default=False)
    is_hidden = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    updated_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    def to_dict(self) -> dict:

        return {
            "urn": self.urn,
            "user_id": self.user_id,
            "is_verified": self.is_verified,
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "last_name": self.last_name,
            "primary_photo_id": self.primary_photo_id,
            "gender_id": self.gender_id,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "bio": self.bio,
            "education_level_id": self.education_level_id,
            "current_organisation": self.current_organisation,
            "location_id": self.location_id,
            "is_premium": self.is_premium,
            "is_hidden": self.is_hidden,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
