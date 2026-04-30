"""Smoke import of public API."""


def test_mixin_and_soft_delete_exported_from_package():
    """Execute test_mixin_and_soft_delete_exported_from_package operation.

    Returns:
        The result of the operation.
    """
    from fastx_database import (
        Base,
        SoftDeleteMixin,
        TimestampMixin,
        UUIDPrimaryKeyMixin,
        filter_active,
        mark_soft_deleted,
        restore_soft_deleted,
        select_active,
        where_not_deleted,
    )

    assert Base is not None
    assert TimestampMixin.__abstract__ is True
    assert UUIDPrimaryKeyMixin.__abstract__ is True
    assert SoftDeleteMixin.__abstract__ is True
    assert callable(select_active)
    assert callable(where_not_deleted)
    assert callable(mark_soft_deleted)
    assert callable(restore_soft_deleted)
    assert callable(filter_active)
