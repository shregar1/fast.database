"""
Product (catalog) model.

Generic sellable item: SKU, display fields, price in minor units, optional inventory
and shipping hints. `product_metadata` holds industry-specific attributes (attributes,
categories, external IDs) without schema churn.

Usage:
    >>> from fastmvc_db_models.models.product import Product
"""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from src.constants.db.table import Table
from src.models import Base


class Product(Base):
    """
    Catalog product or service line item.

    Designed to work for retail, SaaS add-ons, bookings, or B2B SKUs: optional
    organization scoping, optional inventory tracking, JSON for flexible facets.

    Attributes:
        id: Primary key.
        urn: Stable external identifier.
        organization_id: Optional tenant/workspace FK.
        sku: Stock-keeping id; unique together with organization_id when used.
        slug: Optional URL slug (unique per org in application logic).
        name: Display name.
        description: Long description.
        product_type: Hint only, e.g. physical, digital, service, subscription.
        price_cents, compare_at_price_cents, currency: List pricing (minor units).
        cost_cents: Optional internal cost for margin reporting.
        is_active: Sellable flag.
        taxable: Whether tax engines should apply tax.
        requires_shipping: Physical goods vs digital.
        is_digital: Delivered electronically.
        track_inventory: If True, use inventory_quantity when applicable.
        inventory_quantity: On-hand stock when tracking.
        weight_grams: Shipping weight estimate.
        product_metadata: JSONB for categories, images, provider ids, custom fields.
        created_at, updated_at, created_by, updated_by: Audit fields.
    """

    __tablename__ = Table.PRODUCT
    __table_args__ = (
        UniqueConstraint("organization_id", "sku", name="uq_product_organization_sku"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    organization_id = Column(
        BigInteger,
        ForeignKey(Table.ORGANIZATION + ".id"),
        nullable=True,
        index=True,
    )
    sku = Column(String(128), nullable=True, index=True)
    slug = Column(String(256), nullable=True, index=True)
    name = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    product_type = Column(String(64), nullable=False, default="physical", index=True)
    price_cents = Column(BigInteger, nullable=False)
    compare_at_price_cents = Column(BigInteger, nullable=True)
    currency = Column(String(8), nullable=False, default="USD")
    cost_cents = Column(BigInteger, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    taxable = Column(Boolean, nullable=False, default=True)
    requires_shipping = Column(Boolean, nullable=False, default=True)
    is_digital = Column(Boolean, nullable=False, default=False)
    track_inventory = Column(Boolean, nullable=False, default=False)
    inventory_quantity = Column(BigInteger, nullable=True)
    weight_grams = Column(BigInteger, nullable=True)
    product_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)
    updated_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "urn": self.urn,
            "organization_id": self.organization_id,
            "sku": self.sku,
            "slug": self.slug,
            "name": self.name,
            "description": self.description,
            "product_type": self.product_type,
            "price_cents": self.price_cents,
            "compare_at_price_cents": self.compare_at_price_cents,
            "currency": self.currency,
            "cost_cents": self.cost_cents,
            "is_active": self.is_active,
            "taxable": self.taxable,
            "requires_shipping": self.requires_shipping,
            "is_digital": self.is_digital,
            "track_inventory": self.track_inventory,
            "inventory_quantity": self.inventory_quantity,
            "weight_grams": self.weight_grams,
            "metadata": self.product_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
