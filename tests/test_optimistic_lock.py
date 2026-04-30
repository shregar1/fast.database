"""optimistic_lock helpers."""

from __future__ import annotations

import pytest

from fastx_database.core.optimistic_lock import (
    StaleVersionError,
    assert_version_matches,
    expected_version,
)


class _Obj:
    """Represents the _Obj class."""

    version = 3


def test_expected_version():
    """Execute test_expected_version operation.

    Returns:
        The result of the operation.
    """
    assert expected_version(_Obj()) == 3
    assert expected_version(object()) is None


def test_assert_version_matches_ok():
    """Execute test_assert_version_matches_ok operation.

    Returns:
        The result of the operation.
    """
    assert_version_matches(_Obj(), 3)


def test_assert_version_matches_skip_when_none():
    """Execute test_assert_version_matches_skip_when_none operation.

    Returns:
        The result of the operation.
    """
    assert_version_matches(_Obj(), None)


def test_assert_version_mismatch():
    """Execute test_assert_version_mismatch operation.

    Returns:
        The result of the operation.
    """
    with pytest.raises(StaleVersionError):
        assert_version_matches(_Obj(), 1)


def test_assert_version_no_column():
    """Execute test_assert_version_no_column operation.

    Returns:
        The result of the operation.
    """
    with pytest.raises(StaleVersionError, match="no version"):
        assert_version_matches(object(), 1)
