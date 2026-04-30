"""Event-sourced aggregates."""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime
from uuid import uuid4

from fastx_database.core.constants.status import Status


@dataclass
class Event:
    """Domain event."""

    type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime

    def __init__(
        self, type: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None
    ):
        """Execute __init__ operation.

        Args:
            type: The type parameter.
            data: The data parameter.
            metadata: The metadata parameter.
        """
        self.type = type
        self.data = data
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()


class Aggregate(ABC):
    """Base class for event-sourced aggregates.

    Subclasses should implement apply_* methods for each event type.
    """

    def __init__(self, aggregate_id: Optional[str] = None):
        """Execute __init__ operation.

        Args:
            aggregate_id: The aggregate_id parameter.
        """
        self.id = aggregate_id or str(uuid4())
        self.version = 0
        self._uncommitted_events: List[Event] = []
        self._is_replaying = False

    def apply_event(self, event: Event) -> None:
        """Apply an event to the aggregate."""
        handler = getattr(self, f"apply_{event.type}", None)

        if handler:
            handler(event.data)

        if not self._is_replaying:
            self._uncommitted_events.append(event)

        self.version += 1

    def create_event(self, event_type: str, data: Dict[str, Any]) -> Event:
        """Create a new event."""
        return Event(
            type=event_type,
            data=data,
            metadata={
                "aggregate_id": self.id,
                "aggregate_type": self.__class__.__name__,
                "version": self.version + 1,
            },
        )

    def load_from_history(self, events: List[Event]) -> None:
        """Load aggregate from event history."""
        self._is_replaying = True
        try:
            for event in events:
                self.apply_event(event)
        finally:
            self._is_replaying = False

        # Clear uncommitted events after replay
        self._uncommitted_events.clear()

    def get_uncommitted_events(self) -> List[Event]:
        """Get uncommitted events."""
        return self._uncommitted_events.copy()

    def mark_committed(self) -> None:
        """Mark all events as committed."""
        self._uncommitted_events.clear()


def event_sourced(aggregate_type: Optional[str] = None):
    """Decorator for event-sourced aggregates.

    Args:
        aggregate_type: Optional type name (defaults to class name)

    """

    def decorator(cls):
        """Execute decorator operation.

        Returns:
            The result of the operation.
        """
        cls._is_event_sourced = True
        cls._aggregate_type = aggregate_type or cls.__name__

        # Ensure it inherits from Aggregate
        if not issubclass(cls, Aggregate):
            raise TypeError("Event-sourced classes must inherit from Aggregate")

        return cls

    return decorator


# Example aggregate implementations


@event_sourced()
class OrderAggregate(Aggregate):
    """Event-sourced Order aggregate."""

    def __init__(self, order_id: Optional[str] = None):
        """Execute __init__ operation.

        Args:
            order_id: The order_id parameter.
        """
        super().__init__(order_id)
        self.customer_id: Optional[str] = None
        self.items: List[Dict] = []
        self.status = Status.PENDING
        self.total_amount = 0.0

    @classmethod
    def create(cls, order_id: str, customer_id: str) -> "OrderAggregate":
        """Factory method to create a new order."""
        order = cls(order_id)
        event = order.create_event(
            "order_created", {"order_id": order_id, "customer_id": customer_id}
        )
        order.apply_event(event)
        return order

    def add_item(self, product_id: str, quantity: int, price: float) -> None:
        """Add item to order."""
        event = self.create_event(
            "item_added",
            {"product_id": product_id, "quantity": quantity, "price": price},
        )
        self.apply_event(event)

    def submit_payment(self, payment_id: str) -> None:
        """Submit payment for order."""
        if self.status != Status.PENDING:
            raise ValueError(f"Cannot submit payment for order in {self.status} status")

        event = self.create_event("payment_submitted", {"payment_id": payment_id})
        self.apply_event(event)

    def ship(self, tracking_number: str) -> None:
        """Mark order as shipped."""
        if self.status != Status.PAID:
            raise ValueError("Cannot ship unpaid order")

        event = self.create_event("order_shipped", {"tracking_number": tracking_number})
        self.apply_event(event)

    # Event handlers

    def apply_order_created(self, data: Dict[str, Any]) -> None:
        """Execute apply_order_created operation.

        Args:
            data: The data parameter.

        Returns:
            The result of the operation.
        """
        self.customer_id = data["customer_id"]

    def apply_item_added(self, data: Dict[str, Any]) -> None:
        """Execute apply_item_added operation.

        Args:
            data: The data parameter.

        Returns:
            The result of the operation.
        """
        self.items.append(
            {
                "product_id": data["product_id"],
                "quantity": data["quantity"],
                "price": data["price"],
            }
        )
        self.total_amount += data["quantity"] * data["price"]

    def apply_payment_submitted(self, data: Dict[str, Any]) -> None:
        """Execute apply_payment_submitted operation.

        Args:
            data: The data parameter.

        Returns:
            The result of the operation.
        """
        self.status = Status.PAID

    def apply_payment_failed(self, data: Dict[str, Any]) -> None:
        """Execute apply_payment_failed operation.

        Args:
            data: The data parameter.

        Returns:
            The result of the operation.
        """
        self.status = Status.PAYMENT_FAILED

    def apply_order_shipped(self, data: Dict[str, Any]) -> None:
        """Execute apply_order_shipped operation.

        Args:
            data: The data parameter.

        Returns:
            The result of the operation.
        """
        self.status = Status.SHIPPED
