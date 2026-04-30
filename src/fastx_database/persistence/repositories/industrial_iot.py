"""Repositories for generic industrial IoT: facilities, assets, devices, channels, samples."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from fastx_database.core.constants.pagination import Pagination
from fastx_database.core.soft_delete import filter_active
from fastx_database.persistence.models.industrial_iot import (
    IndustrialAsset,
    IndustrialFacility,
    IndustrialIoTDevice,
    IndustrialTelemetryChannel,
    IndustrialTelemetrySample,
)
from fastx_database.persistence.repositories.abstraction import IRepository


def _utc_now() -> datetime:
    """Execute _utc_now operation.

    Returns:
        The result of the operation.
    """
    return datetime.now(timezone.utc)


class IndustrialFacilityRepository(IRepository):
    """Data access for :class:`~fastx_database.persistence.models.industrial_iot.IndustrialFacility`."""

    def __init__(
        self,
        session: Session | None = None,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            session: The session parameter.
            urn: The urn parameter.
            user_urn: The user_urn parameter.
            api_name: The api_name parameter.
            user_id: The user_id parameter.
        """
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
        """Execute session operation.

        Returns:
            The result of the operation.
        """
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        """Execute session operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._session = value

    def _active_query(self):
        """Execute _active_query operation.

        Returns:
            The result of the operation.
        """
        q = self.session.query(IndustrialFacility)
        return filter_active(q, IndustrialFacility.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> IndustrialFacility | None:
        """Execute retrieve_record_by_id operation.

        Args:
            record_id: The record_id parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(IndustrialFacility.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> IndustrialFacility | None:
        """Execute retrieve_record_by_urn operation.

        Args:
            urn: The urn parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(IndustrialFacility.urn == urn).first()

    def find_by_facility_code(self, facility_code: str) -> IndustrialFacility | None:
        """Execute find_by_facility_code operation.

        Args:
            facility_code: The facility_code parameter.

        Returns:
            The result of the operation.
        """
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
        limit: int = Pagination.LARGE_LIMIT,
    ) -> list[IndustrialFacility]:
        """Execute list_by_organization operation.

        Args:
            organization_id: The organization_id parameter.
            skip: The skip parameter.
            limit: The limit parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query()
            .filter(IndustrialFacility.organization_id == organization_id)
            .order_by(IndustrialFacility.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_record(self, record: IndustrialFacility) -> IndustrialFacility:
        """Execute create_record operation.

        Args:
            record: The record parameter.

        Returns:
            The result of the operation.
        """
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record


class IndustrialAssetRepository(IRepository):
    """Data access for :class:`~fastx_database.persistence.models.industrial_iot.IndustrialAsset`."""

    def __init__(
        self,
        session: Session | None = None,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            session: The session parameter.
            urn: The urn parameter.
            user_urn: The user_urn parameter.
            api_name: The api_name parameter.
            user_id: The user_id parameter.
        """
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
        """Execute session operation.

        Returns:
            The result of the operation.
        """
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        """Execute session operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._session = value

    def _active_query(self):
        """Execute _active_query operation.

        Returns:
            The result of the operation.
        """
        q = self.session.query(IndustrialAsset)
        return filter_active(q, IndustrialAsset.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> IndustrialAsset | None:
        """Execute retrieve_record_by_id operation.

        Args:
            record_id: The record_id parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(IndustrialAsset.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> IndustrialAsset | None:
        """Execute retrieve_record_by_urn operation.

        Args:
            urn: The urn parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(IndustrialAsset.urn == urn).first()

    def list_by_facility(
        self,
        facility_id: int,
        *,
        skip: int = 0,
        limit: int = Pagination.BULK_LIMIT,
    ) -> list[IndustrialAsset]:
        """Execute list_by_facility operation.

        Args:
            facility_id: The facility_id parameter.
            skip: The skip parameter.
            limit: The limit parameter.

        Returns:
            The result of the operation.
        """
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
        """Execute list_children_of operation.

        Args:
            parent_asset_id: The parent_asset_id parameter.

        Returns:
            The result of the operation.
        """
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
        """Execute list_root_assets operation.

        Args:
            facility_id: The facility_id parameter.

        Returns:
            The result of the operation.
        """
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
        limit: int = Pagination.LARGE_LIMIT,
    ) -> list[IndustrialAsset]:
        """Execute list_by_facility_and_kind operation.

        Args:
            facility_id: The facility_id parameter.
            asset_kind: The asset_kind parameter.
            skip: The skip parameter.
            limit: The limit parameter.

        Returns:
            The result of the operation.
        """
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
        """Execute create_record operation.

        Args:
            record: The record parameter.

        Returns:
            The result of the operation.
        """
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record


class IndustrialIoTDeviceRepository(IRepository):
    """Data access for :class:`~fastx_database.persistence.models.industrial_iot.IndustrialIoTDevice`."""

    def __init__(
        self,
        session: Session | None = None,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            session: The session parameter.
            urn: The urn parameter.
            user_urn: The user_urn parameter.
            api_name: The api_name parameter.
            user_id: The user_id parameter.
        """
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
        """Execute session operation.

        Returns:
            The result of the operation.
        """
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        """Execute session operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._session = value

    def _active_query(self):
        """Execute _active_query operation.

        Returns:
            The result of the operation.
        """
        q = self.session.query(IndustrialIoTDevice)
        return filter_active(q, IndustrialIoTDevice.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> IndustrialIoTDevice | None:
        """Execute retrieve_record_by_id operation.

        Args:
            record_id: The record_id parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(IndustrialIoTDevice.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> IndustrialIoTDevice | None:
        """Execute retrieve_record_by_urn operation.

        Args:
            urn: The urn parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(IndustrialIoTDevice.urn == urn).first()

    def find_by_facility_and_device_key(
        self,
        facility_id: int,
        device_key: str,
    ) -> IndustrialIoTDevice | None:
        """Execute find_by_facility_and_device_key operation.

        Args:
            facility_id: The facility_id parameter.
            device_key: The device_key parameter.

        Returns:
            The result of the operation.
        """
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
        limit: int = Pagination.BULK_LIMIT,
    ) -> list[IndustrialIoTDevice]:
        """Execute list_by_facility operation.

        Args:
            facility_id: The facility_id parameter.
            skip: The skip parameter.
            limit: The limit parameter.

        Returns:
            The result of the operation.
        """
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
        """Execute list_by_asset operation.

        Args:
            asset_id: The asset_id parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query()
            .filter(IndustrialIoTDevice.asset_id == asset_id)
            .order_by(IndustrialIoTDevice.display_name.asc())
            .all()
        )

    def create_record(self, record: IndustrialIoTDevice) -> IndustrialIoTDevice:
        """Execute create_record operation.

        Args:
            record: The record parameter.

        Returns:
            The result of the operation.
        """
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record


class IndustrialTelemetryChannelRepository(IRepository):
    """Data access for :class:`~fastx_database.persistence.models.industrial_iot.IndustrialTelemetryChannel`."""

    def __init__(
        self,
        session: Session | None = None,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            session: The session parameter.
            urn: The urn parameter.
            user_urn: The user_urn parameter.
            api_name: The api_name parameter.
            user_id: The user_id parameter.
        """
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
        """Execute session operation.

        Returns:
            The result of the operation.
        """
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        """Execute session operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._session = value

    def _active_query(self):
        """Execute _active_query operation.

        Returns:
            The result of the operation.
        """
        q = self.session.query(IndustrialTelemetryChannel)
        return filter_active(q, IndustrialTelemetryChannel.is_deleted)

    def retrieve_record_by_id(
        self, record_id: int
    ) -> IndustrialTelemetryChannel | None:
        """Execute retrieve_record_by_id operation.

        Args:
            record_id: The record_id parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query()
            .filter(IndustrialTelemetryChannel.id == record_id)
            .first()
        )

    def retrieve_record_by_urn(self, urn: str) -> IndustrialTelemetryChannel | None:
        """Execute retrieve_record_by_urn operation.

        Args:
            urn: The urn parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query().filter(IndustrialTelemetryChannel.urn == urn).first()
        )

    def find_by_device_and_channel_key(
        self,
        device_id: int,
        channel_key: str,
    ) -> IndustrialTelemetryChannel | None:
        """Execute find_by_device_and_channel_key operation.

        Args:
            device_id: The device_id parameter.
            channel_key: The channel_key parameter.

        Returns:
            The result of the operation.
        """
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
        """Execute list_by_device operation.

        Args:
            device_id: The device_id parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query()
            .filter(IndustrialTelemetryChannel.device_id == device_id)
            .order_by(IndustrialTelemetryChannel.channel_key.asc())
            .all()
        )

    def create_record(
        self, record: IndustrialTelemetryChannel
    ) -> IndustrialTelemetryChannel:
        """Execute create_record operation.

        Args:
            record: The record parameter.

        Returns:
            The result of the operation.
        """
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record


class IndustrialTelemetrySampleRepository(IRepository):
    """Data access for :class:`~fastx_database.persistence.models.industrial_iot.IndustrialTelemetrySample`."""

    def __init__(
        self,
        session: Session | None = None,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            session: The session parameter.
            urn: The urn parameter.
            user_urn: The user_urn parameter.
            api_name: The api_name parameter.
            user_id: The user_id parameter.
        """
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
        """Execute session operation.

        Returns:
            The result of the operation.
        """
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        """Execute session operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._session = value

    def retrieve_record_by_id(self, record_id: int) -> IndustrialTelemetrySample | None:
        """Execute retrieve_record_by_id operation.

        Args:
            record_id: The record_id parameter.

        Returns:
            The result of the operation.
        """
        return (
            self.session.query(IndustrialTelemetrySample)
            .filter(IndustrialTelemetrySample.id == record_id)
            .first()
        )

    def retrieve_record_by_urn(self, urn: str) -> IndustrialTelemetrySample | None:
        """Execute retrieve_record_by_urn operation.

        Args:
            urn: The urn parameter.

        Returns:
            The result of the operation.
        """
        return (
            self.session.query(IndustrialTelemetrySample)
            .filter(IndustrialTelemetrySample.urn == urn)
            .first()
        )

    def find_by_source_event_id(
        self, source_event_id: str
    ) -> IndustrialTelemetrySample | None:
        """Execute find_by_source_event_id operation.

        Args:
            source_event_id: The source_event_id parameter.

        Returns:
            The result of the operation.
        """
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
        limit: int = Pagination.DEFAULT_LIMIT,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[IndustrialTelemetrySample]:
        """Execute list_by_channel operation.

        Args:
            channel_id: The channel_id parameter.
            limit: The limit parameter.
            since: The since parameter.
            until: The until parameter.

        Returns:
            The result of the operation.
        """
        q = self.session.query(IndustrialTelemetrySample).filter(
            IndustrialTelemetrySample.channel_id == channel_id,
        )
        if since is not None:
            q = q.filter(IndustrialTelemetrySample.observed_at >= since)
        if until is not None:
            q = q.filter(IndustrialTelemetrySample.observed_at <= until)
        return (
            q.order_by(IndustrialTelemetrySample.observed_at.desc()).limit(limit).all()
        )

    def latest_for_channel(self, channel_id: int) -> IndustrialTelemetrySample | None:
        """Execute latest_for_channel operation.

        Args:
            channel_id: The channel_id parameter.

        Returns:
            The result of the operation.
        """
        return (
            self.session.query(IndustrialTelemetrySample)
            .filter(IndustrialTelemetrySample.channel_id == channel_id)
            .order_by(IndustrialTelemetrySample.observed_at.desc())
            .first()
        )

    def create_record(
        self, record: IndustrialTelemetrySample
    ) -> IndustrialTelemetrySample:
        """Execute create_record operation.

        Args:
            record: The record parameter.

        Returns:
            The result of the operation.
        """
        if record.ingested_at is None:
            record.ingested_at = _utc_now()
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record
