"""
Payment Method Type Lookup Repository.

Data access for the PaymentMethodTypeLk model (payment method types: e.g.
card, upi, wallet). IRepository wrapper; use for retrieve by id or code,
list all. Used by PaymentTransaction and UserPaymentMethod.

Usage:
    >>> from fast_database.persistence.repositories.payment_method_type_lk import PaymentMethodTypeLkRepository
    >>> repo = PaymentMethodTypeLkRepository(session=db_session)
"""



from sqlalchemy.orm import Session

from fast_database.persistence.repositories.abstraction import IRepository
from fast_database.persistence.models.payment_method_type_lk import PaymentMethodTypeLk


class PaymentMethodTypeLkRepository(IRepository):
    """
    Repository for PaymentMethodTypeLk (payment method type) records.

    Provides session and IRepository base. Use for resolving
    payment_method_type_id in payment and saved-method flows.
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
            model=PaymentMethodTypeLk,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value

    def list_all(self):
        """Return all payment method type lookup entries ordered by code."""

        return (
            self.session.query(PaymentMethodTypeLk)
            .order_by(PaymentMethodTypeLk.code)
            .all()
        )
