"""
User Profile Photo Repository.

Data access for the UserProfilePhoto model (profile photo URL, order_sequence,
is_deleted). IRepository wrapper; use for create, retrieve by id/user_id,
update, and list by user. Used by profile and avatar APIs.

Usage:
    >>> from fast_repositories.user_profile_photo import UserProfilePhotoRepository
    >>> repo = UserProfilePhotoRepository(session=db_session)
"""



from sqlalchemy.orm import Session

from fast_repositories.repository import IRepository
from fast_database.models.user_profile_photo import UserProfilePhoto


class UserProfilePhotoRepository(IRepository):
    """
    Repository for UserProfilePhoto records.

    Provides session and IRepository base for UserProfilePhoto. Use for
    managing profile photos: create, retrieve by user, set primary, reorder,
    soft delete in services.
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
            model=UserProfilePhoto,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value
