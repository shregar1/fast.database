"""Smoke tests for selected ORM models (no live DB required)."""

from fastmvc_db_models import Base
from fastmvc_db_models.constants.db.table import Table
from fastmvc_db_models.models.messaging_chat import Chat
from fastmvc_db_models.models.status_lk import StatusLk
from fastmvc_db_models.models.user import User


def test_user_tablename():
    assert User.__tablename__ == Table.USER


def test_status_lk_has_code_column():
    assert any(c.name == "code" for c in StatusLk.__table__.columns)


def test_metadata_registers_core_tables():
    """Models use PostgreSQL types (e.g. JSONB); metadata still registers table names."""
    assert Table.USER in Base.metadata.tables
    assert "status_lk" in Base.metadata.tables
    assert len(Base.metadata.tables) > 20
    assert Table.CHAT in Base.metadata.tables


def test_chat_tablename():
    assert Chat.__tablename__ == Table.CHAT
