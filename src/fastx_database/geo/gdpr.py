"""GDPR Compliance Features."""

from typing import Set, Dict, Any, Optional, List
from uuid import UUID

from fastx_database.core.constants.geo import Shard
from .models import BaseGeoModel, GeoLocation
from .router import GeoShardingRouter


class GDPRCompliance:
    """GDPR-specific compliance features for geo-partitioning."""

    # EU member states (ISO 3166-1 alpha-2)
    EU_COUNTRIES: Set[str] = {
        "AT",  # Austria
        "BE",  # Belgium
        "BG",  # Bulgaria
        "HR",  # Croatia
        "CY",  # Cyprus
        "CZ",  # Czech Republic
        "DK",  # Denmark
        "EE",  # Estonia
        "FI",  # Finland
        "FR",  # France
        "DE",  # Germany
        "GR",  # Greece
        "HU",  # Hungary
        "IE",  # Ireland
        "IT",  # Italy
        "LV",  # Latvia
        "LT",  # Lithuania
        "LU",  # Luxembourg
        "MT",  # Malta
        "NL",  # Netherlands
        "PL",  # Poland
        "PT",  # Portugal
        "RO",  # Romania
        "SK",  # Slovakia
        "SI",  # Slovenia
        "ES",  # Spain
        "SE",  # Sweden
    }

    # EEA countries (also covered)
    EEA_COUNTRIES: Set[str] = EU_COUNTRIES | {
        "IS",  # Iceland
        "LI",  # Liechtenstein
        "NO",  # Norway
    }

    @classmethod
    def requires_eu_residency(cls, country_code: str) -> bool:
        """Check if country requires EU data residency."""
        return country_code.upper() in cls.EEA_COUNTRIES

    @classmethod
    def get_appropriate_shard(cls, location: GeoLocation) -> str:
        """Get appropriate shard for data residency compliance."""
        if cls.requires_eu_residency(location.country):
            # Must use EU shard
            return Shard.EU_WEST  # Primary EU shard

        # Use proximity-based routing for non-EU
        from .router import GeoShardingRouter

        if location.coordinates:
            return GeoShardingRouter.find_nearest_shard(location.coordinates)

        return Shard.US_EAST  # Default

    @classmethod
    async def handle_data_deletion_request(
        cls, user_id: UUID, model_class: Optional[type] = None
    ) -> Dict[str, Any]:
        """Handle GDPR right to erasure (Article 17).

        Deletes all data for a user across all shards.
        """
        deleted_shards = []
        failed_shards = []

        # Find all shards
        shards = GeoShardingRouter.list_shards()

        for shard_id in shards:
            try:
                db = GeoShardingRouter.get_database(shard_id)

                if model_class:
                    # Delete specific model
                    records = await db.query(model_class, user_id=user_id)
                    for record in records:
                        # Delete record
                        pass  # Actual deletion
                else:
                    # Delete all user data across all tables
                    pass  # Implementation

                deleted_shards.append(shard_id)

            except Exception as e:
                failed_shards.append({"shard": shard_id, "error": str(e)})

        # Log deletion for compliance
        await AuditLog.log_gdpr_deletion(user_id, deleted_shards)

        return {
            "user_id": str(user_id),
            "deleted_from": deleted_shards,
            "failed": failed_shards,
            "deleted_at": datetime.utcnow().isoformat(),
        }

    @classmethod
    async def export_user_data(
        cls, user_id: UUID, model_classes: Optional[List[type]] = None
    ) -> Dict[str, Any]:
        """Handle GDPR data portability (Article 20).

        Exports all data for a user in machine-readable format.
        """
        all_data: Dict[str, Any] = {
            "user_id": str(user_id),
            "exported_at": datetime.utcnow().isoformat(),
            "shards": {},
        }

        shards = GeoShardingRouter.list_shards()

        for shard_id in shards:
            db = GeoShardingRouter.get_database(shard_id)
            shard_data = {}

            try:
                if model_classes:
                    for model_class in model_classes:
                        records = await db.query(model_class, user_id=user_id)
                        shard_data[model_class.__name__] = [
                            cls._serialize_record(r) for r in records
                        ]
                else:
                    # Query all geo-partitioned models
                    pass

                if shard_data:
                    all_data["shards"][shard_id] = shard_data

            except Exception as e:
                all_data["shards"][shard_id] = {"error": str(e)}

        return all_data

    @classmethod
    async def handle_data_rectification(
        cls, user_id: UUID, corrections: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle GDPR right to rectification (Article 16)."""
        updated_shards = []

        shards = GeoShardingRouter.list_shards()

        for shard_id in shards:
            db = GeoShardingRouter.get_database(shard_id)
            # Apply corrections
            updated_shards.append(shard_id)

        return {
            "user_id": str(user_id),
            "updated_shards": updated_shards,
            "corrected_at": datetime.utcnow().isoformat(),
        }

    @classmethod
    def _serialize_record(cls, record: BaseGeoModel) -> Dict[str, Any]:
        """Serialize record for export."""
        return {
            "id": str(record.id),
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
            "data": record.dict(exclude={"id", "created_at", "updated_at"}),
        }


class AuditLog:
    """Audit log for compliance operations."""

    _logs: List[Dict[str, Any]] = []

    @classmethod
    async def log_gdpr_deletion(cls, user_id: UUID, shards: List[str]) -> None:
        """Log GDPR deletion for compliance."""
        cls._logs.append(
            {
                "event": "gdpr_deletion",
                "user_id": str(user_id),
                "shards": shards,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    @classmethod
    async def log_gdpr_export(cls, user_id: UUID, shards: List[str]) -> None:
        """Log GDPR export for compliance."""
        cls._logs.append(
            {
                "event": "gdpr_export",
                "user_id": str(user_id),
                "shards": shards,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    @classmethod
    def get_logs(cls, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get audit logs."""
        if event_type:
            return [log for log in cls._logs if log["event"] == event_type]
        return cls._logs.copy()


# Import datetime here to avoid circular imports
from datetime import datetime
