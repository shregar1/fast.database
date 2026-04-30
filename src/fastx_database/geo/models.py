"""Geo-Partitioning Models."""

from enum import Enum
from typing import Optional, Dict, Any, List, TypeVar, Type
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from fastx_database.core.constants.geo import EARTH_RADIUS_KM, Shard


class GeoShardingStrategy(Enum):
    """Strategies for geo-sharding."""

    PROXIMITY = "proximity"  # Route to nearest shard
    RESIDENCY = "residency"  # Strict data residency
    REPLICATED = "replicated"  # Full replication across regions
    PARTITIONED = "partitioned"  # Partitioned by geo key


class GeoPoint(BaseModel):
    """Geographic coordinates."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

    def distance_to(self, other: "GeoPoint") -> float:
        """Calculate distance in kilometers using Haversine formula."""
        from math import radians, sin, cos, sqrt, atan2

        R = EARTH_RADIUS_KM  # Earth's radius in km

        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c


class GeoLocation(BaseModel):
    """Complete geographic location."""

    country: str  # ISO 3166-1 alpha-2
    region: Optional[str] = None  # State/Province
    city: Optional[str] = None
    coordinates: Optional[GeoPoint] = None
    timezone: Optional[str] = None


T = TypeVar("T", bound="BaseGeoModel")


class BaseGeoModel(BaseModel):
    """Base model for geo-partitioned data.

    Subclass this and use @geo_partition decorator to enable geo-sharding.
    """

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Geo fields (auto-populated)
    geo_location: Optional[GeoLocation] = None
    geo_shard_id: Optional[str] = None  # Which shard owns this record
    geo_replicated_at: Dict[str, datetime] = Field(default_factory=dict)

    # Configuration (set by decorator)
    _geo_shard_key: Optional[str] = None
    _geo_strategy: GeoShardingStrategy = GeoShardingStrategy.PROXIMITY
    _geo_replicas: Dict[str, int] = {}
    _geo_sync_replication: bool = False
    _geo_tablename: Optional[str] = None

    class Config:
        """Represents the Config class."""

        arbitrary_types_allowed = True

    @classmethod
    def get_shard_for_location(cls, location: GeoLocation) -> str:
        """Determine which shard should store this record."""
        # Map country to shard
        shard_map = {
            # North America
            "US": Shard.US_EAST,
            "CA": Shard.US_EAST,
            "MX": Shard.US_EAST,
            # Europe
            "GB": Shard.EU_WEST,
            "DE": Shard.EU_WEST,
            "FR": Shard.EU_WEST,
            "IT": Shard.EU_WEST,
            "ES": Shard.EU_WEST,
            "NL": Shard.EU_WEST,
            # Asia Pacific
            "JP": Shard.APAC_TOKYO,
            "KR": Shard.APAC_TOKYO,
            "SG": Shard.APAC_SINGAPORE,
            "AU": Shard.APAC_SYDNEY,
            "NZ": Shard.APAC_SYDNEY,
            "IN": Shard.APAC_SINGAPORE,
        }
        return shard_map.get(location.country, Shard.US_EAST)

    @classmethod
    async def create_in_region(cls: Type[T], location: GeoLocation, **data) -> T:
        """Create record in appropriate region."""
        shard_id = cls.get_shard_for_location(location)

        instance = cls(geo_location=location, geo_shard_id=shard_id, **data)

        # Save to primary shard (implementation would use actual DB)
        await cls._save_to_shard(instance, shard_id)

        # Trigger replication if configured
        if cls._geo_replicas:
            await cls._replicate(instance)

        return instance

    @classmethod
    async def _save_to_shard(cls, instance: "BaseGeoModel", shard_id: str) -> None:
        """Save instance to specific shard."""
        # Placeholder - actual implementation would use database
        pass

    @classmethod
    async def _replicate(cls, instance: "BaseGeoModel") -> None:
        """Replicate to configured regions."""
        from .replication import GeoReplicationService

        await GeoReplicationService.replicate(instance)

    @classmethod
    async def get_by_id(
        cls: Type[T], id: UUID, preferred_region: Optional[str] = None
    ) -> Optional[T]:
        """Get record, preferring nearby replica."""
        # In real implementation, would query appropriate shard
        # For now, return None
        return None

    @classmethod
    def set_geo_config(
        cls,
        shard_key: str,
        strategy: GeoShardingStrategy,
        replicas: Dict[str, int],
        sync_replication: bool,
        tablename: str,
    ) -> None:
        """Set geo configuration (called by decorator)."""
        cls._geo_shard_key = shard_key
        cls._geo_strategy = strategy
        cls._geo_replicas = replicas
        cls._geo_sync_replication = sync_replication
        cls._geo_tablename = tablename


class ShardConfig(BaseModel):
    """Configuration for a geo-shard."""

    shard_id: str
    primary_region: str
    replica_regions: List[str] = []
    strategy: GeoShardingStrategy = GeoShardingStrategy.PROXIMITY
    partition_key: Optional[str] = None
    gdpr_compliant: bool = False


class GeoReplicaConfig(BaseModel):
    """Configuration for geo-replicas."""

    region: str
    replica_count: int = 1
    priority: int = 1
    is_read_replica: bool = False
    sync_mode: str = "async"  # "sync" or "async"
