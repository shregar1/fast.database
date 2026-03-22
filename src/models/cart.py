"""
Shopping cart and cart line models.

`Cart` holds session state before checkout (authenticated user, optional org, or
guest via token). `CartItem` stores denormalized product fields so cart survives
catalog edits. Totals on the cart are caches maintained by the application.

Usage:
    >>> from fast_database.models.cart import Cart, CartItem
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB

from fast_database.constants.table import Table
from fast_database.models import Base


class Cart(Base):
    """
    Shopping basket before an order is placed.

    Status examples: draft, active, merged, converted, abandoned, locked.
    Either `user_id` or `guest_token` typically identifies the owner; both may be
    set after login merge.

    Attributes:
        id: Primary key.
        urn: Stable external identifier.
        user_id: Optional FK when logged in.
        guest_token: Opaque id for anonymous carts (cookie / session).
        organization_id: Optional B2B or marketplace tenant.
        currency: ISO currency for line items and totals.
        status: Lifecycle string (see above).
        coupon_code: Optional applied promo code (denormalized).
        item_count: Cached number of lines or units (app-defined).
        subtotal_cents, discount_total_cents, tax_estimate_cents,
        shipping_estimate_cents, total_cents: Cached money fields (minor units).
        expires_at: Optional TTL for abandoned-cart cleanup.
        cart_metadata: JSONB (device, campaign, sales channel, custom).
        created_at, updated_at, created_by, updated_by: Audit fields.
    """

    __tablename__ = Table.CART

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=True, index=True)
    guest_token = Column(String(128), nullable=True, index=True)
    organization_id = Column(
        BigInteger,
        ForeignKey(Table.ORGANIZATION + ".id"),
        nullable=True,
        index=True,
    )
    currency = Column(String(8), nullable=False, default="USD")
    status = Column(String(32), nullable=False, default="active", index=True)
    coupon_code = Column(String(64), nullable=True, index=True)
    item_count = Column(BigInteger, nullable=False, default=0)
    subtotal_cents = Column(BigInteger, nullable=False, default=0)
    discount_total_cents = Column(BigInteger, nullable=False, default=0)
    tax_estimate_cents = Column(BigInteger, nullable=False, default=0)
    shipping_estimate_cents = Column(BigInteger, nullable=False, default=0)
    total_cents = Column(BigInteger, nullable=False, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    cart_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)
    updated_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "urn": self.urn,
            "user_id": self.user_id,
            "guest_token": self.guest_token,
            "organization_id": self.organization_id,
            "currency": self.currency,
            "status": self.status,
            "coupon_code": self.coupon_code,
            "item_count": self.item_count,
            "subtotal_cents": self.subtotal_cents,
            "discount_total_cents": self.discount_total_cents,
            "tax_estimate_cents": self.tax_estimate_cents,
            "shipping_estimate_cents": self.shipping_estimate_cents,
            "total_cents": self.total_cents,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.cart_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CartItem(Base):
    """
    Single line in a cart.

    Snapshots `title` / `variant_title` / `sku` so display stays stable if the
    catalog changes. `quantity` supports fractional units (weight, hours) via Numeric.

    Attributes:
        id: Primary key.
        urn: Stable external identifier.
        cart_id: FK to cart.
        product_id: Optional FK to product (catalog may delete; snapshot still valid).
        sku: Copied SKU at add-to-cart time.
        title: Product title snapshot.
        variant_title: Variant option label (size, plan tier, etc.).
        quantity: Ordered amount (supports decimals).
        unit_price_cents: Price per unit in minor currency units.
        compare_at_price_cents: Optional strike-through list price.
        currency: Line currency (normally matches cart).
        line_subtotal_cents: quantity * unit, before line discounts (app-maintained).
        discount_cents: Line-level discount.
        tax_cents: Estimated line tax.
        notes: Buyer or gift message (short).
        sort_order: Display order within the cart.
        item_metadata: JSONB (bundle children, custom options, engraving).
        created_at, updated_at: Timestamps.
    """

    __tablename__ = Table.CART_ITEM

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    cart_id = Column(
        BigInteger,
        ForeignKey(Table.CART + ".id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = Column(
        BigInteger,
        ForeignKey(Table.PRODUCT + ".id"),
        nullable=True,
        index=True,
    )
    sku = Column(String(128), nullable=True, index=True)
    title = Column(String(512), nullable=False)
    variant_title = Column(String(256), nullable=True)
    quantity = Column(Numeric(18, 6), nullable=False, default=1)
    unit_price_cents = Column(BigInteger, nullable=False)
    compare_at_price_cents = Column(BigInteger, nullable=True)
    currency = Column(String(8), nullable=False, default="USD")
    line_subtotal_cents = Column(BigInteger, nullable=False)
    discount_cents = Column(BigInteger, nullable=False, default=0)
    tax_cents = Column(BigInteger, nullable=False, default=0)
    notes = Column(String(1024), nullable=True)
    sort_order = Column(BigInteger, nullable=False, default=0)
    item_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        q = float(self.quantity) if self.quantity is not None else None
        return {
            "id": self.id,
            "urn": self.urn,
            "cart_id": self.cart_id,
            "product_id": self.product_id,
            "sku": self.sku,
            "title": self.title,
            "variant_title": self.variant_title,
            "quantity": q,
            "unit_price_cents": self.unit_price_cents,
            "compare_at_price_cents": self.compare_at_price_cents,
            "currency": self.currency,
            "line_subtotal_cents": self.line_subtotal_cents,
            "discount_cents": self.discount_cents,
            "tax_cents": self.tax_cents,
            "notes": self.notes,
            "sort_order": self.sort_order,
            "metadata": self.item_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
