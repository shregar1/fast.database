"""
Shipment tracking log model.

One row per carrier or aggregator event (scan, status change, exception). Used to
render timelines, reconcile webhooks, and debug integrations. Typically append-only.

Usage:
    >>> from fastmvc_db_models.models.shipment_tracking_log import ShipmentTrackingLog
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from fastmvc_db_models.constants.db.table import Table
from fastmvc_db_models.models import Base


class ShipmentTrackingLog(Base):
    """
    A single tracking milestone for a shipment.

    `event_at` is when the carrier reports the event (often in local time; store
    as provided or normalized in application code). `recorded_at` is when this row
    was written (ingestion time). `external_event_id` supports idempotent upserts
    from carrier APIs when present.

    Attributes:
        id: Primary key.
        urn: Stable external identifier.
        shipment_id: FK to shipments.
        event_at: Carrier-reported event time (UTC recommended).
        recorded_at: When the event was stored in our system.
        status_code: Carrier-specific machine code (e.g. UPS activity code).
        status_label: Human-readable status (e.g. "Out for delivery").
        location_line: Single-line location description (city, facility name).
        location_city, location_region, location_postal_code, location_country:
            Optional structured location fields.
        description: Carrier detail / exception message.
        source: Origin of the row (carrier_api, webhook, aftership, manual, etc.).
        external_event_id: Idempotency key from carrier or aggregator.
        event_metadata: JSONB (coordinates, substatus, raw nested fields).
        raw_payload: Full provider response for audit and reprocessing.
    """

    __tablename__ = Table.SHIPMENT_TRACKING_LOG
    __table_args__ = (
        UniqueConstraint(
            "shipment_id",
            "external_event_id",
            name="uq_shipment_tracking_log_shipment_external_event",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    shipment_id = Column(
        BigInteger,
        ForeignKey(Table.SHIPMENT + ".id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_at = Column(DateTime(timezone=True), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    status_code = Column(String(64), nullable=True, index=True)
    status_label = Column(String(256), nullable=True)
    location_line = Column(String(512), nullable=True)
    location_city = Column(String(128), nullable=True)
    location_region = Column(String(128), nullable=True)
    location_postal_code = Column(String(32), nullable=True)
    location_country = Column(String(8), nullable=True)
    description = Column(Text, nullable=True)
    source = Column(String(64), nullable=False, default="carrier_api", index=True)
    external_event_id = Column(String(256), nullable=True, index=True)
    event_metadata = Column("metadata", JSONB, nullable=True)
    raw_payload = Column(JSONB, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "urn": self.urn,
            "shipment_id": self.shipment_id,
            "event_at": self.event_at.isoformat() if self.event_at else None,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
            "status_code": self.status_code,
            "status_label": self.status_label,
            "location_line": self.location_line,
            "location_city": self.location_city,
            "location_region": self.location_region,
            "location_postal_code": self.location_postal_code,
            "location_country": self.location_country,
            "description": self.description,
            "source": self.source,
            "external_event_id": self.external_event_id,
            "metadata": self.event_metadata,
            "raw_payload": self.raw_payload,
        }
