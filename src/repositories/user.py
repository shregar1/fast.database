"""
User Repository.

Data access layer for the User model. Provides query and list operations for
user accounts: by email, email+password, by ID and login status, and paginated
admin listing with optional email search and soft-delete handling. Requires a
SQLAlchemy session; supports IRepository base (urn, user_urn, api_name, user_id).

Usage:
    >>> from fast_repositories.user import UserRepository
    >>> repo = UserRepository(session=db_session, urn="req-1", user_id=1)
    >>> user = repo.retrieve_record_by_email("user@example.com")
    >>> user = repo.retrieve_record_by_id_and_is_logged_in(1, is_logged_in=True)
"""


from datetime import datetime

from sqlalchemy.orm import Session

from fast_repositories.repository import IRepository
from fast_database.models.user import User


class UserRepository(IRepository):
    """
    Repository for User (account) data access and queries.

    Wraps the User model with methods for authentication (email/password, id +
    is_logged_in), lookup by email, and admin listing with pagination and
    optional email filter. Session is required; raises RuntimeError if not set.

    Attributes:
        session: SQLAlchemy Session for database operations.
        urn, user_urn, api_name, user_id: Request context (from IRepository).

    Methods:
        retrieve_record_by_email: Find user by email (optional is_deleted).
        retrieve_record_by_email_and_password: Find by email and hashed password.
        retrieve_record_by_id_and_is_logged_in: Find by id and is_logged_in (list).
        retrieve_record_by_id_is_logged_in: Same as above, single record (one_or_none).
        list_users: Paginated list with optional email_contains and include_deleted.
    """



    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        session: Session = None,
        user_id: str = None,
    ):
        self._cache = None
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            cache=self._cache,
            model=User,
        )
        self._urn = urn
        self._user_urn = user_urn
        self._api_name = api_name
        self._session = session
        self._user_id = user_id
        if not self._session:
            raise RuntimeError("DB session not found")
        self.logger.debug(
            f"UserRepository initialized for user_id={user_id}, "
            f"urn={urn}, api_name={api_name}"
        )

    @property
    def urn(self):

        return self._urn

    @urn.setter
    def urn(self, value):
        self._urn = value

    @property
    def user_urn(self):

        return self._user_urn

    @user_urn.setter
    def user_urn(self, value):
        self._user_urn = value

    @property
    def api_name(self):

        return self._api_name

    @api_name.setter
    def api_name(self, value):
        self._api_name = value

    @property
    def session(self):

        return self._session

    @session.setter
    def session(self, value):
        if not isinstance(value, Session):
            raise ValueError("session must be a SQLAlchemy Session instance")
        self._session = value

    @property
    def user_id(self):

        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    def retrieve_record_by_email_and_password(
        self,
        email: str,
        password: str,
        is_deleted: bool = False,
    ) -> User:
        """
        Retrieve a user by email and password.
        Args:
            email (str): User's email address.
            password (str): User's password (hashed).
            is_deleted (bool): Whether to include deleted users.
        Returns:
            User: The user record if found, else None.
        """


        self.logger.info(f"Retrieving user by email: {email}")
        start_time = datetime.now()
        record = (
            self.session.query(self.model)
            .filter(
                self.model.email == email,
                self.model.password == password,
                self.model.is_deleted == is_deleted,
            )
            .first()
        )
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return record if record else None

    def retrieve_record_by_email(
        self,
        email: str,
        is_deleted: bool = False,
    ) -> User:
        """
        Retrieve a user by email.
        Args:
            email (str): User's email address.
            is_deleted (bool): Whether to include deleted users.
        Returns:
            User: The user record if found, else None.
        """


        self.logger.info(f"Retrieving user by email: {email}")
        start_time = datetime.now()
        record = (
            self.session.query(self.model)
            .filter(
                self.model.email == email,
                self.model.is_deleted == is_deleted,
            )
            .first()
        )
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return record if record else None

    def retrieve_record_by_phone(
        self,
        phone: str,
        is_deleted: bool = False,
    ) -> User:
        """
        Retrieve a user by phone number.
        """
        if not phone or not str(phone).strip():
            return None
        normalized = str(phone).strip()
        record = (
            self.session.query(self.model)
            .filter(
                self.model.phone == normalized,
                self.model.is_deleted == is_deleted,
            )
            .first()
        )
        return record if record else None

    def retrieve_record_by_id_and_is_logged_in(
        self,
        id: str,
        is_logged_in: bool,
        is_deleted: bool = False,
    ) -> User:
        """
        Retrieve users by ID and login status.
        Args:
            id (str): User's ID.
            is_logged_in (bool): Login status to filter by.
            is_deleted (bool): Whether to include deleted users.
        Returns:
            list[User]: List of user records matching the criteria.
        """


        self.logger.info(
            f"Retrieving user by id: {id}, is_logged_in: {is_logged_in}"
        )
        start_time = datetime.now()
        records = (
            self.session.query(self.model)
            .filter(
                self.model.id == id,
                self.model.is_logged_in == is_logged_in,
                self.model.is_deleted == is_deleted,
            )
            .all()
        )
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return records

    def retrieve_record_by_id_is_logged_in(
        self,
        id: int,
        is_logged_in: bool,
        is_deleted: bool = False,
    ) -> User:
        """
        Retrieve a user by ID and login status (single record).
        Args:
            id (int): User's ID.
            is_logged_in (bool): Login status to filter by.
            is_deleted (bool): Whether to include deleted users.
        Returns:
            User: The user record if found, else None.
        """


        self.logger.info(
            f"Retrieving user by id: {id}, is_logged_in: {is_logged_in}"
        )
        start_time = datetime.now()
        record = (
            self.session.query(self.model)
            .filter(
                self.model.id == id,
                self.model.is_logged_in == is_logged_in,
                self.model.is_deleted == is_deleted,
            )
            .one_or_none()
        )
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return record

    def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        email_contains: str | None = None,
        include_deleted: bool = False,
    ) -> tuple[list, int]:
        """List users for admin. Returns (items, total)."""

        query = self.session.query(self.model)
        if not include_deleted:
            query = query.filter(self.model.is_deleted.is_(False))
        if email_contains and email_contains.strip():
            pattern = f"%{email_contains.strip()}%"
            query = query.filter(self.model.email.ilike(pattern))
        total = query.count()

        items = (
            query.order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return items, total

    def count_users(self, include_deleted: bool = False) -> int:
        """Total user count. Excludes deleted by default."""
        query = self.session.query(self.model)
        if not include_deleted:
            query = query.filter(self.model.is_deleted.is_(False))
        return query.count()
