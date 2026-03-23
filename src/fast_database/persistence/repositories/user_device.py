"""
User Device Repository.

Data access for the UserDevice model (registered devices: fingerprint, type,
OS, last_seen_at, is_current). IRepository wrapper with session and model;
use inherited or service methods for list by user, create, update, revoke.
Used by device management and security flows.

Usage:
    >>> from fast_database.persistence.repositories.user_device import UserDeviceRepository
    >>> repo = UserDeviceRepository(session=db_session, user_id=1)
"""



from sqlalchemy.orm import Session

from fast_database.persistence.repositories.abstraction import IRepository
from fast_database.persistence.models.user_device import UserDevice


class UserDeviceRepository(IRepository):
    """
    Repository for UserDevice (registered device) records.

    Provides session and IRepository base for UserDevice. Use for listing
    devices per user, creating/updating device records, and soft delete
    (revoke) in services.
    """



    def __init__(
        self,
        session: Session = None,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ):
        self._cache = None
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            cache=self._cache,
            model=UserDevice,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value
