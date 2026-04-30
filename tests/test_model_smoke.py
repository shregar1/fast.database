"""Smoke tests for selected ORM models (no live DB required)."""

from fastx_database import Base
from fastx_database.core.constants.table import Table
from fastx_database.persistence.models.crowdfunding import CrowdfundingCampaign
from fastx_database.persistence.models.healthcare import HealthcareFacility
from fastx_database.persistence.models.industrial_iot import IndustrialFacility
from fastx_database.persistence.models.messaging_chat import Chat
from fastx_database.persistence.models.status_lk import StatusLk
from fastx_database.persistence.models.user import User


def test_user_tablename():
    """Execute test_user_tablename operation.

    Returns:
        The result of the operation.
    """
    assert User.__tablename__ == Table.USER


def test_status_lk_has_code_column():
    """Execute test_status_lk_has_code_column operation.

    Returns:
        The result of the operation.
    """
    assert any(c.name == "code" for c in StatusLk.__table__.columns)


def test_metadata_registers_core_tables():
    """Models use PostgreSQL types (e.g. JSONB); metadata still registers table names."""
    assert Table.USER in Base.metadata.tables
    assert "status_lk" in Base.metadata.tables
    assert len(Base.metadata.tables) > 20
    assert Table.CHAT in Base.metadata.tables
    assert Table.CROWDFUNDING_CAMPAIGN in Base.metadata.tables
    assert Table.INDUSTRIAL_FACILITY in Base.metadata.tables
    assert Table.HEALTHCARE_FACILITY in Base.metadata.tables


def test_chat_tablename():
    """Execute test_chat_tablename operation.

    Returns:
        The result of the operation.
    """
    assert Chat.__tablename__ == Table.CHAT


def test_crowdfunding_campaign_tablename():
    """Execute test_crowdfunding_campaign_tablename operation.

    Returns:
        The result of the operation.
    """
    assert CrowdfundingCampaign.__tablename__ == Table.CROWDFUNDING_CAMPAIGN


def test_industrial_facility_tablename():
    """Execute test_industrial_facility_tablename operation.

    Returns:
        The result of the operation.
    """
    assert IndustrialFacility.__tablename__ == Table.INDUSTRIAL_FACILITY


def test_healthcare_facility_tablename():
    """Execute test_healthcare_facility_tablename operation.

    Returns:
        The result of the operation.
    """
    assert HealthcareFacility.__tablename__ == Table.HEALTHCARE_FACILITY
