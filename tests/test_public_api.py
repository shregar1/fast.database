"""Public exports resolve."""

from __future__ import annotations

import importlib

import pytest

PACKAGE = "fastx_database"


def test_package_imports():
    """Execute test_package_imports operation.

    Returns:
        The result of the operation.
    """
    m = importlib.import_module(PACKAGE)
    assert m is not None


def test_public_exports_resolve():
    """Execute test_public_exports_resolve operation.

    Returns:
        The result of the operation.
    """
    m = importlib.import_module(PACKAGE)
    for export_name in getattr(m, "__all__", ()):
        obj = getattr(m, export_name)
        assert obj is not None


def test_version_when_present():
    """Execute test_version_when_present operation.

    Returns:
        The result of the operation.
    """
    m = importlib.import_module(PACKAGE)
    if hasattr(m, "__version__"):
        assert isinstance(m.__version__, str)
