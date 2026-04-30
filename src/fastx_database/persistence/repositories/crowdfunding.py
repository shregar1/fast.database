"""Repositories for crowdfunding campaigns, reward tiers, and pledges."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, nulls_last
from sqlalchemy.orm import Session

from fastx_database.core.soft_delete import filter_active
from fastx_database.persistence.models.crowdfunding import (
    CrowdfundingCampaign,
    CrowdfundingPledge,
    CrowdfundingReward,
)
from fastx_database.persistence.repositories.abstraction import IRepository


def _utc_now() -> datetime:
    """Execute _utc_now operation.

    Returns:
        The result of the operation.
    """
    return datetime.now(timezone.utc)


class CrowdfundingCampaignRepository(IRepository):
    """Data access for :class:`~fastx_database.persistence.models.crowdfunding.CrowdfundingCampaign`."""

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
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            cache=None,
            model=CrowdfundingCampaign,
        )
        self._session = session

    @property
    def session(self) -> Session | None:
        """Execute session operation.

        Returns:
            The result of the operation.
        """
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        """Execute session operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._session = value

    def _active_query(self):
        """Execute _active_query operation.

        Returns:
            The result of the operation.
        """
        q = self.session.query(CrowdfundingCampaign)
        return filter_active(q, CrowdfundingCampaign.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> CrowdfundingCampaign | None:
        """Execute retrieve_record_by_id operation.

        Args:
            record_id: The record_id parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(CrowdfundingCampaign.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> CrowdfundingCampaign | None:
        """Execute retrieve_record_by_urn operation.

        Args:
            urn: The urn parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(CrowdfundingCampaign.urn == urn).first()

    def find_by_creator_and_slug(
        self,
        creator_user_id: int,
        slug: str,
    ) -> CrowdfundingCampaign | None:
        """Execute find_by_creator_and_slug operation.

        Args:
            creator_user_id: The creator_user_id parameter.
            slug: The slug parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query()
            .filter(
                CrowdfundingCampaign.creator_user_id == creator_user_id,
                CrowdfundingCampaign.slug == slug,
            )
            .first()
        )

    def list_by_creator(
        self,
        creator_user_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CrowdfundingCampaign]:
        """Execute list_by_creator operation.

        Args:
            creator_user_id: The creator_user_id parameter.
            skip: The skip parameter.
            limit: The limit parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query()
            .filter(CrowdfundingCampaign.creator_user_id == creator_user_id)
            .order_by(CrowdfundingCampaign.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CrowdfundingCampaign]:
        """Execute list_by_status operation.

        Args:
            status: The status parameter.
            skip: The skip parameter.
            limit: The limit parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query()
            .filter(CrowdfundingCampaign.status == status)
            .order_by(nulls_last(CrowdfundingCampaign.ends_at.asc()))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_live_at(
        self,
        at: datetime | None = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CrowdfundingCampaign]:
        """Campaigns with ``status == live`` whose window contains ``at`` (UTC)."""
        when = at or _utc_now()
        q = self._active_query().filter(CrowdfundingCampaign.status == "live")
        q = q.filter(
            (
                CrowdfundingCampaign.starts_at.is_(None)
                | (CrowdfundingCampaign.starts_at <= when)
            )
        )
        q = q.filter(
            (
                CrowdfundingCampaign.ends_at.is_(None)
                | (CrowdfundingCampaign.ends_at >= when)
            )
        )
        return (
            q.order_by(nulls_last(CrowdfundingCampaign.ends_at.asc()))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_record(self, record: CrowdfundingCampaign) -> CrowdfundingCampaign:
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


class CrowdfundingRewardRepository(IRepository):
    """Data access for :class:`~fastx_database.persistence.models.crowdfunding.CrowdfundingReward`."""

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
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            cache=None,
            model=CrowdfundingReward,
        )
        self._session = session

    @property
    def session(self) -> Session | None:
        """Execute session operation.

        Returns:
            The result of the operation.
        """
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        """Execute session operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._session = value

    def _active_query(self):
        """Execute _active_query operation.

        Returns:
            The result of the operation.
        """
        q = self.session.query(CrowdfundingReward)
        return filter_active(q, CrowdfundingReward.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> CrowdfundingReward | None:
        """Execute retrieve_record_by_id operation.

        Args:
            record_id: The record_id parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(CrowdfundingReward.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> CrowdfundingReward | None:
        """Execute retrieve_record_by_urn operation.

        Args:
            urn: The urn parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(CrowdfundingReward.urn == urn).first()

    def list_by_campaign(
        self,
        campaign_id: int,
        *,
        include_deleted: bool = False,
    ) -> list[CrowdfundingReward]:
        """Execute list_by_campaign operation.

        Args:
            campaign_id: The campaign_id parameter.
            include_deleted: The include_deleted parameter.

        Returns:
            The result of the operation.
        """
        q = self.session.query(CrowdfundingReward).filter(
            CrowdfundingReward.campaign_id == campaign_id,
        )
        if not include_deleted:
            q = filter_active(q, CrowdfundingReward.is_deleted)
        return q.order_by(
            CrowdfundingReward.sort_order.asc(), CrowdfundingReward.id.asc()
        ).all()

    def create_record(self, record: CrowdfundingReward) -> CrowdfundingReward:
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


class CrowdfundingPledgeRepository(IRepository):
    """Data access for :class:`~fastx_database.persistence.models.crowdfunding.CrowdfundingPledge`."""

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
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            cache=None,
            model=CrowdfundingPledge,
        )
        self._session = session

    @property
    def session(self) -> Session | None:
        """Execute session operation.

        Returns:
            The result of the operation.
        """
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        """Execute session operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._session = value

    def retrieve_record_by_id(self, record_id: int) -> CrowdfundingPledge | None:
        """Execute retrieve_record_by_id operation.

        Args:
            record_id: The record_id parameter.

        Returns:
            The result of the operation.
        """
        return (
            self.session.query(CrowdfundingPledge)
            .filter(CrowdfundingPledge.id == record_id)
            .first()
        )

    def retrieve_record_by_urn(self, urn: str) -> CrowdfundingPledge | None:
        """Execute retrieve_record_by_urn operation.

        Args:
            urn: The urn parameter.

        Returns:
            The result of the operation.
        """
        return (
            self.session.query(CrowdfundingPledge)
            .filter(CrowdfundingPledge.urn == urn)
            .first()
        )

    def find_by_idempotency_key(self, key: str) -> CrowdfundingPledge | None:
        """Execute find_by_idempotency_key operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        if not key:
            return None
        return (
            self.session.query(CrowdfundingPledge)
            .filter(CrowdfundingPledge.idempotency_key == key)
            .first()
        )

    def list_by_campaign(
        self,
        campaign_id: int,
        *,
        skip: int = 0,
        limit: int = 500,
    ) -> list[CrowdfundingPledge]:
        """Execute list_by_campaign operation.

        Args:
            campaign_id: The campaign_id parameter.
            skip: The skip parameter.
            limit: The limit parameter.

        Returns:
            The result of the operation.
        """
        return (
            self.session.query(CrowdfundingPledge)
            .filter(CrowdfundingPledge.campaign_id == campaign_id)
            .order_by(CrowdfundingPledge.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_backer(
        self,
        backer_user_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CrowdfundingPledge]:
        """Execute list_by_backer operation.

        Args:
            backer_user_id: The backer_user_id parameter.
            skip: The skip parameter.
            limit: The limit parameter.

        Returns:
            The result of the operation.
        """
        return (
            self.session.query(CrowdfundingPledge)
            .filter(CrowdfundingPledge.backer_user_id == backer_user_id)
            .order_by(CrowdfundingPledge.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def sum_captured_amount_cents(self, campaign_id: int) -> int:
        """Execute sum_captured_amount_cents operation.

        Args:
            campaign_id: The campaign_id parameter.

        Returns:
            The result of the operation.
        """
        total = (
            self.session.query(
                func.coalesce(func.sum(CrowdfundingPledge.amount_cents), 0)
            )
            .filter(
                CrowdfundingPledge.campaign_id == campaign_id,
                CrowdfundingPledge.status == "captured",
            )
            .scalar()
        )
        return int(total or 0)

    def create_record(self, record: CrowdfundingPledge) -> CrowdfundingPledge:
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
