"""
Webhook and WebhookDelivery Repositories.

Data access for Webhook (endpoint URL, secret, enabled) and WebhookDelivery
(delivery attempts and payloads). WebhookRepository: create, retrieve by id,
retrieve_records (user_id, enabled_only, pagination). WebhookDeliveryRepository:
create delivery, list by webhook_id, update status. Used by webhook management
and outbound delivery workers.

Usage:
    >>> from fast_repositories.webhook import WebhookRepository
    >>> repo = WebhookRepository(session=db_session)
    >>> webhooks, total = repo.retrieve_records(user_id=1, enabled_only=True)
"""



from sqlalchemy import func, nulls_last
from sqlalchemy.orm import Session

from fast_repositories.repository import IRepository
from fast_database.models.webhook import Webhook, WebhookDelivery


class WebhookRepository(IRepository):
    """
    Repository for Webhook (webhook endpoint) records.

    Create, retrieve by id, and retrieve_records with user_id and enabled_only
    filters and pagination. Used by webhook list and create/update APIs.
    """



    def __init__(
        self,
        session: Session | None = None,
        *,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            model=Webhook,
            cache=None,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session) -> None:
        self._session = value

    def create_record(self, record: Webhook) -> Webhook:
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)

        return record

    def retrieve_record_by_id(self, record_id: int) -> Webhook | None:

        return self.session.query(Webhook).filter(Webhook.id == record_id).first()

    def retrieve_records(
        self,
        user_id: int | None = None,
        enabled_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Webhook], int]:
        query = self.session.query(Webhook)
        if user_id is not None:
            query = query.filter(Webhook.user_id == user_id)
        if enabled_only:
            query = query.filter(Webhook.enabled.is_(True))
        total = query.count()

        items = query.order_by(Webhook.created_at.desc()).offset(skip).limit(limit).all()

        return items, total

    def retrieve_by_event(self, event_type: str, user_id: int | None = None) -> list[Webhook]:
        """Return webhooks that subscribe to this event (and optionally for this user)."""

        query = self.session.query(Webhook).filter(
            Webhook.enabled.is_(True),
            Webhook.events.contains([event_type]),
        )
        if user_id is not None:
            query = query.filter((Webhook.user_id == user_id) | (Webhook.user_id.is_(None)))
        else:
            query = query.filter(Webhook.user_id.is_(None))

        return query.all()

    def update_record(self, record: Webhook) -> Webhook:
        self.session.commit()
        self.session.refresh(record)

        return record

    def count_by_enabled(self, user_id: int | None = None) -> dict:
        """Return {total, active, inactive} webhook counts."""
        query = self.session.query(Webhook)
        if user_id is not None:
            query = query.filter(Webhook.user_id == user_id)
        total = query.count()
        active = query.filter(Webhook.enabled.is_(True)).count()
        return {"total": total, "active": active, "inactive": total - active}

    def delete_record(self, record_id: int) -> bool:
        record = self.retrieve_record_by_id(record_id)
        if not record:

            return False
        self.session.delete(record)

        self.session.commit()

        return True


