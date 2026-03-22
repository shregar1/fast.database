"""
Payment Transaction Repository.

Data access for the PaymentTransaction model (single charge: amount, status,
provider ids, paid_at/refunded_at). IRepository wrapper with session and model;
use inherited or service methods for create, retrieve by id/provider_payment_id,
and list by user. Used by checkout and webhook handlers.

Usage:
    >>> from fast_database.repositories.payment_transaction import PaymentTransactionRepository
    >>> repo = PaymentTransactionRepository(session=db_session)
"""



from datetime import datetime

from sqlalchemy.orm import Session

from fast_database.repositories.abstraction import IRepository
from fast_database.models.payment_transaction import PaymentTransaction


class PaymentTransactionRepository(IRepository):
    """
    Repository for PaymentTransaction (charge) records.

    Provides session and IRepository base for PaymentTransaction. Use
    retrieve_record_by_id, create_record, update_record, list_by_user,
    or custom filters (e.g. by user_id, provider_payment_id) in services.
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
            model=PaymentTransaction,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value

    def list_by_user(
        self,
        user_id: int,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[PaymentTransaction], int]:
        query = self.session.query(PaymentTransaction).filter(PaymentTransaction.user_id == user_id)
        if from_date is not None:
            query = query.filter(PaymentTransaction.created_at >= from_date)
        if to_date is not None:
            query = query.filter(PaymentTransaction.created_at <= to_date)
        total = query.count()
        items = query.order_by(PaymentTransaction.created_at.desc()).offset(skip).limit(limit).all()
        return list(items), total
