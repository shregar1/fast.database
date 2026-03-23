"""
Repositories for generic healthcare: facilities, patients, practitioners, encounters.
"""

from __future__ import annotations

from sqlalchemy import nulls_last
from sqlalchemy.orm import Session

from fast_database.core.soft_delete import filter_active
from fast_database.persistence.models.healthcare import (
    ClinicalEncounter,
    ClinicalEncounterParticipant,
    HealthcareFacility,
    HealthcarePatient,
    HealthcarePractitioner,
)
from fast_database.persistence.repositories.abstraction import IRepository


class HealthcareFacilityRepository(IRepository):
    """Data access for :class:`~fast_database.persistence.models.healthcare.HealthcareFacility`."""

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
            model=HealthcareFacility,
        )
        self._session = session

    @property
    def session(self) -> Session | None:
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        self._session = value

    def _active_query(self):
        q = self.session.query(HealthcareFacility)
        return filter_active(q, HealthcareFacility.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> HealthcareFacility | None:
        return self._active_query().filter(HealthcareFacility.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> HealthcareFacility | None:
        return self._active_query().filter(HealthcareFacility.urn == urn).first()

    def find_by_facility_code(self, facility_code: str) -> HealthcareFacility | None:
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
        limit: int = 200,
    ) -> list[HealthcareFacility]:
        return (
            self._active_query()
            .filter(HealthcareFacility.organization_id == organization_id)
            .order_by(HealthcareFacility.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_record(self, record: HealthcareFacility) -> HealthcareFacility:
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record


class HealthcarePatientRepository(IRepository):
    """Data access for :class:`~fast_database.persistence.models.healthcare.HealthcarePatient`."""

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
            model=HealthcarePatient,
        )
        self._session = session

    @property
    def session(self) -> Session | None:
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        self._session = value

    def _active_query(self):
        q = self.session.query(HealthcarePatient)
        return filter_active(q, HealthcarePatient.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> HealthcarePatient | None:
        return self._active_query().filter(HealthcarePatient.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> HealthcarePatient | None:
        return self._active_query().filter(HealthcarePatient.urn == urn).first()

    def find_by_organization_and_patient_key(
        self,
        organization_id: int,
        patient_key: str,
    ) -> HealthcarePatient | None:
        return (
            self._active_query()
            .filter(
                HealthcarePatient.organization_id == organization_id,
                HealthcarePatient.patient_key == patient_key,
            )
            .first()
        )

    def find_by_user_id(self, user_id: int) -> HealthcarePatient | None:
        return (
            self._active_query()
            .filter(HealthcarePatient.user_id == user_id)
            .first()
        )

    def list_by_organization(
        self,
        organization_id: int,
        *,
        skip: int = 0,
        limit: int = 200,
    ) -> list[HealthcarePatient]:
        return (
            self._active_query()
            .filter(HealthcarePatient.organization_id == organization_id)
            .order_by(HealthcarePatient.family_name.asc(), HealthcarePatient.given_name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_record(self, record: HealthcarePatient) -> HealthcarePatient:
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record


class HealthcarePractitionerRepository(IRepository):
    """Data access for :class:`~fast_database.persistence.models.healthcare.HealthcarePractitioner`."""

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
            model=HealthcarePractitioner,
        )
        self._session = session

    @property
    def session(self) -> Session | None:
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        self._session = value

    def _active_query(self):
        q = self.session.query(HealthcarePractitioner)
        return filter_active(q, HealthcarePractitioner.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> HealthcarePractitioner | None:
        return self._active_query().filter(HealthcarePractitioner.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> HealthcarePractitioner | None:
        return self._active_query().filter(HealthcarePractitioner.urn == urn).first()

    def find_by_organization_and_practitioner_key(
        self,
        organization_id: int,
        practitioner_key: str,
    ) -> HealthcarePractitioner | None:
        return (
            self._active_query()
            .filter(
                HealthcarePractitioner.organization_id == organization_id,
                HealthcarePractitioner.practitioner_key == practitioner_key,
            )
            .first()
        )

    def find_by_national_provider_id(self, npi: str) -> HealthcarePractitioner | None:
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
        limit: int = 200,
    ) -> list[HealthcarePractitioner]:
        return (
            self._active_query()
            .filter(HealthcarePractitioner.organization_id == organization_id)
            .order_by(HealthcarePractitioner.display_name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_record(self, record: HealthcarePractitioner) -> HealthcarePractitioner:
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record


class ClinicalEncounterRepository(IRepository):
    """Data access for :class:`~fast_database.persistence.models.healthcare.ClinicalEncounter`."""

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
            model=ClinicalEncounter,
        )
        self._session = session

    @property
    def session(self) -> Session | None:
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        self._session = value

    def _active_query(self):
        q = self.session.query(ClinicalEncounter)
        return filter_active(q, ClinicalEncounter.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> ClinicalEncounter | None:
        return self._active_query().filter(ClinicalEncounter.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> ClinicalEncounter | None:
        return self._active_query().filter(ClinicalEncounter.urn == urn).first()

    def find_by_facility_and_encounter_key(
        self,
        facility_id: int,
        encounter_key: str,
    ) -> ClinicalEncounter | None:
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
        limit: int = 100,
    ) -> list[ClinicalEncounter]:
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
        limit: int = 200,
    ) -> list[ClinicalEncounter]:
        return (
            self._active_query()
            .filter(ClinicalEncounter.facility_id == facility_id)
            .order_by(nulls_last(ClinicalEncounter.period_start.desc()))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_record(self, record: ClinicalEncounter) -> ClinicalEncounter:
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record


class ClinicalEncounterParticipantRepository(IRepository):
    """Data access for :class:`~fast_database.persistence.models.healthcare.ClinicalEncounterParticipant`."""

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
            model=ClinicalEncounterParticipant,
        )
        self._session = session

    @property
    def session(self) -> Session | None:
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        self._session = value

    def _active_query(self):
        q = self.session.query(ClinicalEncounterParticipant)
        return filter_active(q, ClinicalEncounterParticipant.is_deleted)

    def retrieve_record_by_id(self, record_id: int) -> ClinicalEncounterParticipant | None:
        return self._active_query().filter(ClinicalEncounterParticipant.id == record_id).first()

    def retrieve_record_by_urn(self, urn: str) -> ClinicalEncounterParticipant | None:
        return self._active_query().filter(ClinicalEncounterParticipant.urn == urn).first()

    def find_by_encounter_and_practitioner(
        self,
        encounter_id: int,
        practitioner_id: int,
    ) -> ClinicalEncounterParticipant | None:
        return (
            self._active_query()
            .filter(
                ClinicalEncounterParticipant.encounter_id == encounter_id,
                ClinicalEncounterParticipant.practitioner_id == practitioner_id,
            )
            .first()
        )

    def list_by_encounter(self, encounter_id: int) -> list[ClinicalEncounterParticipant]:
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
        limit: int = 200,
    ) -> list[ClinicalEncounterParticipant]:
        return (
            self._active_query()
            .filter(ClinicalEncounterParticipant.practitioner_id == practitioner_id)
            .order_by(ClinicalEncounterParticipant.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_record(self, record: ClinicalEncounterParticipant) -> ClinicalEncounterParticipant:
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record
