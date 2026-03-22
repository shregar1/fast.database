"""
Payment Refund Repository.

Data access for the PaymentRefund model (refund against a payment transaction).
IRepository wrapper with session and model; use inherited or service methods
for create, retrieve by id/transaction_id, and list. Used by refund and
webhook handlers.

Usage:
    >>> from fast_database.repositories.payment_refund import PaymentRefundRepository
    >>> repo = PaymentRefundRepository(session=db_session)
"""



from sqlalchemy.orm import Session

from fast_database.repositories.abstraction import IRepository
from fast_database.models.payment_refund import PaymentRefund


class PaymentRefundRepository(IRepository):
    """
    Repository for PaymentRefund records.

    Provides session and IRepository base for PaymentRefund. Use
    retrieve_record_by_id, create_record, update_record, or custom filters
    (e.g. by payment_transaction_id) in services.
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
            model=PaymentRefund,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value
