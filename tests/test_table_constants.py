"""Tests for shared table name constants."""

from fastx_database.core.constants.table import Table


def test_core_table_names_exist():
    """Execute test_core_table_names_exist operation.

    Returns:
        The result of the operation.
    """
    assert Table.USER == "user"
    assert Table.SESSION == "sessions"
    assert isinstance(Table.LEDGER_WORKSPACE, str)


def test_commerce_table_names():
    """Execute test_commerce_table_names operation.

    Returns:
        The result of the operation.
    """
    assert Table.PRODUCT == "product"
    assert Table.COMMERCE_ORDER == "orders"


def test_messaging_table_names():
    """Execute test_messaging_table_names operation.

    Returns:
        The result of the operation.
    """
    assert Table.CHAT == "chats"
    assert Table.CHAT_MESSAGE == "chat_messages"
    assert Table.MESSAGE_READ_RECEIPT == "message_read_receipts"


def test_crowdfunding_table_names():
    """Execute test_crowdfunding_table_names operation.

    Returns:
        The result of the operation.
    """
    assert Table.CROWDFUNDING_CAMPAIGN == "crowdfunding_campaign"
    assert Table.CROWDFUNDING_REWARD == "crowdfunding_reward"
    assert Table.CROWDFUNDING_PLEDGE == "crowdfunding_pledge"


def test_industrial_iot_table_names():
    """Execute test_industrial_iot_table_names operation.

    Returns:
        The result of the operation.
    """
    assert Table.INDUSTRIAL_FACILITY == "industrial_facility"
    assert Table.INDUSTRIAL_ASSET == "industrial_asset"
    assert Table.INDUSTRIAL_IOT_DEVICE == "industrial_iot_device"
    assert Table.INDUSTRIAL_TELEMETRY_CHANNEL == "industrial_telemetry_channel"
    assert Table.INDUSTRIAL_TELEMETRY_SAMPLE == "industrial_telemetry_sample"


def test_healthcare_table_names():
    """Execute test_healthcare_table_names operation.

    Returns:
        The result of the operation.
    """
    assert Table.HEALTHCARE_FACILITY == "healthcare_facility"
    assert Table.HEALTHCARE_PATIENT == "healthcare_patient"
    assert Table.HEALTHCARE_PRACTITIONER == "healthcare_practitioner"
    assert Table.CLINICAL_ENCOUNTER == "clinical_encounter"
    assert Table.CLINICAL_ENCOUNTER_PARTICIPANT == "clinical_encounter_participant"
