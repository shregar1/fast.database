"""
Crowdfunding domain models (campaigns, reward tiers, pledges).

Maps creator campaigns with funding goals, discrete reward tiers, and backer pledges.
Amounts are stored in **minor units** (e.g. cents) with an ISO currency code.

Usage:
    >>> from fast_database.persistence.models.crowdfunding import (
    ...     CrowdfundingCampaign,
    ...     CrowdfundingPledge,
    ...     CrowdfundingReward,
    ... )
"""

from __future__ import annotations

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from fast_database.core.constants.table import Table
from fast_database.core.mixins import SoftDeleteMixin, TimestampMixin
from fast_database.persistence.models import Base


class CrowdfundingCampaign(Base, TimestampMixin, SoftDeleteMixin):
    """
    A funding campaign owned by a creator (user).

    ``funded_amount_cents`` is typically maintained by application logic when pledges
    are captured or cancelled.
    """

    __tablename__ = Table.CROWDFUNDING_CAMPAIGN
    __table_args__ = (
        UniqueConstraint(
            "creator_user_id",
            "slug",
            name="uq_crowdfunding_campaign_creator_slug",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    creator_user_id = Column(
        BigInteger,
        ForeignKey(f"{Table.USER}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id = Column(
        BigInteger,
        ForeignKey(f"{Table.ORGANIZATION}.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title = Column(String(512), nullable=False)
    slug = Column(String(256), nullable=False, index=True)
    short_description = Column(String(1024), nullable=True)
    body = Column(Text, nullable=True)
    goal_amount_cents = Column(BigInteger, nullable=False)
    funded_amount_cents = Column(BigInteger, nullable=False, default=0)
    currency = Column(String(8), nullable=False, default="USD")
    status = Column(
        String(32),
        nullable=False,
        default="draft",
        index=True,
    )
    starts_at = Column(DateTime(timezone=True), nullable=True)
    ends_at = Column(DateTime(timezone=True), nullable=True, index=True)
    category = Column(String(128), nullable=True, index=True)
    campaign_metadata = Column("metadata", JSONB, nullable=True)

    def to_summary_dict(self) -> dict:
        return {
            "urn": self.urn,
            "title": self.title,
            "slug": self.slug,
            "goalAmountCents": self.goal_amount_cents,
            "fundedAmountCents": self.funded_amount_cents,
            "currency": self.currency,
            "status": self.status,
        }


class CrowdfundingReward(Base, TimestampMixin, SoftDeleteMixin):
    """A reward tier: minimum pledge amount and optional backer cap."""

    __tablename__ = Table.CROWDFUNDING_REWARD

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    campaign_id = Column(
        BigInteger,
        ForeignKey(f"{Table.CROWDFUNDING_CAMPAIGN}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    amount_cents = Column(BigInteger, nullable=False)
    delivery_estimate = Column(String(512), nullable=True)
    max_backers = Column(Integer, nullable=True)
    backers_count = Column(Integer, nullable=False, default=0)
    sort_order = Column(Integer, nullable=False, default=0)
    reward_metadata = Column("metadata", JSONB, nullable=True)


class CrowdfundingPledge(Base, TimestampMixin):
    """A backer's commitment; pair with payment provider state via ``status``."""

    __tablename__ = Table.CROWDFUNDING_PLEDGE

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    campaign_id = Column(
        BigInteger,
        ForeignKey(f"{Table.CROWDFUNDING_CAMPAIGN}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reward_id = Column(
        BigInteger,
        ForeignKey(f"{Table.CROWDFUNDING_REWARD}.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    backer_user_id = Column(
        BigInteger,
        ForeignKey(f"{Table.USER}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount_cents = Column(BigInteger, nullable=False)
    currency = Column(String(8), nullable=False, default="USD")
    status = Column(String(32), nullable=False, default="pending", index=True)
    payment_provider_ref = Column(String(256), nullable=True, index=True)
    idempotency_key = Column(String(128), nullable=True, unique=True)
