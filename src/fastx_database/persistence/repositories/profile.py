"""Profile Repository.

Data access layer for the Profile model (extended user profile: name, bio,
education, location, verification, etc.). Provides retrieve by user_id,
create_for_user, and update_for_user. Uses IRepository base; session is optional
at init but required for all operations.

Usage:
    >>> from fastx_database.persistence.repositories.profile import ProfileRepository
    >>> repo = ProfileRepository(session=db_session)
    >>> profile = repo.retrieve_by_user_id(user_id=1)
    >>> profile = repo.create_for_user(user_id=1, data={"first_name": "Jane", ...})
"""

from sqlalchemy.orm import Session

from fastx_database.persistence.repositories.abstraction import IRepository
from fastx_database.persistence.models.profile import Profile


class ProfileRepository(IRepository):
    """Repository for Profile (extended user profile) database operations.

    One profile per user. Supports fetch by user_id, create for a new user, and
    update (upsert-style: update existing or create if missing). All mutations
    commit and refresh the profile instance.

    Methods:
        retrieve_by_user_id: Get profile by user_id (one_or_none).
        create_for_user: Create a new profile for user_id with given data.
        update_for_user: Update existing profile or create if none; returns profile.

    """

    def __init__(
        self,
        session: Session | None = None,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
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
            model=Profile,
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
    def session(self, value: Session) -> None:
        """Execute session operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._session = value

    def retrieve_by_user_id(self, user_id: int) -> Profile | None:
        """Execute retrieve_by_user_id operation.

        Args:
            user_id: The user_id parameter.

        Returns:
            The result of the operation.
        """
        self.logger.debug(f"Retrieving profile by user_id={user_id}")

        return (
            self.session.query(Profile).filter(Profile.user_id == user_id).one_or_none()
        )

    def create_for_user(
        self,
        user_id: int,
        data: dict,
    ) -> Profile:
        """Execute create_for_user operation.

        Args:
            user_id: The user_id parameter.
            data: The data parameter.

        Returns:
            The result of the operation.
        """
        self.logger.debug(f"Creating profile for user_id={user_id}")
        profile = Profile(user_id=user_id, **data)
        self.session.add(profile)
        self.session.commit()
        self.session.refresh(profile)

        return profile

    def update_for_user(
        self,
        user_id: int,
        data: dict,
    ) -> Profile:
        """Execute update_for_user operation.

        Args:
            user_id: The user_id parameter.
            data: The data parameter.

        Returns:
            The result of the operation.
        """
        self.logger.debug(f"Updating profile for user_id={user_id}")
        profile = self.retrieve_by_user_id(user_id)
        if profile is None:
            profile = Profile(user_id=user_id, **data)
            self.session.add(profile)
        else:
            for key, value in data.items():
                setattr(profile, key, value)
        self.session.commit()

        self.session.refresh(profile)

        return profile
