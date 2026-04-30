"""Invoice Repository.

Data access for the Invoice model (billing invoices from payment providers).
Create, retrieve by id, retrieve by provider_id and external_id (idempotency),
list by user with optional filters (user_subscription_id, status_id, date
range), and update_record. Uses IRepository base.

Usage:
    >>> from fastx_database.persistence.repositories.invoice import InvoiceRepository
    >>> repo = InvoiceRepository(session=db_session)
    >>> inv = repo.retrieve_by_provider_and_external_id(provider_id=1, external_id="in_123")
    >>> items, total = repo.list_by_user(user_id=1, status_id=2, skip=0, limit=20)
"""

from datetime import datetime

from sqlalchemy.orm import Session

from fastx_database.persistence.repositories.abstraction import IRepository
from fastx_database.persistence.models.invoice import Invoice
from fastx_database.persistence.models.payment_provider_lk import PaymentProviderLk


class InvoiceRepository(IRepository):
    """Repository for Invoice (billing) create, lookup, and list.

    Supports create_record, retrieve_record_by_id, retrieve_by_provider_and_external_id
    for provider reconciliation, list_by_user with filters and pagination, and
    update_record. Used by webhooks and billing APIs.

    Methods:
        create_record, retrieve_record_by_id, update_record: Standard CRUD.
        retrieve_by_provider_and_external_id: Find by provider and external id.
        list_by_user: Paginated list with user_subscription_id, status_id, from_date, to_date.

    """

    def __init__(
        self,
        session: Session | None = None,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
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
            model=Invoice,
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
    def session(self, value: Session) -> None:
        """Execute session operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._session = value

    def create_record(self, record: Invoice) -> Invoice:
        """Execute create_record operation.

        Args:
            record: The record parameter.

        Returns:
            The result of the operation.
        """
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)

        return record

    def retrieve_record_by_id(self, record_id: int) -> Invoice | None:
        """Execute retrieve_record_by_id operation.

        Args:
            record_id: The record_id parameter.

        Returns:
            The result of the operation.
        """
        return self.session.query(Invoice).filter(Invoice.id == record_id).first()

    def retrieve_by_provider_and_external_id(
        self, provider_id: int, external_id: str
    ) -> Invoice | None:
        """Execute retrieve_by_provider_and_external_id operation.

        Args:
            provider_id: The provider_id parameter.
            external_id: The external_id parameter.

        Returns:
            The result of the operation.
        """
        return (
            self.session.query(Invoice)
            .filter(
                Invoice.provider_id == provider_id,
                Invoice.external_id == external_id,
            )
            .first()
        )

    def retrieve_by_external_id(
        self, provider: str, external_id: str
    ) -> Invoice | None:
        """Find invoice by provider code (e.g. 'stripe') and external_id.
        Used by Stripe webhook sync for idempotent upserts.
        """
        row = (
            self.session.query(PaymentProviderLk)
            .filter(PaymentProviderLk.code == provider)
            .first()
        )
        if not row:
            return None
        return self.retrieve_by_provider_and_external_id(
            provider_id=row.id, external_id=external_id
        )

    def list_by_user(
        self,
        user_id: int,
        user_subscription_id: int | None = None,
        status_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Invoice], int]:
        """Execute list_by_user operation.

        Args:
            user_id: The user_id parameter.
            user_subscription_id: The user_subscription_id parameter.
            status_id: The status_id parameter.
            from_date: The from_date parameter.
            to_date: The to_date parameter.
            skip: The skip parameter.
            limit: The limit parameter.

        Returns:
            The result of the operation.
        """
        query = self.session.query(Invoice).filter(Invoice.user_id == user_id)
        if user_subscription_id is not None:
            query = query.filter(Invoice.user_subscription_id == user_subscription_id)
        if status_id is not None:
            query = query.filter(Invoice.status_id == status_id)
        if from_date is not None:
            query = query.filter(Invoice.created_at >= from_date)
        if to_date is not None:
            query = query.filter(Invoice.created_at <= to_date)
        total = query.count()

        items = (
            query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()
        )

        return list(items), total

    def update_record(self, record: Invoice) -> Invoice:
        """Execute update_record operation.

        Args:
            record: The record parameter.

        Returns:
            The result of the operation.
        """
        self.session.commit()
        self.session.refresh(record)

        return record
