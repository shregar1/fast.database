"""
Order and order line models.

Represents a placed purchase: immutable snapshots of customer, addresses, and
money totals, with optional links back to cart and payment rows.

Usage:
    >>> from fast_database.models.order import Order, OrderItem
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from fast_database.constants.db.table import Table
from fast_database.models import Base


class Order(Base):
    """
    Customer order (invoice-like aggregate, separate from provider `invoice`).

    `order_number` is human-facing and unique. Addresses are JSONB blobs so any
    regional format or PII policy can be applied without multiple address tables.
    `status_id` ties to `status_lk` for workflow (pending, paid, shipped, cancelled).

    Attributes:
        id: Primary key.
        urn: Stable external identifier.
        order_number: Unique business key (e.g. ORD-2025-00042).
        user_id: Buyer FK.
        organization_id: Optional tenant / account.
        cart_id: Optional originating cart.
        status_id: FK to status_lk (order workflow).
        email: Contact email at time of order.
        customer_note: Buyer instructions.
        payment_status: Denormalized payment state (e.g. authorized, paid, failed).
        payment_transaction_id: Optional FK to payment_transaction when paid.
        currency: Order currency.
        subtotal_cents, discount_cents, tax_cents, shipping_cents, fees_cents,
        total_cents: Money in minor units (snapshots).
        amount_paid_cents, refunded_cents: Payment reconciliation hints.
        billing_address_json, shipping_address_json: JSON address snapshots.
        placed_at: When the order was submitted.
        paid_at, cancelled_at, fulfilled_at: Lifecycle timestamps.
        cancel_reason: If cancelled.
        external_order_id: PSP or marketplace order id (idempotency / sync).
        order_metadata: JSONB (tax ids, marketplace fees, EDI refs).
        created_at, updated_at, created_by, updated_by: Audit fields.
    """

    __tablename__ = Table.COMMERCE_ORDER
    __table_args__ = (UniqueConstraint("order_number", name="uq_order_order_number"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    order_number = Column(String(64), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    organization_id = Column(
        BigInteger,
        ForeignKey(Table.ORGANIZATION + ".id"),
        nullable=True,
        index=True,
    )
    cart_id = Column(
        BigInteger,
        ForeignKey(Table.CART + ".id"),
        nullable=True,
        index=True,
    )
    status_id = Column(BigInteger, ForeignKey("status_lk.id"), nullable=False, index=True)
    email = Column(String(320), nullable=False)
    customer_note = Column(Text, nullable=True)
    payment_status = Column(String(32), nullable=False, default="pending", index=True)
    payment_transaction_id = Column(
        BigInteger,
        ForeignKey(Table.PAYMENT_TRANSACTION + ".id"),
        nullable=True,
        index=True,
    )
    currency = Column(String(8), nullable=False, default="USD")
    subtotal_cents = Column(BigInteger, nullable=False)
    discount_cents = Column(BigInteger, nullable=False, default=0)
    tax_cents = Column(BigInteger, nullable=False, default=0)
    shipping_cents = Column(BigInteger, nullable=False, default=0)
    fees_cents = Column(BigInteger, nullable=False, default=0)
    total_cents = Column(BigInteger, nullable=False)
    amount_paid_cents = Column(BigInteger, nullable=False, default=0)
    refunded_cents = Column(BigInteger, nullable=False, default=0)
    billing_address_json = Column(JSONB, nullable=True)
    shipping_address_json = Column(JSONB, nullable=True)
    placed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    fulfilled_at = Column(DateTime(timezone=True), nullable=True)
    cancel_reason = Column(String(512), nullable=True)
    external_order_id = Column(String(128), nullable=True, index=True)
    order_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)
    updated_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "urn": self.urn,
            "order_number": self.order_number,
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "cart_id": self.cart_id,
            "status_id": self.status_id,
            "email": self.email,
            "customer_note": self.customer_note,
            "payment_status": self.payment_status,
            "payment_transaction_id": self.payment_transaction_id,
            "currency": self.currency,
            "subtotal_cents": self.subtotal_cents,
            "discount_cents": self.discount_cents,
            "tax_cents": self.tax_cents,
            "shipping_cents": self.shipping_cents,
            "fees_cents": self.fees_cents,
            "total_cents": self.total_cents,
            "amount_paid_cents": self.amount_paid_cents,
            "refunded_cents": self.refunded_cents,
            "billing_address_json": self.billing_address_json,
            "shipping_address_json": self.shipping_address_json,
            "placed_at": self.placed_at.isoformat() if self.placed_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "fulfilled_at": self.fulfilled_at.isoformat() if self.fulfilled_at else None,
            "cancel_reason": self.cancel_reason,
            "external_order_id": self.external_order_id,
            "metadata": self.order_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class OrderItem(Base):
    """
    Immutable line on an order.

    Fulfillment fields support partial ship/return flows without a separate table
    for every industry; use `fulfillment_status` + `item_metadata` for splits.

    Attributes:
        id: Primary key.
        urn: Stable external identifier.
        order_id: FK to orders.
        product_id: Optional FK to product (historical).
        sku: Snapshot SKU.
        title: Product title at purchase.
        variant_title: Variant label snapshot.
        quantity: Purchased quantity (may be fractional).
        unit_price_cents: Unit price in minor units.
        compare_at_price_cents: Optional list price snapshot.
        line_subtotal_cents: Before line discount.
        discount_cents: Line discount.
        tax_cents: Allocated tax.
        total_cents: Line total in minor units.
        currency: Line currency.
        fulfillment_status: e.g. pending, partial, fulfilled, returned, cancelled.
        sort_order: Display order on documents.
        item_metadata: JSONB (serial numbers, license keys, subscription term).
        created_at: Row creation (normally equals order placement).
    """

    __tablename__ = Table.ORDER_ITEM

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    order_id = Column(
        BigInteger,
        ForeignKey(Table.COMMERCE_ORDER + ".id", ondelete="CASCADE"),
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
    quantity = Column(Numeric(18, 6), nullable=False)
    unit_price_cents = Column(BigInteger, nullable=False)
    compare_at_price_cents = Column(BigInteger, nullable=True)
    line_subtotal_cents = Column(BigInteger, nullable=False)
    discount_cents = Column(BigInteger, nullable=False, default=0)
    tax_cents = Column(BigInteger, nullable=False, default=0)
    total_cents = Column(BigInteger, nullable=False)
    currency = Column(String(8), nullable=False, default="USD")
    fulfillment_status = Column(String(32), nullable=False, default="pending", index=True)
    sort_order = Column(BigInteger, nullable=False, default=0)
    item_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def to_dict(self) -> dict:
        q = float(self.quantity) if self.quantity is not None else None
        return {
            "id": self.id,
            "urn": self.urn,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "sku": self.sku,
            "title": self.title,
            "variant_title": self.variant_title,
            "quantity": q,
            "unit_price_cents": self.unit_price_cents,
            "compare_at_price_cents": self.compare_at_price_cents,
            "line_subtotal_cents": self.line_subtotal_cents,
            "discount_cents": self.discount_cents,
            "tax_cents": self.tax_cents,
            "total_cents": self.total_cents,
            "currency": self.currency,
            "fulfillment_status": self.fulfillment_status,
            "sort_order": self.sort_order,
            "metadata": self.item_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
