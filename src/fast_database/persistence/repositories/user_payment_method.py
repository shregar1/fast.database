"""
User Payment Method Repository.

Data access for the UserPaymentMethod model (saved payment methods: card
last4, brand, expiry, is_default). IRepository wrapper; use for list by user,
create, update, set default, soft delete. Used by checkout and payment-method
APIs.

Usage:
    >>> from fast_database.persistence.repositories.user_payment_method import UserPaymentMethodRepository
    >>> repo = UserPaymentMethodRepository(session=db_session)
"""



from sqlalchemy.orm import Session

from fast_database.persistence.repositories.abstraction import IRepository
from fast_database.persistence.models.user_payment_method import UserPaymentMethod


class UserPaymentMethodRepository(IRepository):
    """
    Repository for UserPaymentMethod (saved payment method) records.

    Provides session and IRepository base for UserPaymentMethod. Use for
    listing methods per user/provider, adding/updating/deleting in services.
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
            model=UserPaymentMethod,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value
