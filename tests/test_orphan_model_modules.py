"""Import model modules that are not re-exported from ``fastx_database.persistence.models``."""

from __future__ import annotations


def test_standalone_model_modules_import():
    """Class bodies execute so coverage includes these tables."""
    import fastx_database.persistence.models.api_key  # noqa: F401
    import fastx_database.persistence.models.audit  # noqa: F401
    import fastx_database.persistence.models.consent  # noqa: F401
    import fastx_database.persistence.models.document  # noqa: F401
