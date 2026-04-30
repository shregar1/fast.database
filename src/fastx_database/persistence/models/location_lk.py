"""Location Lookup Model.

SQLAlchemy ORM model for locations: city, state, country, country_code, and
optional pin_code. Unique on (city, state, country_code, pin_code). Referenced
by profile.location_id.

Usage:
    >>> from fastx_database.persistence.models.location_lk import LocationLk
    >>> # Used for profile location (e.g. city, state, country)
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String, UniqueConstraint

from fastx_database.core.constants.table import Table
from fastx_database.persistence.models import Base


class LocationLk(Base):
    """Lookup: location (city, state, country, pin_code).

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        city, state, country, country_code: Location components.
        pin_code: Optional postal code.
        created_at, updated_at: Timestamps.

    """

    __tablename__ = Table.LOCATION_LK
    __table_args__ = (
        UniqueConstraint(
            "city",
            "state",
            "country_code",
            "pin_code",
            name="uq_location_lk_city_state_country_pin",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    city = Column(String(128), nullable=False, index=True)
    state = Column(String(128), nullable=False, index=True)
    country = Column(String(128), nullable=False, index=True)
    country_code = Column(String(8), nullable=False, index=True)
    pin_code = Column(String(32), nullable=True, index=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow
    )

    def to_dict(self) -> dict:
        """Execute to_dict operation.

        Returns:
            The result of the operation.
        """
        return {
            "urn": self.urn,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "country_code": self.country_code,
            "pin_code": self.pin_code,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
