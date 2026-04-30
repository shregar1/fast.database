"""Unit tests for soft_delete helpers (no DB)."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

from sqlalchemy import Column, Integer
from sqlalchemy.orm import Query

from fastx_database.persistence.models import Base
from fastx_database.core.mixins import SoftDeleteMixin
from fastx_database.core.soft_delete import (
    filter_active,
    mark_soft_deleted,
    restore_soft_deleted,
    select_active,
    where_not_deleted,
)


def test_where_not_deleted_and_select_active():
    """Execute test_where_not_deleted_and_select_active operation.

    Returns:
        The result of the operation.
    """

    class M(Base, SoftDeleteMixin):
        """Represents the M class."""

        __tablename__ = "t_soft_m"
        id = Column(Integer, primary_key=True)

    w = where_not_deleted(M)
    assert w is not None
    stmt = select_active(M)
    assert str(stmt).lower().find("is_deleted") != -1


def test_mark_and_restore_soft_deleted():
    """Execute test_mark_and_restore_soft_deleted operation.

    Returns:
        The result of the operation.
    """
    bare = MagicMock()
    bare.is_deleted = False
    mark_soft_deleted(bare)
    assert bare.is_deleted is True

    with_deleted = MagicMock()
    with_deleted.is_deleted = False
    with_deleted.deleted_at = None
    mark_soft_deleted(with_deleted, when=datetime(2020, 1, 1, tzinfo=timezone.utc))
    assert with_deleted.is_deleted is True
    assert with_deleted.deleted_at is not None

    restore_soft_deleted(with_deleted)
    assert with_deleted.is_deleted is False
    assert with_deleted.deleted_at is None


def test_filter_active_legacy_query():
    """Execute test_filter_active_legacy_query operation.

    Returns:
        The result of the operation.
    """
    q = MagicMock(spec=Query)
    attr = MagicMock()
    filter_active(q, attr)
    q.filter.assert_called_once()
