"""Tests for shared table name constants."""

from fast_database.constants.table import Table


def test_core_table_names_exist():
    assert Table.USER == "user"
    assert Table.SESSION == "sessions"
    assert isinstance(Table.LEDGER_WORKSPACE, str)


def test_commerce_table_names():
    assert Table.PRODUCT == "product"
    assert Table.COMMERCE_ORDER == "orders"


def test_messaging_table_names():
    assert Table.CHAT == "chats"
    assert Table.CHAT_MESSAGE == "chat_messages"
    assert Table.MESSAGE_READ_RECEIPT == "message_read_receipts"
