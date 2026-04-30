"""Geo Replication Service."""

from typing import Dict
from datetime import datetime

from .models import BaseGeoModel, GeoShardingStrategy
from .router import GeoShardingRouter


class GeoReplicationService:
    """Manages cross-region replication of geo-partitioned data."""

    _replication_queue: Dict[str, list] = {}

    @classmethod
    async def replicate(cls, record: BaseGeoModel) -> None:
        """Replicate record to configured regions."""
        replicas = record._geo_replicas
        primary_shard = record.geo_shard_id

        if not replicas:
            return

        for region, replica_count in replicas.items():
            if region == primary_shard:
                continue

            # Replicate based on strategy
            if record._geo_sync_replication:
                await cls._sync_replicate(record, region)
            else:
                # Async - queue for replication
                await cls._queue_replication(record, region)

    @classmethod
    async def _sync_replicate(cls, record: BaseGeoModel, target_region: str) -> None:
        """Synchronous replication."""
        # Get target database
        target_db = GeoShardingRouter.get_database(target_region)

        # Save to target
        await target_db.save(record)

        # Update replication timestamp
        record.geo_replicated_at[target_region] = datetime.utcnow()

    @classmethod
    async def _queue_replication(cls, record: BaseGeoModel, target_region: str) -> None:
        """Queue for async replication."""
        key = f"geo:replication:queue:{target_region}"

        if key not in cls._replication_queue:
            cls._replication_queue[key] = []

        cls._replication_queue[key].append(
            {
                "record_id": str(record.id),
                "tablename": record._geo_tablename,
                "target_region": target_region,
                "queued_at": datetime.utcnow().isoformat(),
            }
        )

    @classmethod
    async def process_replication_queue(cls, region: str) -> int:
        """Process queued replications for a region."""
        key = f"geo:replication:queue:{region}"
        queue = cls._replication_queue.get(key, [])
        processed = 0

        for item in queue[:]:
            try:
                # Process replication
                # In real implementation, would fetch record and save to target
                processed += 1
                queue.remove(item)
            except Exception as e:
                # Log error, will retry
                print(f"Replication failed for {item}: {e}")

        return processed

    @classmethod
    async def get_replication_lag(cls, region: str) -> float:
        """Get replication lag for region in seconds."""
        # In real implementation, would query replication status
        key = f"geo:replication:queue:{region}"
        queue = cls._replication_queue.get(key, [])

        if not queue:
            return 0.0

        # Calculate lag based on oldest item
        oldest = min(datetime.fromisoformat(item["queued_at"]) for item in queue)
        return (datetime.utcnow() - oldest).total_seconds()

    @classmethod
    def get_queue_length(cls, region: str) -> int:
        """Get number of items in replication queue."""
        key = f"geo:replication:queue:{region}"
        return len(cls._replication_queue.get(key, []))
