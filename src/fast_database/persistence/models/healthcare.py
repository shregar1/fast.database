"""
Generic healthcare operations models (multi-domain).

Use for hospitals, clinics, telehealth, labs, imaging centers, payers’ care management,
or public-health programs. **PHI handling, consent, and regional regulation** belong in
application policy and security layers; these tables store **structural** identifiers
and workflow state only.

Usage:
    >>> from fast_database.persistence.models.healthcare import (
    ...     ClinicalEncounter,
    ...     ClinicalEncounterParticipant,
    ...     HealthcareFacility,
    ...     HealthcarePatient,
    ...     HealthcarePractitioner,
    ... )
"""

from __future__ import annotations

from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from fast_database.core.constants.table import Table
from fast_database.core.mixins import SoftDeleteMixin, TimestampMixin
from fast_database.persistence.models import Base


class HealthcareFacility(Base, TimestampMixin, SoftDeleteMixin):
    """
    A care delivery site: hospital campus, clinic, lab draw site, imaging center, ward, etc.

    ``facility_code`` is a **globally unique** stable key for routing and integrations.
    """

    __tablename__ = Table.HEALTHCARE_FACILITY

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    organization_id = Column(
        BigInteger,
        ForeignKey(f"{Table.ORGANIZATION}.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    facility_code = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(512), nullable=False)
    facility_type = Column(String(64), nullable=False, default="clinic", index=True)
    timezone = Column(String(64), nullable=True)
    country_code = Column(String(8), nullable=True)
    facility_metadata = Column("metadata", JSONB, nullable=True)


class HealthcarePatient(Base, TimestampMixin, SoftDeleteMixin):
    """
    A person receiving care within an organization’s namespace.

    ``patient_key`` is the tenant-scoped medical record / MPI key (not a global national id).
    Optional ``user_id`` links a portal or app account.
    """

    __tablename__ = Table.HEALTHCARE_PATIENT
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "patient_key",
            name="uq_healthcare_patient_org_key",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    organization_id = Column(
        BigInteger,
        ForeignKey(f"{Table.ORGANIZATION}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        BigInteger,
        ForeignKey(f"{Table.USER}.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    patient_key = Column(String(128), nullable=False, index=True)
    given_name = Column(String(256), nullable=True)
    family_name = Column(String(256), nullable=True)
    birth_date = Column(Date, nullable=True)
    administrative_gender = Column(String(32), nullable=True)
    patient_metadata = Column("metadata", JSONB, nullable=True)


class HealthcarePractitioner(Base, TimestampMixin, SoftDeleteMixin):
    """
    A licensed or credentialed care giver: physician, nurse, therapist, technician, etc.

    ``practitioner_key`` is stable within the organization (often tied to HR or NPI).
    """

    __tablename__ = Table.HEALTHCARE_PRACTITIONER
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "practitioner_key",
            name="uq_healthcare_practitioner_org_key",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    organization_id = Column(
        BigInteger,
        ForeignKey(f"{Table.ORGANIZATION}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        BigInteger,
        ForeignKey(f"{Table.USER}.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    practitioner_key = Column(String(128), nullable=False, index=True)
    display_name = Column(String(512), nullable=False)
    role_kind = Column(String(64), nullable=False, default="physician", index=True)
    specialty = Column(String(256), nullable=True, index=True)
    national_provider_id = Column(String(64), nullable=True, index=True)
    practitioner_metadata = Column("metadata", JSONB, nullable=True)


class ClinicalEncounter(Base, TimestampMixin, SoftDeleteMixin):
    """
    A clinical interaction: visit, admission episode, telehealth session, lab order encounter, etc.

    ``encounter_key`` is unique per facility (external visit number / CSN).
    """

    __tablename__ = Table.CLINICAL_ENCOUNTER
    __table_args__ = (
        UniqueConstraint(
            "facility_id",
            "encounter_key",
            name="uq_clinical_encounter_facility_key",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    patient_id = Column(
        BigInteger,
        ForeignKey(f"{Table.HEALTHCARE_PATIENT}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    facility_id = Column(
        BigInteger,
        ForeignKey(f"{Table.HEALTHCARE_FACILITY}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    encounter_key = Column(String(128), nullable=False, index=True)
    encounter_class = Column(String(64), nullable=False, default="ambulatory", index=True)
    status = Column(String(32), nullable=False, default="planned", index=True)
    period_start = Column(DateTime(timezone=True), nullable=True, index=True)
    period_end = Column(DateTime(timezone=True), nullable=True, index=True)
    chief_complaint = Column(Text, nullable=True)
    encounter_metadata = Column("metadata", JSONB, nullable=True)


class ClinicalEncounterParticipant(Base, TimestampMixin, SoftDeleteMixin):
    """
    Links a :class:`ClinicalEncounter` to a :class:`HealthcarePractitioner` with a role.

    Examples: attending, primary, consultant, assistant, referrer.
    """

    __tablename__ = Table.CLINICAL_ENCOUNTER_PARTICIPANT
    __table_args__ = (
        UniqueConstraint(
            "encounter_id",
            "practitioner_id",
            name="uq_clinical_encounter_participant_enc_pract",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    encounter_id = Column(
        BigInteger,
        ForeignKey(f"{Table.CLINICAL_ENCOUNTER}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    practitioner_id = Column(
        BigInteger,
        ForeignKey(f"{Table.HEALTHCARE_PRACTITIONER}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    participation_role = Column(String(64), nullable=False, default="attending", index=True)
    participant_metadata = Column("metadata", JSONB, nullable=True)
