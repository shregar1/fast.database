"""
User Subscription Repository.

Data access for the UserSubscription model (user–plan–period link, usage count,
payment_transaction_id). IRepository wrapper with session and model only;
extend or use service layer for retrieve_by_user, create, update. Used by
subscription and billing flows.

Usage:
    >>> from fast_repositories.user_subscription import UserSubscriptionRepository
    >>> repo = UserSubscriptionRepository(session=db_session, user_id=1)
"""



from sqlalchemy.orm import Session

from fast_repositories.repository import IRepository
from fast_database.models.user_subscription import UserSubscription


class UserSubscriptionRepository(IRepository):
    """
    Repository for UserSubscription (user–plan–billing period) records.

    Provides session and IRepository base (urn, user_urn, api_name, user_id,
    model=UserSubscription). Use inherited retrieve/create/update methods or
    service-level logic for listing and business rules.
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
            model=UserSubscription,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value
