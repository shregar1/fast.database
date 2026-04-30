"""Location Lookup Repository.

Data access for the LocationLk model (city, state, country, country_code,
pin_code). IRepository wrapper; use for retrieve by id or composite, list
with filters. Used by Profile for location_id.

Usage:
    >>> from fastx_database.persistence.repositories.location_lk import LocationLkRepository
    >>> repo = LocationLkRepository(session=db_session)
"""

from sqlalchemy.orm import Session

from fastx_database.persistence.repositories.abstraction import IRepository
from fastx_database.persistence.models.location_lk import LocationLk


class LocationLkRepository(IRepository):
    """Repository for LocationLk (location) records.

    Provides session and IRepository base. Use for resolving location_id and
    listing locations for profile/address forms.
    """

    def __init__(
        self,
        session: Session = None,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ):
        """Execute __init__ operation.

        Args:
            session: The session parameter.
            urn: The urn parameter.
            user_urn: The user_urn parameter.
            api_name: The api_name parameter.
            user_id: The user_id parameter.
        """
        self._cache = None
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            cache=self._cache,
            model=LocationLk,
        )
        self._session = session

    @property
    def session(self) -> Session:
        """Execute session operation.

        Returns:
            The result of the operation.
        """
        return self._session

    @session.setter
    def session(self, value: Session):
        """Execute session operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._session = value

    def list_all(self):
        """Return all location lookup entries ordered by city, state, country."""
        return (
            self.session.query(LocationLk)
            .order_by(LocationLk.country, LocationLk.state, LocationLk.city)
            .all()
        )
