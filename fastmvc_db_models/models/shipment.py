"""
Shipment model.

Tracks outbound fulfillment for a commerce order: carrier, tracking, and
delivery lifecycle. One order may have several shipments (partial fulfillments).

Usage:
    >>> from fastmvc_db_models.models.shipment import Shipment
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB

from fastmvc_db_models.constants.db.table import Table
from fastmvc_db_models.models import Base


class Shipment(Base):
    """
    Physical (or third-party) shipment tied to an order.

    `status_id` can reference `status_lk` for carrier-agnostic states (label_created,
    in_transit, delivered). Destination may duplicate order shipping JSON for
    split-ship scenarios.

    Attributes:
        id: Primary key.
        urn: Stable external identifier.
        order_id: Parent order.
        status_id: FK to status_lk (shipment lifecycle).
        carrier_code: Machine code (ups, fedex, dhl, custom).
        carrier_name: Human-readable carrier label.
        service_level: e.g. ground, express.
        tracking_number: Carrier tracking id.
        tracking_url: Optional deep link for buyers.
        weight_grams: Optional shipped weight.
        shipped_at, delivered_at, estimated_delivery_at: Timestamps.
        destination_json: Optional JSON snapshot if different from order address.
        shipment_metadata: JSONB (label id, customs, package dimensions).
        created_at, updated_at: Audit fields.
    """

    __tablename__ = Table.SHIPMENT

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    order_id = Column(
        BigInteger,
        ForeignKey(Table.COMMERCE_ORDER + ".id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status_id = Column(BigInteger, ForeignKey("status_lk.id"), nullable=False, index=True)
    carrier_code = Column(String(64), nullable=True, index=True)
    carrier_name = Column(String(128), nullable=True)
    service_level = Column(String(64), nullable=True)
    tracking_number = Column(String(256), nullable=True, index=True)
    tracking_url = Column(String(1024), nullable=True)
    weight_grams = Column(BigInteger, nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True, index=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    estimated_delivery_at = Column(DateTime(timezone=True), nullable=True)
    destination_json = Column(JSONB, nullable=True)
    shipment_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "urn": self.urn,
            "order_id": self.order_id,
            "status_id": self.status_id,
            "carrier_code": self.carrier_code,
            "carrier_name": self.carrier_name,
            "service_level": self.service_level,
            "tracking_number": self.tracking_number,
            "tracking_url": self.tracking_url,
            "weight_grams": self.weight_grams,
            "shipped_at": self.shipped_at.isoformat() if self.shipped_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "estimated_delivery_at": (
                self.estimated_delivery_at.isoformat() if self.estimated_delivery_at else None
            ),
            "destination_json": self.destination_json,
            "metadata": self.shipment_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
