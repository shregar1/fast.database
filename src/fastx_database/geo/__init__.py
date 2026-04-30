"""FastMVC Geo-Partitioning Module.

Automatic geo-aware data sharding for global applications with data residency compliance.
"""

from .models import (
    GeoPoint,
    GeoLocation,
    BaseGeoModel,
    GeoShardingStrategy,
)
from .router import GeoShardingRouter
from .decorator import geo_partition
from .replication import GeoReplicationService
from .gdpr import GDPRCompliance

__all__ = [
    "GeoPoint",
    "GeoLocation",
    "BaseGeoModel",
    "GeoShardingStrategy",
    "GeoShardingRouter",
    "geo_partition",
    "GeoReplicationService",
    "GDPRCompliance",
]
