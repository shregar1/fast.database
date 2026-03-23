"""
Repositories for generic industrial IoT: facilities, assets, devices, channels, samples.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from fast_database.core.soft_delete import filter_active
from fast_database.persistence.models.industrial_iot import (
    IndustrialAsset,
    IndustrialFacility,
    IndustrialIoTDevice,
    IndustrialTelemetryChannel,
    IndustrialTelemetrySample,
)
from fast_database.persistence.repositories.abstraction import IRepository


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class IndustrialFacilityRepository(IRepository):
    """Data access for :class:`~fast_database.persistence.models.industrial_iot.IndustrialFacility`."""

    def __init__(
        self,
        session: Session | None = None,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            cache=None,
            model=IndustrialFacility,
        )
        self._session = session

    @property
    def session(self) -> Session | None:
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        self._session = value

    def _active_query(self):
        q = self.session.query(IndustrialFacility)
        return filter_active(q, IndustrialFacility.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> IndustrialFacility | None:
        return self._active_query().filter(IndustrialFacility.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> IndustrialFacility | None:
        return self._active_query().filter(IndustrialFacility.urn == urn).first()

    def find_by_facility_code(self, facility_code: str) -> IndustrialFacility | None:
        return (
            self._active_query()
            .filter(IndustrialFacility.facility_code == facility_code)
            .first()
        )

    def list_by_organization(
        self,
        organization_id: int,
        *,
        skip: int = 0,
        limit: int = 200,
    ) -> list[IndustrialFacility]:
        return (
            self._active_query()
            .filter(IndustrialFacility.organization_id == organization_id)
            .order_by(IndustrialFacility.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_record(self, record: IndustrialFacility) -> IndustrialFacility:
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record


class IndustrialAssetRepository(IRepository):
    """Data access for :class:`~fast_database.persistence.models.industrial_iot.IndustrialAsset`."""

    def __init__(
        self,
        session: Session | None = None,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            cache=None,
            model=IndustrialAsset,
        )
        self._session = session

    @property
    def session(self) -> Session | None:
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        self._session = value

    def _active_query(self):
        q = self.session.query(IndustrialAsset)
        return filter_active(q, IndustrialAsset.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> IndustrialAsset | None:
        return self._active_query().filter(IndustrialAsset.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> IndustrialAsset | None:
        return self._active_query().filter(IndustrialAsset.urn == urn).first()

    def list_by_facility(
        self,
        facility_id: int,
        *,
        skip: int = 0,
        limit: int = 500,
    ) -> list[IndustrialAsset]:
        return (
            self._active_query()
            .filter(IndustrialAsset.facility_id == facility_id)
            .order_by(IndustrialAsset.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_children_of(
        self,
        parent_asset_id: int,
    ) -> list[IndustrialAsset]:
        return (
            self._active_query()
            .filter(IndustrialAsset.parent_asset_id == parent_asset_id)
            .order_by(IndustrialAsset.name.asc())
            .all()
        )

    def list_root_assets(
        self,
        facility_id: int,
    ) -> list[IndustrialAsset]:
        return (
            self._active_query()
            .filter(
                IndustrialAsset.facility_id == facility_id,
                IndustrialAsset.parent_asset_id.is_(None),
            )
            .order_by(IndustrialAsset.name.asc())
            .all()
        )

    def list_by_facility_and_kind(
        self,
        facility_id: int,
        asset_kind: str,
        *,
        skip: int = 0,
        limit: int = 200,
    ) -> list[IndustrialAsset]:
        return (
            self._active_query()
            .filter(
                IndustrialAsset.facility_id == facility_id,
                IndustrialAsset.asset_kind == asset_kind,
            )
            .order_by(IndustrialAsset.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_record(self, record: IndustrialAsset) -> IndustrialAsset:
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record


class IndustrialIoTDeviceRepository(IRepository):
    """Data access for :class:`~fast_database.persistence.models.industrial_iot.IndustrialIoTDevice`."""

    def __init__(
        self,
        session: Session | None = None,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            cache=None,
            model=IndustrialIoTDevice,
        )
        self._session = session

    @property
    def session(self) -> Session | None:
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        self._session = value

    def _active_query(self):
        q = self.session.query(IndustrialIoTDevice)
        return filter_active(q, IndustrialIoTDevice.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> IndustrialIoTDevice | None:
        return self._active_query().filter(IndustrialIoTDevice.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> IndustrialIoTDevice | None:
        return self._active_query().filter(IndustrialIoTDevice.urn == urn).first()

    def find_by_facility_and_device_key(
        self,
        facility_id: int,
        device_key: str,
    ) -> IndustrialIoTDevice | None:
        return (
            self._active_query()
            .filter(
                IndustrialIoTDevice.facility_id == facility_id,
                IndustrialIoTDevice.device_key == device_key,
            )
            .first()
        )

    def list_by_facility(
        self,
        facility_id: int,
        *,
        skip: int = 0,
        limit: int = 500,
    ) -> list[IndustrialIoTDevice]:
        return (
            self._active_query()
            .filter(IndustrialIoTDevice.facility_id == facility_id)
            .order_by(IndustrialIoTDevice.display_name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_asset(
        self,
        asset_id: int,
    ) -> list[IndustrialIoTDevice]:
        return (
            self._active_query()
            .filter(IndustrialIoTDevice.asset_id == asset_id)
            .order_by(IndustrialIoTDevice.display_name.asc())
            .all()
        )

    def create_record(self, record: IndustrialIoTDevice) -> IndustrialIoTDevice:
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record


class IndustrialTelemetryChannelRepository(IRepository):
    """Data access for :class:`~fast_database.persistence.models.industrial_iot.IndustrialTelemetryChannel`."""

    def __init__(
        self,
        session: Session | None = None,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            cache=None,
            model=IndustrialTelemetryChannel,
        )
        self._session = session

    @property
    def session(self) -> Session | None:
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        self._session = value

    def _active_query(self):
        q = self.session.query(IndustrialTelemetryChannel)
        return filter_active(q, IndustrialTelemetryChannel.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> IndustrialTelemetryChannel | None:
        return self._active_query().filter(IndustrialTelemetryChannel.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> IndustrialTelemetryChannel | None:
        return self._active_query().filter(IndustrialTelemetryChannel.urn == urn).first()

    def find_by_device_and_channel_key(
        self,
        device_id: int,
        channel_key: str,
    ) -> IndustrialTelemetryChannel | None:
        return (
            self._active_query()
            .filter(
                IndustrialTelemetryChannel.device_id == device_id,
                IndustrialTelemetryChannel.channel_key == channel_key,
            )
            .first()
        )

    def list_by_device(
        self,
        device_id: int,
    ) -> list[IndustrialTelemetryChannel]:
        return (
            self._active_query()
            .filter(IndustrialTelemetryChannel.device_id == device_id)
            .order_by(IndustrialTelemetryChannel.channel_key.asc())
            .all()
        )

    def create_record(self, record: IndustrialTelemetryChannel) -> IndustrialTelemetryChannel:
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record


class IndustrialTelemetrySampleRepository(IRepository):
    """Data access for :class:`~fast_database.persistence.models.industrial_iot.IndustrialTelemetrySample`."""

    def __init__(
        self,
        session: Session | None = None,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            cache=None,
            model=IndustrialTelemetrySample,
        )
        self._session = session

    @property
    def session(self) -> Session | None:
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        self._session = value

    def retrieve_record_by_id(self, record_id: int) -> IndustrialTelemetrySample | None:
        return (
            self.session.query(IndustrialTelemetrySample)
            .filter(IndustrialTelemetrySample.id == record_id)
            .first()
        )

    def retrieve_record_by_urn(self, urn: str) -> IndustrialTelemetrySample | None:
        return (
            self.session.query(IndustrialTelemetrySample)
            .filter(IndustrialTelemetrySample.urn == urn)
            .first()
        )

    def find_by_source_event_id(self, source_event_id: str) -> IndustrialTelemetrySample | None:
        if not source_event_id:
            return None
        return (
            self.session.query(IndustrialTelemetrySample)
            .filter(IndustrialTelemetrySample.source_event_id == source_event_id)
            .first()
        )

    def list_by_channel(
        self,
        channel_id: int,
        *,
        limit: int = 100,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[IndustrialTelemetrySample]:
        q = self.session.query(IndustrialTelemetrySample).filter(
            IndustrialTelemetrySample.channel_id == channel_id,
        )
        if since is not None:
            q = q.filter(IndustrialTelemetrySample.observed_at >= since)
        if until is not None:
            q = q.filter(IndustrialTelemetrySample.observed_at <= until)
        return (
            q.order_by(IndustrialTelemetrySample.observed_at.desc())
            .limit(limit)
            .all()
        )

    def latest_for_channel(self, channel_id: int) -> IndustrialTelemetrySample | None:
        return (
            self.session.query(IndustrialTelemetrySample)
            .filter(IndustrialTelemetrySample.channel_id == channel_id)
            .order_by(IndustrialTelemetrySample.observed_at.desc())
            .first()
        )

    def create_record(self, record: IndustrialTelemetrySample) -> IndustrialTelemetrySample:
        if record.ingested_at is None:
            record.ingested_at = _utc_now()
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record
