"""Smoke tests for selected ORM models (no live DB required)."""

from fast_database import Base
from fast_database.constants.table import Table
from fast_database.models.messaging_chat import Chat
from fast_database.models.status_lk import StatusLk
from fast_database.models.user import User


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
