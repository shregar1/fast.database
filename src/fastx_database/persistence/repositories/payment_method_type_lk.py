"""Payment Method Type Lookup Repository.

Data access for the PaymentMethodTypeLk model (payment method types: e.g.
card, upi, wallet). IRepository wrapper; use for retrieve by id or code,
list all. Used by PaymentTransaction and UserPaymentMethod.

Usage:
    >>> from fastx_database.persistence.repositories.payment_method_type_lk import PaymentMethodTypeLkRepository
    >>> repo = PaymentMethodTypeLkRepository(session=db_session)
"""

from sqlalchemy.orm import Session

from fastx_database.persistence.repositories.abstraction import IRepository
from fastx_database.persistence.models.payment_method_type_lk import PaymentMethodTypeLk


class PaymentMethodTypeLkRepository(IRepository):
    """Repository for PaymentMethodTypeLk (payment method type) records.

    Provides session and IRepository base. Use for resolving
    payment_method_type_id in payment and saved-method flows.
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
            model=PaymentMethodTypeLk,
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
        """Return all payment method type lookup entries ordered by code."""
        return (
            self.session.query(PaymentMethodTypeLk)
            .order_by(PaymentMethodTypeLk.code)
            .all()
        )
