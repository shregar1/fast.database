"""Generic industrial IoT & automation models (multi-domain).

Use for factory floors, warehouses, energy sites, logistics hubs, or any **physical site**
with **equipment hierarchy**, **edge devices**, and **telemetry channels**. Amounts of
high-volume time-series data are often offloaded to a dedicated TSDB; ``IndustrialTelemetrySample``
is a **bounded** store for recent samples, edge sync, or project-scoped history.

Usage:
    >>> from fastx_database.persistence.models.industrial_iot import (
    ...     IndustrialAsset,
    ...     IndustrialFacility,
    ...     IndustrialIoTDevice,
    ...     IndustrialTelemetryChannel,
    ...     IndustrialTelemetrySample,
    ... )
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

from fastx_database.core.constants.db import StringLength
from fastx_database.core.constants.status import Status
from fastx_database.core.constants.table import Table
from fastx_database.core.mixins import SoftDeleteMixin, TimestampMixin
from fastx_database.persistence.models import Base


def _utc_now() -> datetime:
    """Execute _utc_now operation.

    Returns:
        The result of the operation.
    """
    return datetime.now(timezone.utc)


class IndustrialFacility(Base, TimestampMixin, SoftDeleteMixin):
    """A logical site: plant, warehouse, substation, farm, hospital wing, etc.

    ``facility_code`` is **globally unique** (stable external id / slug for integrations).
    ``organization_id`` is optional tenant scope when applicable.
    """

    __tablename__ = Table.INDUSTRIAL_FACILITY

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(StringLength.URN), nullable=False, unique=True, index=True)
    organization_id = Column(
        BigInteger,
        ForeignKey(f"{Table.ORGANIZATION}.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    facility_code = Column(String(StringLength.CODE), nullable=False, unique=True, index=True)
    name = Column(String(StringLength.DESCRIPTION), nullable=False)
    description = Column(Text, nullable=True)
    timezone = Column(String(StringLength.CODE), nullable=True)
    country_code = Column(String(StringLength.CODE), nullable=True)
    facility_metadata = Column("metadata", JSONB, nullable=True)


class IndustrialAsset(Base, TimestampMixin, SoftDeleteMixin):
    """A physical or logical asset: line, machine, cell, sensor rack, AGV route, etc.

    Optional ``parent_asset_id`` forms a tree under one :class:`IndustrialFacility`.
    ``external_ref`` is an optional ERP/MES key; uniqueness is enforced in application
    logic if needed (multiple unset refs are allowed).
    """

    __tablename__ = Table.INDUSTRIAL_ASSET
    __table_args__ = (
        Index(
            "ix_industrial_asset_facility_external_ref",
            "facility_id",
            "external_ref",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(StringLength.URN), nullable=False, unique=True, index=True)
    facility_id = Column(
        BigInteger,
        ForeignKey(f"{Table.INDUSTRIAL_FACILITY}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_asset_id = Column(
        BigInteger,
        ForeignKey(f"{Table.INDUSTRIAL_ASSET}.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name = Column(String(StringLength.DESCRIPTION), nullable=False)
    asset_kind = Column(String(StringLength.URN), nullable=False, index=True)
    external_ref = Column(String(StringLength.NAME), nullable=True, index=True)
    status = Column(String(StringLength.STATUS), nullable=False, default=Status.ACTIVE, index=True)
    asset_metadata = Column("metadata", JSONB, nullable=True)


class IndustrialIoTDevice(Base, TimestampMixin, SoftDeleteMixin):
    """A connected edge device: gateway, PLC, IPC, sensor hub, robot controller, etc.

    ``device_key`` is stable within the facility (used in MQTT/OPC mapping).
    """

    __tablename__ = Table.INDUSTRIAL_IOT_DEVICE
    __table_args__ = (
        UniqueConstraint(
            "facility_id",
            "device_key",
            name="uq_industrial_iot_device_facility_key",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(StringLength.URN), nullable=False, unique=True, index=True)
    facility_id = Column(
        BigInteger,
        ForeignKey(f"{Table.INDUSTRIAL_FACILITY}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    asset_id = Column(
        BigInteger,
        ForeignKey(f"{Table.INDUSTRIAL_ASSET}.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    device_key = Column(String(256), nullable=False, index=True)
    display_name = Column(String(512), nullable=False)
    protocol = Column(String(64), nullable=False, default="unknown", index=True)
    manufacturer = Column(String(256), nullable=True)
    model_name = Column(String(256), nullable=True)
    serial_number = Column(String(256), nullable=True)

    connection_status = Column(
        String(32), nullable=False, default="unknown", index=True
    )
    last_seen_at = Column(DateTime(timezone=True), nullable=True, index=True)
    firmware_version = Column(String(128), nullable=True)

    device_metadata = Column("metadata", JSONB, nullable=True)


class IndustrialTelemetryChannel(Base, TimestampMixin, SoftDeleteMixin):
    """A logical signal on a device (tag, topic leaf, OPC node id, register map).

    ``channel_key`` is unique per device; ``quantity_kind`` and ``unit`` are free-form strings.
    """

    __tablename__ = Table.INDUSTRIAL_TELEMETRY_CHANNEL
    __table_args__ = (
        UniqueConstraint(
            "device_id",
            "channel_key",
            name="uq_industrial_telemetry_channel_device_key",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(StringLength.URN), nullable=False, unique=True, index=True)
    device_id = Column(
        BigInteger,
        ForeignKey(f"{Table.INDUSTRIAL_IOT_DEVICE}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel_key = Column(String(StringLength.DESCRIPTION), nullable=False, index=True)
    display_name = Column(String(StringLength.DESCRIPTION), nullable=True)
    unit = Column(String(StringLength.CODE), nullable=True)
    quantity_kind = Column(String(StringLength.URN), nullable=True, index=True)
    value_schema = Column(String(StringLength.STATUS), nullable=False, default="numeric", index=True)
    channel_metadata = Column("metadata", JSONB, nullable=True)


class IndustrialTelemetrySample(Base):
    """One observed value (bounded history / edge buffer; not a full historian).

    Prefer external TSDBs for high-cardinality long retention; use this for automation
    state, recent windows, or cross-domain sync.
    """

    __tablename__ = Table.INDUSTRIAL_TELEMETRY_SAMPLE
    __table_args__ = (
        Index(
            "ix_industrial_telemetry_sample_channel_observed",
            "channel_id",
            "observed_at",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(StringLength.URN), nullable=False, unique=True, index=True)
    channel_id = Column(
        BigInteger,
        ForeignKey(f"{Table.INDUSTRIAL_TELEMETRY_CHANNEL}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    observed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    value_numeric = Column(Numeric(28, 10), nullable=True)
    value_text = Column(Text, nullable=True)
    value_json = Column(JSONB, nullable=True)
    quality_code = Column(String(StringLength.STATUS), nullable=True)
    source_event_id = Column(String(StringLength.URN), nullable=True, index=True)
    ingested_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
        server_default=func.now(),
    )
