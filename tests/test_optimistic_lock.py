"""optimistic_lock helpers."""

from __future__ import annotations

import pytest

from src.optimistic_lock import (
    StaleVersionError,
    assert_version_matches,
    expected_version,
)


class _Obj:
    version = 3


def test_expected_version():
    assert expected_version(_Obj()) == 3
    assert expected_version(object()) is None


def test_assert_version_matches_ok():
    assert_version_matches(_Obj(), 3)


def test_assert_version_matches_skip_when_none():
    assert_version_matches(_Obj(), None)


def test_assert_version_mismatch():
    with pytest.raises(StaleVersionError):
        assert_version_matches(_Obj(), 1)


def test_assert_version_no_column():
    with pytest.raises(StaleVersionError, match="no version"):
        assert_version_matches(object(), 1)
