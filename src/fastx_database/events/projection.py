"""Event projections for read models."""

from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import asyncio


class Projection(ABC):
    """Abstract base class for event projections.

    Projections build read models from event streams.
    """

    def __init__(self, name: str):
        """Execute __init__ operation.

        Args:
            name: The name parameter.
        """
        self.name = name
        self._handlers: Dict[str, Callable] = {}
        self._position = 0

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """Register an event handler."""
        self._handlers[event_type] = handler

    async def handle(self, event: Any) -> None:
        """Handle an event."""
        handler = self._handlers.get(event.event_type)
        if handler:
            await handler(event)
        self._position = event.sequence_number

    @abstractmethod
    async def reset(self) -> None:
        """Reset the projection."""
        pass

    @property
    def position(self) -> int:
        """Current position in the event stream."""
        return self._position


class ProjectionBuilder:
    """Builder for creating projections."""

    def __init__(self, name: str):
        """Execute __init__ operation.

        Args:
            name: The name parameter.
        """
        self.name = name
        self._handlers: Dict[str, Callable] = {}
        self._reset_handler: Optional[Callable] = None

    def on(self, event_type: str):
        """Decorator to register an event handler."""

        def decorator(func: Callable):
            """Execute decorator operation.

            Args:
                func: The func parameter.

            Returns:
                The result of the operation.
            """
            self._handlers[event_type] = func
            return func

        return decorator

    def reset(self, func: Callable):
        """Decorator to register reset handler."""
        self._reset_handler = func
        return func

    def build(self) -> Projection:
        """Build the projection."""
        projection = DynamicProjection(self.name)

        for event_type, handler in self._handlers.items():
            projection.register_handler(event_type, handler)

        if self._reset_handler:
            projection._reset = self._reset_handler

        return projection


class DynamicProjection(Projection):
    """Dynamically built projection."""

    def __init__(self, name: str):
        """Execute __init__ operation.

        Args:
            name: The name parameter.
        """
        super().__init__(name)
        self._reset: Optional[Callable] = None

    async def reset(self) -> None:
        """Execute reset operation.

        Returns:
            The result of the operation.
        """
        if self._reset:
            await self._reset()
        self._position = 0


# Example projection


class OrderSummaryProjection(Projection):
    """Projection that builds order summaries."""

    def __init__(self):
        """Execute __init__ operation."""
        super().__init__("order_summary")
        self._summaries: Dict[str, Dict[str, Any]] = {}

        # Register handlers
        self.register_handler("order_created", self._on_order_created)
        self.register_handler("item_added", self._on_item_added)
        self.register_handler("payment_submitted", self._on_payment_submitted)
        self.register_handler("order_shipped", self._on_order_shipped)

    async def reset(self) -> None:
        """Execute reset operation.

        Returns:
            The result of the operation.
        """
        self._summaries.clear()
        self._position = 0

    def get_summary(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order summary."""
        return self._summaries.get(order_id)

    def get_all_summaries(self) -> List[Dict[str, Any]]:
        """Get all order summaries."""
        return list(self._summaries.values())

    # Event handlers

    async def _on_order_created(self, event) -> None:
        """Execute _on_order_created operation.

        Args:
            event: The event parameter.

        Returns:
            The result of the operation.
        """
        self._summaries[event.aggregate_id] = {
            "order_id": event.aggregate_id,
            "customer_id": event.event_data["customer_id"],
            "status": "pending",
            "total_amount": 0.0,
            "item_count": 0,
        }

    async def _on_item_added(self, event) -> None:
        """Execute _on_item_added operation.

        Args:
            event: The event parameter.

        Returns:
            The result of the operation.
        """
        summary = self._summaries.get(event.aggregate_id)
        if summary:
            data = event.event_data
            summary["total_amount"] += data["quantity"] * data["price"]
            summary["item_count"] += data["quantity"]

    async def _on_payment_submitted(self, event) -> None:
        """Execute _on_payment_submitted operation.

        Args:
            event: The event parameter.

        Returns:
            The result of the operation.
        """
        summary = self._summaries.get(event.aggregate_id)
        if summary:
            summary["status"] = "paid"

    async def _on_order_shipped(self, event) -> None:
        """Execute _on_order_shipped operation.

        Args:
            event: The event parameter.

        Returns:
            The result of the operation.
        """
        summary = self._summaries.get(event.aggregate_id)
        if summary:
            summary["status"] = "shipped"
            summary["tracking_number"] = event.event_data.get("tracking_number")


class ProjectionRunner:
    """Runs projections against an event store."""

    def __init__(self, event_store, projections: List[Projection]):
        """Execute __init__ operation.

        Args:
            event_store: The event_store parameter.
            projections: The projections parameter.
        """
        self.event_store = event_store
        self.projections = projections
        self._running = False

    async def run(self, catch_up: bool = True) -> None:
        """Start processing events.

        Args:
            catch_up: Whether to process all existing events first

        """
        self._running = True

        if catch_up:
            # Get minimum position across all projections
            min_position = (
                min(p.position for p in self.projections) if self.projections else 0
            )

            # Catch up on existing events
            async for event in self.event_store.get_all_events(
                after_position=min_position
            ):
                if not self._running:
                    break

                for projection in self.projections:
                    if event.sequence_number > projection.position:
                        await projection.handle(event)

        # Continue with new events (would subscribe to event stream)
        while self._running:
            await asyncio.sleep(1)

    def stop(self) -> None:
        """Stop processing events."""
        self._running = False

    async def reset_all(self) -> None:
        """Reset all projections."""
        for projection in self.projections:
            await projection.reset()
