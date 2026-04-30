"""Geo-Partitioning Decorator."""

from typing import Dict, Optional, Type

from .models import BaseGeoModel, GeoShardingStrategy


def geo_partition(
    shard_key: str,
    strategy: GeoShardingStrategy = GeoShardingStrategy.PROXIMITY,
    replicas: Optional[Dict[str, int]] = None,
    sync_replication: bool = False,
    tablename: Optional[str] = None,
):
    """Decorator to enable geo-partitioning for a model.

    Args:
        shard_key: Dot-notation path to geo location field (e.g., "user.location.country")
        strategy: Sharding strategy
        replicas: Dict of region -> replica count
        sync_replication: Whether to wait for replication
        tablename: Database table name (defaults to class name)

    Example:
        @geo_partition(
            shard_key="location.country",
            strategy=GeoShardingStrategy.RESIDENCY,
            replicas={"us-west": 1, "eu-central": 1}
        )
        class UserData(BaseGeoModel):
            user_id: UUID
            location: GeoLocation
            data: Dict[str, Any]

    """

    def decorator(cls: Type[BaseGeoModel]) -> Type[BaseGeoModel]:
        """Execute decorator operation.

        Returns:
            The result of the operation.
        """
        # Ensure it's a subclass of BaseGeoModel
        if not issubclass(cls, BaseGeoModel):
            raise TypeError(
                f"@geo_partition can only be used on BaseGeoModel subclasses, "
                f"got {cls.__name__}"
            )

        # Set geo configuration on the class
        table = tablename or cls.__name__.lower()
        cls.set_geo_config(
            shard_key=shard_key,
            strategy=strategy,
            replicas=replicas or {},
            sync_replication=sync_replication,
            tablename=table,
        )

        # Mark as geo-partitioned
        cls._is_geo_partitioned = True

        return cls

    return decorator
