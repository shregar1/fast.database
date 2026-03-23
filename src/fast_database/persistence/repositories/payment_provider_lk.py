"""
Payment Provider Lookup Repository.

Data access for the PaymentProviderLk model (payment providers: e.g. Stripe,
Razorpay). IRepository wrapper; use for retrieve by id or code, list active.
Used by PaymentTransaction, UserPaymentMethod, Invoice.

Usage:
    >>> from fast_database.persistence.repositories.payment_provider_lk import PaymentProviderLkRepository
    >>> repo = PaymentProviderLkRepository(session=db_session)
"""



from sqlalchemy.orm import Session

from fast_database.persistence.repositories.abstraction import IRepository
from fast_database.persistence.models.payment_provider_lk import PaymentProviderLk


class PaymentProviderLkRepository(IRepository):
    """
    Repository for PaymentProviderLk (payment provider) records.

    Provides session and IRepository base. Use for resolving provider_id and
    listing active providers for checkout/integrations.
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
            model=PaymentProviderLk,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value

    def list_all(self):
        """Return all payment provider lookup entries ordered by code."""

        return (
            self.session.query(PaymentProviderLk)
            .order_by(PaymentProviderLk.code)
            .all()
        )
