"""Payment Status Lookup Repository.

Data access for the PaymentStatusLk model (payment/refund statuses: e.g.
pending, succeeded, failed, refunded). IRepository wrapper; use for retrieve
by id or code, list all. Used by PaymentTransaction and PaymentRefund.

Usage:
    >>> from fastx_database.persistence.repositories.payment_status_lk import PaymentStatusLkRepository
    >>> repo = PaymentStatusLkRepository(session=db_session)
"""

from sqlalchemy.orm import Session

from fastx_database.persistence.repositories.abstraction import IRepository
from fastx_database.persistence.models.payment_status_lk import PaymentStatusLk


class PaymentStatusLkRepository(IRepository):
    """Repository for PaymentStatusLk (payment/refund status) records.

    Provides session and IRepository base. Use for resolving status_id in
    payment and refund flows.
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
            model=PaymentStatusLk,
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
        """Return all payment status lookup entries ordered by code."""
        return self.session.query(PaymentStatusLk).order_by(PaymentStatusLk.code).all()
