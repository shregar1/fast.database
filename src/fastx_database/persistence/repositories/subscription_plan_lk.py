"""Subscription Plan Lookup Repository.

Data access for the SubscriptionPlanLk model (plan definitions: name,
number_sessions, price_usd, features). IRepository wrapper; use for retrieve
by id or name, list all. Used by subscription and checkout flows.

Usage:
    >>> from fastx_database.persistence.repositories.subscription_plan_lk import SubscriptionPlanLkRepository
    >>> repo = SubscriptionPlanLkRepository(session=db_session)
"""

from sqlalchemy.orm import Session

from fastx_database.persistence.repositories.abstraction import IRepository
from fastx_database.persistence.models.subscription_plan_lk import SubscriptionPlanLk


class SubscriptionPlanLkRepository(IRepository):
    """Repository for SubscriptionPlanLk (plan definition) records.

    Provides session and IRepository base. Use for listing plans for UI and
    resolving plan_id by name or id in subscription creation.
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
            model=SubscriptionPlanLk,
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

    def list_all(self) -> list[SubscriptionPlanLk]:
        """Return all subscription plans ordered by name (catalog for pricing/checkout)."""
        return (
            self.session.query(SubscriptionPlanLk)
            .order_by(SubscriptionPlanLk.name)
            .all()
        )
