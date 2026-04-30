"""Event Store implementations."""

from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
from uuid import UUID, uuid4
import json


@dataclass
class EventRecord:
    """A stored event."""

    id: UUID
    aggregate_id: str
    aggregate_type: str
    event_type: str
    event_data: Dict[str, Any]
    sequence_number: int
    timestamp: datetime
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Execute to_dict operation.

        Returns:
            The result of the operation.
        """
        return {
            "id": str(self.id),
            "aggregate_id": self.aggregate_id,
            "aggregate_type": self.aggregate_type,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "sequence_number": self.sequence_number,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventRecord":
        """Execute from_dict operation.

        Args:
            data: The data parameter.

        Returns:
            The result of the operation.
        """
        return cls(
            id=UUID(data["id"]),
            aggregate_id=data["aggregate_id"],
            aggregate_type=data["aggregate_type"],
            event_type=data["event_type"],
            event_data=data["event_data"],
            sequence_number=data["sequence_number"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


class EventStore(ABC):
    """Abstract event store."""

    @abstractmethod
    async def append(
        self,
        aggregate_id: str,
        aggregate_type: str,
        events: List[Dict[str, Any]],
        expected_version: Optional[int] = None,
    ) -> List[EventRecord]:
        """Append events to an aggregate."""
        pass

    @abstractmethod
    async def get_events(
        self, aggregate_id: str, from_sequence: int = 0
    ) -> List[EventRecord]:
        """Get events for an aggregate."""
        pass

    @abstractmethod
    async def get_all_events(
        self,
        event_types: Optional[List[str]] = None,
        after_position: Optional[int] = None,
    ) -> AsyncIterator[EventRecord]:
        """Get all events (for projections)."""
        pass

    @abstractmethod
    async def get_current_version(self, aggregate_id: str) -> int:
        """Get current version of an aggregate."""
        pass


class InMemoryEventStore(EventStore):
    """In-memory event store for development/testing."""

    def __init__(self):
        """Execute __init__ operation."""
        self._events: Dict[str, List[EventRecord]] = {}
        self._all_events: List[EventRecord] = []

    async def append(
        self,
        aggregate_id: str,
        aggregate_type: str,
        events: List[Dict[str, Any]],
        expected_version: Optional[int] = None,
    ) -> List[EventRecord]:
        """Execute append operation.

        Args:
            aggregate_id: The aggregate_id parameter.
            aggregate_type: The aggregate_type parameter.
            events: The events parameter.
            expected_version: The expected_version parameter.

        Returns:
            The result of the operation.
        """
        if aggregate_id not in self._events:
            self._events[aggregate_id] = []

        current_version = len(self._events[aggregate_id])

        if expected_version is not None and current_version != expected_version:
            raise ConflictError(
                f"Expected version {expected_version} but found {current_version}"
            )

        records = []
        for i, event in enumerate(events):
            record = EventRecord(
                id=uuid4(),
                aggregate_id=aggregate_id,
                aggregate_type=aggregate_type,
                event_type=event["type"],
                event_data=event.get("data", {}),
                sequence_number=current_version + i + 1,
                timestamp=datetime.utcnow(),
                metadata=event.get("metadata", {}),
            )
            records.append(record)
            self._events[aggregate_id].append(record)
            self._all_events.append(record)

        return records

    async def get_events(
        self, aggregate_id: str, from_sequence: int = 0
    ) -> List[EventRecord]:
        """Execute get_events operation.

        Args:
            aggregate_id: The aggregate_id parameter.
            from_sequence: The from_sequence parameter.

        Returns:
            The result of the operation.
        """
        events = self._events.get(aggregate_id, [])
        return [e for e in events if e.sequence_number >= from_sequence]

    async def get_all_events(
        self,
        event_types: Optional[List[str]] = None,
        after_position: Optional[int] = None,
    ) -> AsyncIterator[EventRecord]:
        """Execute get_all_events operation.

        Args:
            event_types: The event_types parameter.
            after_position: The after_position parameter.

        Returns:
            The result of the operation.
        """
        for event in self._all_events:
            if event_types and event.event_type not in event_types:
                continue
            if after_position and event.sequence_number <= after_position:
                continue
            yield event

    async def get_current_version(self, aggregate_id: str) -> int:
        """Execute get_current_version operation.

        Args:
            aggregate_id: The aggregate_id parameter.

        Returns:
            The result of the operation.
        """
        return len(self._events.get(aggregate_id, []))


class PostgreSQLEventStore(EventStore):
    """PostgreSQL event store for production."""

    def __init__(self, dsn: str):
        """Execute __init__ operation.

        Args:
            dsn: The dsn parameter.
        """
        self.dsn = dsn
        self._pool = None

    async def _get_pool(self):
        """Execute _get_pool operation.

        Returns:
            The result of the operation.
        """
        if self._pool is None:
            try:
                import asyncpg

                self._pool = await asyncpg.create_pool(self.dsn)
            except ImportError:
                raise ImportError("asyncpg required for PostgreSQLEventStore")
        return self._pool

    async def append(
        self,
        aggregate_id: str,
        aggregate_type: str,
        events: List[Dict[str, Any]],
        expected_version: Optional[int] = None,
    ) -> List[EventRecord]:
        """Execute append operation.

        Args:
            aggregate_id: The aggregate_id parameter.
            aggregate_type: The aggregate_type parameter.
            events: The events parameter.
            expected_version: The expected_version parameter.

        Returns:
            The result of the operation.
        """
        pool = await self._get_pool()

        async with pool.acquire() as conn:
            async with conn.transaction():
                # Check version
                current_version = await conn.fetchval(
                    "SELECT COUNT(*) FROM events WHERE aggregate_id = $1", aggregate_id
                )

                if expected_version is not None and current_version != expected_version:
                    raise ConflictError(
                        f"Expected version {expected_version} but found {current_version}"
                    )

                records = []
                for i, event in enumerate(events):
                    record_id = uuid4()
                    sequence = current_version + i + 1

                    await conn.execute(
                        """
                        INSERT INTO events (
                            id, aggregate_id, aggregate_type, event_type,
                            event_data, sequence_number, timestamp, metadata
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        """,
                        record_id,
                        aggregate_id,
                        aggregate_type,
                        event["type"],
                        json.dumps(event.get("data", {})),
                        sequence,
                        datetime.utcnow(),
                        json.dumps(event.get("metadata", {})),
                    )

                    records.append(
                        EventRecord(
                            id=record_id,
                            aggregate_id=aggregate_id,
                            aggregate_type=aggregate_type,
                            event_type=event["type"],
                            event_data=event.get("data", {}),
                            sequence_number=sequence,
                            timestamp=datetime.utcnow(),
                            metadata=event.get("metadata", {}),
                        )
                    )

                return records

    async def get_events(
        self, aggregate_id: str, from_sequence: int = 0
    ) -> List[EventRecord]:
        """Execute get_events operation.

        Args:
            aggregate_id: The aggregate_id parameter.
            from_sequence: The from_sequence parameter.

        Returns:
            The result of the operation.
        """
        pool = await self._get_pool()

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM events 
                WHERE aggregate_id = $1 AND sequence_number >= $2
                ORDER BY sequence_number
                """,
                aggregate_id,
                from_sequence,
            )

            return [
                EventRecord(
                    id=row["id"],
                    aggregate_id=row["aggregate_id"],
                    aggregate_type=row["aggregate_type"],
                    event_type=row["event_type"],
                    event_data=json.loads(row["event_data"]),
                    sequence_number=row["sequence_number"],
                    timestamp=row["timestamp"],
                    metadata=json.loads(row["metadata"]),
                )
                for row in rows
            ]

    async def get_all_events(
        self,
        event_types: Optional[List[str]] = None,
        after_position: Optional[int] = None,
    ) -> AsyncIterator[EventRecord]:
        """Execute get_all_events operation.

        Args:
            event_types: The event_types parameter.
            after_position: The after_position parameter.

        Returns:
            The result of the operation.
        """
        # Implementation for projections
        pass

    async def get_current_version(self, aggregate_id: str) -> int:
        """Execute get_current_version operation.

        Args:
            aggregate_id: The aggregate_id parameter.

        Returns:
            The result of the operation.
        """
        pool = await self._get_pool()

        async with pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT COUNT(*) FROM events WHERE aggregate_id = $1", aggregate_id
            )


class ConflictError(Exception):
    """Optimistic concurrency conflict."""

    pass
