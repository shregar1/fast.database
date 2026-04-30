"""FastMVC Event Sourcing Module.

Event-driven architecture with event stores and aggregates.
"""

from .store import (
    EventStore,
    InMemoryEventStore,
    PostgreSQLEventStore,
    EventRecord,
)
from .aggregate import (
    Aggregate,
    event_sourced,
    Event,
)
from .projection import (
    Projection,
    ProjectionBuilder,
)

__all__ = [
    "EventStore",
    "InMemoryEventStore",
    "PostgreSQLEventStore",
    "EventRecord",
    "Aggregate",
    "event_sourced",
    "Event",
    "Projection",
    "ProjectionBuilder",
]
