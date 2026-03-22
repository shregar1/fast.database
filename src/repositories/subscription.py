"""
Subscription Repository.

Data access layer for the Subscription model (subscription lifecycle: status,
start_date, grace period, etc.). Create, retrieve by id/urn, update, soft
delete, list with active_only, count, retrieve_latest_active_by_user_id, and
retrieve_effective_subscription_by_user_id (ACTIVE/trialing/past_due in grace).
Used by entitlements and plan rate limit. Extends
:class:`~fast_database.repositories.repository.IRepository` with ``model=Subscription``.

Usage:
    >>> from fast_database.repositories.subscription import SubscriptionRepository
    >>> repo = SubscriptionRepository(session=db_session)
    >>> sub = repo.retrieve_effective_subscription_by_user_id(user_id=1)
"""



from sqlalchemy import func
from loguru import logger
from sqlalchemy.orm import Session

from fast_database.repositories.abstraction import IRepository
from fast_database.models.subscription import Subscription


class SubscriptionRepository(IRepository):
    """
    Repository for Subscription (subscription lifecycle) database operations.

    Supports create_record, retrieve_record_by_id, retrieve_record_by_urn,
    update_record, delete_record (soft), retrieve_all_records, count_records,
    retrieve_latest_active_by_user_id, and retrieve_effective_subscription_by_user_id
    (for entitlements: ACTIVE, trialing, or past_due within grace period).
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
            model=Subscription,
            cache=None,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session) -> None:
        self._session = value

    def create_record(self, record: Subscription) -> Subscription:
        self.logger.debug(f"Creating subscription: user_id={record.user_id}")
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        self.logger.info(f"Created subscription with ID: {record.id}")

        return record

    def retrieve_record_by_id(self, record_id: int) -> Subscription | None:
        self.logger.debug(f"Retrieving subscription by ID: {record_id}")

        return (
            self.session.query(Subscription)
            .filter(Subscription.id == record_id)
            .filter(Subscription.is_deleted.is_(False))
            .first()
        )

    def retrieve_record_by_urn(self, urn: str) -> Subscription | None:
        self.logger.debug(f"Retrieving subscription by URN: {urn}")

        return (
            self.session.query(Subscription)
            .filter(Subscription.urn == urn)
            .filter(Subscription.is_deleted.is_(False))
            .first()
        )

    def retrieve_all_records(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> list[Subscription]:
        self.logger.debug(
            f"Retrieving subscriptions: skip={skip}, limit={limit}, active_only={active_only}"
        )
        query = self.session.query(Subscription).filter(
            Subscription.is_deleted.is_(False)
        )
        if active_only:
            query = query.filter(Subscription.status == "ACTIVE")

        return query.offset(skip).limit(limit).all()

    def list_for_metered_billing(self, limit: int = 5000) -> list[Subscription]:
        """
        List subscriptions eligible for metered usage sync: ACTIVE or trialing.
        Used by usage sync cron to report usage to Stripe.
        """
        return (
            self.session.query(Subscription)
            .filter(Subscription.is_deleted.is_(False))
            .filter(Subscription.status.in_(["ACTIVE", "trialing"]))
            .limit(limit)
            .all()
        )

    def list_user_ids_with_effective_subscription(
        self, limit: int = 10000
    ) -> list[int]:
        """
        Return distinct user_id values that have an effective subscription
        (ACTIVE, trialing, or past_due within grace). Used by nightly low-credits
        notification job to find users with a session limit.
        """
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        rows = (
            self.session.query(Subscription.user_id)
            .filter(Subscription.is_deleted.is_(False))
            .filter(
                (Subscription.status.in_(["ACTIVE", "trialing"]))
                | (
                    (Subscription.status == "past_due")
                    & (Subscription.grace_period_ends_at.isnot(None))
                    & (Subscription.grace_period_ends_at > now)
                )
            )
            .distinct()
            .limit(limit)
            .all()
        )
        return [r[0] for r in rows]

    def update_record(self, record: Subscription) -> Subscription:
        self.logger.debug(f"Updating subscription: {record.id}")
        self.session.commit()
        self.session.refresh(record)
        self.logger.info(f"Updated subscription: {record.id}")

        return record

    def delete_record(self, record_id: int, deleted_by: int) -> bool:
        self.logger.debug(f"Soft deleting subscription: {record_id}")
        record = self.retrieve_record_by_id(record_id)
        if not record:

            return False
        record.is_deleted = True

        record.updated_by = deleted_by
        self.session.commit()
        self.logger.info(f"Soft deleted subscription: {record_id}")

        return True

    def count_records(self, active_only: bool = True) -> int:
        query = self.session.query(Subscription).filter(
            Subscription.is_deleted.is_(False)
        )
        if active_only:
            query = query.filter(Subscription.status == "ACTIVE")

        return query.count()

    def count_distinct_users_active(self) -> int:
        """Count distinct user_id with at least one active, non-deleted subscription."""
        return (
            self.session.query(func.count(func.distinct(Subscription.user_id)))
            .filter(Subscription.is_deleted.is_(False))
            .filter(Subscription.status == "ACTIVE")
            .scalar()
            or 0
        )

    def count_by_plan(self, active_only: bool = True) -> dict[str, int]:
        """Return counts per plan_code, e.g. {'free': 10, 'pro': 5}."""
        query = (
            self.session.query(Subscription.plan_code, func.count(Subscription.id))
            .filter(Subscription.is_deleted.is_(False))
        )
        if active_only:
            query = query.filter(Subscription.status == "ACTIVE")
        query = query.group_by(Subscription.plan_code)
        rows = query.all()
        return {str(row[0]): int(row[1]) for row in rows}

    def retrieve_latest_active_by_user_id(
        self, user_id: int
    ) -> Subscription | None:
        """
        Retrieve the most recent active subscription for a given user.
        """


        self.logger.debug(
            f"Retrieving latest active subscription for user_id={user_id}"
        )

        return (
            self.session.query(Subscription)
            .filter(Subscription.user_id == user_id)
            .filter(Subscription.is_deleted.is_(False))
            .filter(Subscription.status == "ACTIVE")
            .order_by(Subscription.start_date.desc())
            .first()
        )

    def retrieve_effective_subscription_by_user_id(
        self, user_id: int
    ) -> Subscription | None:
        """
        Retrieve the most recent subscription that grants access: ACTIVE, trialing,
        or past_due within grace period (grace_period_ends_at > now).
        Used for entitlements (trial + grace).
        """


        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        return (
            self.session.query(Subscription)
            .filter(Subscription.user_id == user_id)
            .filter(Subscription.is_deleted.is_(False))
            .filter(
                (Subscription.status.in_(["ACTIVE", "trialing"]))
                | (
                    (Subscription.status == "past_due")
                    & (Subscription.grace_period_ends_at.isnot(None))
                    & (Subscription.grace_period_ends_at > now)
                )
            )
            .order_by(Subscription.start_date.desc())
            .first()
        )

    def list_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> tuple[list[Subscription], int]:
        """List subscriptions for a user (admin/support). Returns (items, total)."""

        query = self.session.query(Subscription).filter(Subscription.user_id == user_id)
        if not include_deleted:
            query = query.filter(Subscription.is_deleted.is_(False))
        total = query.count()

        items = (
            query.order_by(Subscription.start_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return items, total

