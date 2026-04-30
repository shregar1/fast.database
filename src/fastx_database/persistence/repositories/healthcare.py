"""Repositories for generic healthcare: facilities, patients, practitioners, encounters."""

from __future__ import annotations

from sqlalchemy import nulls_last
from sqlalchemy.orm import Session

from fastx_database.core.constants.pagination import Pagination
from fastx_database.core.soft_delete import filter_active
from fastx_database.persistence.models.healthcare import (
    ClinicalEncounter,
    ClinicalEncounterParticipant,
    HealthcareFacility,
    HealthcarePatient,
    HealthcarePractitioner,
)
from fastx_database.persistence.repositories.abstraction import IRepository


class HealthcareFacilityRepository(IRepository):
    """Data access for :class:`~fastx_database.persistence.models.healthcare.HealthcareFacility`."""

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
            model=HealthcareFacility,
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
        q = self.session.query(HealthcareFacility)
        return filter_active(q, HealthcareFacility.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> HealthcareFacility | None:
        """Execute retrieve_record_by_id operation.

        Args:
            record_id: The record_id parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(HealthcareFacility.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> HealthcareFacility | None:
        """Execute retrieve_record_by_urn operation.

        Args:
            urn: The urn parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(HealthcareFacility.urn == urn).first()

    def find_by_facility_code(self, facility_code: str) -> HealthcareFacility | None:
        """Execute find_by_facility_code operation.

        Args:
            facility_code: The facility_code parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query()
            .filter(HealthcareFacility.facility_code == facility_code)
            .first()
        )

    def list_by_organization(
        self,
        organization_id: int,
        *,
        skip: int = 0,
        limit: int = Pagination.LARGE_LIMIT,
    ) -> list[HealthcareFacility]:
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
            .filter(HealthcareFacility.organization_id == organization_id)
            .order_by(HealthcareFacility.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_record(self, record: HealthcareFacility) -> HealthcareFacility:
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


class HealthcarePatientRepository(IRepository):
    """Data access for :class:`~fastx_database.persistence.models.healthcare.HealthcarePatient`."""

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
            model=HealthcarePatient,
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
        q = self.session.query(HealthcarePatient)
        return filter_active(q, HealthcarePatient.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> HealthcarePatient | None:
        """Execute retrieve_record_by_id operation.

        Args:
            record_id: The record_id parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(HealthcarePatient.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> HealthcarePatient | None:
        """Execute retrieve_record_by_urn operation.

        Args:
            urn: The urn parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(HealthcarePatient.urn == urn).first()

    def find_by_organization_and_patient_key(
        self,
        organization_id: int,
        patient_key: str,
    ) -> HealthcarePatient | None:
        """Execute find_by_organization_and_patient_key operation.

        Args:
            organization_id: The organization_id parameter.
            patient_key: The patient_key parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query()
            .filter(
                HealthcarePatient.organization_id == organization_id,
                HealthcarePatient.patient_key == patient_key,
            )
            .first()
        )

    def find_by_user_id(self, user_id: int) -> HealthcarePatient | None:
        """Execute find_by_user_id operation.

        Args:
            user_id: The user_id parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(HealthcarePatient.user_id == user_id).first()

    def list_by_organization(
        self,
        organization_id: int,
        *,
        skip: int = 0,
        limit: int = Pagination.LARGE_LIMIT,
    ) -> list[HealthcarePatient]:
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
            .filter(HealthcarePatient.organization_id == organization_id)
            .order_by(
                HealthcarePatient.family_name.asc(), HealthcarePatient.given_name.asc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_record(self, record: HealthcarePatient) -> HealthcarePatient:
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


class HealthcarePractitionerRepository(IRepository):
    """Data access for :class:`~fastx_database.persistence.models.healthcare.HealthcarePractitioner`."""

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
            model=HealthcarePractitioner,
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
        q = self.session.query(HealthcarePractitioner)
        return filter_active(q, HealthcarePractitioner.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> HealthcarePractitioner | None:
        """Execute retrieve_record_by_id operation.

        Args:
            record_id: The record_id parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query().filter(HealthcarePractitioner.id == record_id).first()
        )

    def retrieve_record_by_urn(self, urn: str) -> HealthcarePractitioner | None:
        """Execute retrieve_record_by_urn operation.

        Args:
            urn: The urn parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(HealthcarePractitioner.urn == urn).first()

    def find_by_organization_and_practitioner_key(
        self,
        organization_id: int,
        practitioner_key: str,
    ) -> HealthcarePractitioner | None:
        """Execute find_by_organization_and_practitioner_key operation.

        Args:
            organization_id: The organization_id parameter.
            practitioner_key: The practitioner_key parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query()
            .filter(
                HealthcarePractitioner.organization_id == organization_id,
                HealthcarePractitioner.practitioner_key == practitioner_key,
            )
            .first()
        )

    def find_by_national_provider_id(self, npi: str) -> HealthcarePractitioner | None:
        """Execute find_by_national_provider_id operation.

        Args:
            npi: The npi parameter.

        Returns:
            The result of the operation.
        """
        if not npi:
            return None
        return (
            self._active_query()
            .filter(HealthcarePractitioner.national_provider_id == npi)
            .first()
        )

    def list_by_organization(
        self,
        organization_id: int,
        *,
        skip: int = 0,
        limit: int = Pagination.LARGE_LIMIT,
    ) -> list[HealthcarePractitioner]:
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
            .filter(HealthcarePractitioner.organization_id == organization_id)
            .order_by(HealthcarePractitioner.display_name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_record(self, record: HealthcarePractitioner) -> HealthcarePractitioner:
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


class ClinicalEncounterRepository(IRepository):
    """Data access for :class:`~fastx_database.persistence.models.healthcare.ClinicalEncounter`."""

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
            model=ClinicalEncounter,
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
        q = self.session.query(ClinicalEncounter)
        return filter_active(q, ClinicalEncounter.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> ClinicalEncounter | None:
        """Execute retrieve_record_by_id operation.

        Args:
            record_id: The record_id parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(ClinicalEncounter.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> ClinicalEncounter | None:
        """Execute retrieve_record_by_urn operation.

        Args:
            urn: The urn parameter.

        Returns:
            The result of the operation.
        """
        return self._active_query().filter(ClinicalEncounter.urn == urn).first()

    def find_by_facility_and_encounter_key(
        self,
        facility_id: int,
        encounter_key: str,
    ) -> ClinicalEncounter | None:
        """Execute find_by_facility_and_encounter_key operation.

        Args:
            facility_id: The facility_id parameter.
            encounter_key: The encounter_key parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query()
            .filter(
                ClinicalEncounter.facility_id == facility_id,
                ClinicalEncounter.encounter_key == encounter_key,
            )
            .first()
        )

    def list_by_patient(
        self,
        patient_id: int,
        *,
        skip: int = 0,
        limit: int = Pagination.DEFAULT_LIMIT,
    ) -> list[ClinicalEncounter]:
        """Execute list_by_patient operation.

        Args:
            patient_id: The patient_id parameter.
            skip: The skip parameter.
            limit: The limit parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query()
            .filter(ClinicalEncounter.patient_id == patient_id)
            .order_by(nulls_last(ClinicalEncounter.period_start.desc()))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_facility(
        self,
        facility_id: int,
        *,
        skip: int = 0,
        limit: int = Pagination.LARGE_LIMIT,
    ) -> list[ClinicalEncounter]:
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
            .filter(ClinicalEncounter.facility_id == facility_id)
            .order_by(nulls_last(ClinicalEncounter.period_start.desc()))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_record(self, record: ClinicalEncounter) -> ClinicalEncounter:
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


class ClinicalEncounterParticipantRepository(IRepository):
    """Data access for :class:`~fastx_database.persistence.models.healthcare.ClinicalEncounterParticipant`."""

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
            model=ClinicalEncounterParticipant,
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
        q = self.session.query(ClinicalEncounterParticipant)
        return filter_active(q, ClinicalEncounterParticipant.is_deleted)

    def retrieve_record_by_id(
        self, record_id: int
    ) -> ClinicalEncounterParticipant | None:
        """Execute retrieve_record_by_id operation.

        Args:
            record_id: The record_id parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query()
            .filter(ClinicalEncounterParticipant.id == record_id)
            .first()
        )

    def retrieve_record_by_urn(self, urn: str) -> ClinicalEncounterParticipant | None:
        """Execute retrieve_record_by_urn operation.

        Args:
            urn: The urn parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query().filter(ClinicalEncounterParticipant.urn == urn).first()
        )

    def find_by_encounter_and_practitioner(
        self,
        encounter_id: int,
        practitioner_id: int,
    ) -> ClinicalEncounterParticipant | None:
        """Execute find_by_encounter_and_practitioner operation.

        Args:
            encounter_id: The encounter_id parameter.
            practitioner_id: The practitioner_id parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query()
            .filter(
                ClinicalEncounterParticipant.encounter_id == encounter_id,
                ClinicalEncounterParticipant.practitioner_id == practitioner_id,
            )
            .first()
        )

    def list_by_encounter(
        self, encounter_id: int
    ) -> list[ClinicalEncounterParticipant]:
        """Execute list_by_encounter operation.

        Args:
            encounter_id: The encounter_id parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query()
            .filter(ClinicalEncounterParticipant.encounter_id == encounter_id)
            .order_by(ClinicalEncounterParticipant.participation_role.asc())
            .all()
        )

    def list_by_practitioner(
        self,
        practitioner_id: int,
        *,
        skip: int = 0,
        limit: int = Pagination.LARGE_LIMIT,
    ) -> list[ClinicalEncounterParticipant]:
        """Execute list_by_practitioner operation.

        Args:
            practitioner_id: The practitioner_id parameter.
            skip: The skip parameter.
            limit: The limit parameter.

        Returns:
            The result of the operation.
        """
        return (
            self._active_query()
            .filter(ClinicalEncounterParticipant.practitioner_id == practitioner_id)
            .order_by(ClinicalEncounterParticipant.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_record(
        self, record: ClinicalEncounterParticipant
    ) -> ClinicalEncounterParticipant:
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
