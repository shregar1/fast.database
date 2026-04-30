"""Payment Refund Repository.

Data access for the PaymentRefund model (refund against a payment transaction).
IRepository wrapper with session and model; use inherited or service methods
for create, retrieve by id/transaction_id, and list. Used by refund and
webhook handlers.

Usage:
    >>> from fastx_database.persistence.repositories.payment_refund import PaymentRefundRepository
    >>> repo = PaymentRefundRepository(session=db_session)
"""

from sqlalchemy.orm import Session

from fastx_database.persistence.repositories.abstraction import IRepository
from fastx_database.persistence.models.payment_refund import PaymentRefund


class PaymentRefundRepository(IRepository):
    """Repository for PaymentRefund records.

    Provides session and IRepository base for PaymentRefund. Use
    retrieve_record_by_id, create_record, update_record, or custom filters
    (e.g. by payment_transaction_id) in services.
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
            model=PaymentRefund,
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