class WebhookDeliveryRepository(IRepository):
    """
    Repository for WebhookDelivery (delivery attempt) records.

    get_or_create: Find or create delivery for webhook_id + event_id (idempotent).
    update_attempt: Set status, response_code, error_message, increment attempts.
    Used by webhook delivery workers.
    """



    def __init__(
        self,
        session: Session | None = None,
        *,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            model=WebhookDelivery,
            cache=None,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session) -> None:
        self._session = value

    def get_or_create(self, webhook_id: int, event_id: str, event_type: str, payload: dict | None) -> tuple[WebhookDelivery, bool]:
        """Get existing delivery or create pending one. Returns (delivery, created)."""

        existing = (
            self.session.query(WebhookDelivery)
            .filter(
                WebhookDelivery.webhook_id == webhook_id,
                WebhookDelivery.event_id == event_id,
            )
            .first()
        )
        if existing:

            return existing, False
        delivery = WebhookDelivery(
            webhook_id=webhook_id,
            event_id=event_id,
            event_type=event_type,
            payload=payload,
            status="pending",
            attempts=0,
        )
        self.session.add(delivery)
        self.session.commit()
        self.session.refresh(delivery)

        return delivery, True

    def get_delivery_with_webhook(
        self,
        delivery_id: int,
        webhook_id: int | None = None,
    ) -> tuple[WebhookDelivery, Webhook] | None:
        """Return (delivery, webhook) for a delivery, optionally scoped to webhook_id. None if not found."""
        query = (
            self.session.query(WebhookDelivery, Webhook)
            .join(Webhook, Webhook.id == WebhookDelivery.webhook_id)
            .filter(WebhookDelivery.id == delivery_id)
        )
        if webhook_id is not None:
            query = query.filter(WebhookDelivery.webhook_id == webhook_id)
        row = query.first()
        if not row:
            return None
        return (row[0], row[1])

    def update_attempt(
        self,
        delivery_id: int,
        status: str,
        response_code: int | None = None,
        error_message: str | None = None,
    ) -> None:
        from datetime import datetime
        delivery = self.session.query(WebhookDelivery).filter(WebhookDelivery.id == delivery_id).first()
        if not delivery:

            return
        delivery.status = status

        delivery.attempts += 1
        delivery.last_attempt_at = datetime.utcnow()
        delivery.response_code = response_code
        delivery.error_message = error_message
        self.session.commit()

    def dashboard_stats(self, user_id: int | None = None) -> dict:
        """
        Aggregate delivery stats for the dashboard.
        Returns counts by status, by event_type, success rate, and total.
        """
        base = self.session.query(WebhookDelivery)
        if user_id is not None:
            base = (
                base.join(Webhook, Webhook.id == WebhookDelivery.webhook_id)
                .filter(Webhook.user_id == user_id)
            )

        total = base.count()

        status_rows = (
            self.session.query(WebhookDelivery.status, func.count(WebhookDelivery.id))
            .join(Webhook, Webhook.id == WebhookDelivery.webhook_id)
        )
        if user_id is not None:
            status_rows = status_rows.filter(Webhook.user_id == user_id)
        status_rows = status_rows.group_by(WebhookDelivery.status).all()
        by_status = {row[0]: row[1] for row in status_rows}

        event_rows = (
            self.session.query(WebhookDelivery.event_type, func.count(WebhookDelivery.id))
            .join(Webhook, Webhook.id == WebhookDelivery.webhook_id)
        )
        if user_id is not None:
            event_rows = event_rows.filter(Webhook.user_id == user_id)
        event_rows = event_rows.group_by(WebhookDelivery.event_type).all()
        by_event_type = {row[0]: row[1] for row in event_rows}

        sent = by_status.get("sent", 0)
        attempted = sent + by_status.get("failed", 0)
        success_rate = round(sent / attempted * 100, 1) if attempted > 0 else None

        return {
            "total_deliveries": total,
            "by_status": by_status,
            "by_event_type": by_event_type,
            "success_rate_percent": success_rate,
        }

    def list_recent(
        self,
        webhook_id: int | None = None,
        user_id: int | None = None,
        status: str | None = None,
        event_type: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """
        List recent delivery records (url, event, status, time, error) for support/debugging.
        Joins with Webhook to include url; optionally filter by webhook_id, user_id, status, event_type.
        """
        query = (
            self.session.query(WebhookDelivery, Webhook.url)
            .join(Webhook, Webhook.id == WebhookDelivery.webhook_id)
        )
        if webhook_id is not None:
            query = query.filter(WebhookDelivery.webhook_id == webhook_id)
        if user_id is not None:
            query = query.filter(Webhook.user_id == user_id)
        if status is not None:
            query = query.filter(WebhookDelivery.status == status)
        if event_type is not None:
            query = query.filter(WebhookDelivery.event_type == event_type)
        total = query.count()
        query = (
            query.order_by(
                nulls_last(WebhookDelivery.last_attempt_at.desc()),
                WebhookDelivery.id.desc(),
            )
            .offset(skip)
            .limit(limit)
        )
        rows = query.all()
        items = []
        for delivery, url in rows:
            last_at = getattr(delivery, "last_attempt_at", None)
            items.append({
                "id": delivery.id,
                "webhook_id": delivery.webhook_id,
                "url": url or "",
                "event_type": delivery.event_type,
                "event_id": delivery.event_id,
                "status": delivery.status,
                "response_code": getattr(delivery, "response_code", None),
                "last_attempt_at": last_at.isoformat() if last_at else None,
                "error_message": getattr(delivery, "error_message", None),
                "attempts": delivery.attempts,
            })
        return items, total
