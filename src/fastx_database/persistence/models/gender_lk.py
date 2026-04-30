"""Gender Lookup Model.

SQLAlchemy ORM model for gender options (e.g. Male, Female, Non-binary).
Referenced by profile.gender_id.

Uses LookupModelMixin for standard lookup table schema:
- id, urn, code, description, created_at, updated_at
- to_dict() serialization method

Note: This model uses code length of 32 instead of the default 64.

Usage:
    >>> from fastx_database.persistence.models.gender_lk import GenderLk
    >>> # Used in profile for user's gender
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String

from fastx_database.core.constants.table import Table
from fastx_database.core.mixins import LookupModelMixin
from fastx_database.persistence.models import Base


class GenderLk(Base, LookupModelMixin):
    """Lookup: gender (e.g. Male, Female, Non-binary).

    Attributes (from LookupModelMixin, with code length 32):
        id: Primary key.
        urn: Unique Resource Name.
        code: Unique code (32 chars).
        description: Human-readable label.
        created_at, updated_at: Timestamps.
    """

    __tablename__ = Table.GENDER_LK

    # Override the code column with different length
    code = Column(String(32), nullable=False, unique=True, index=True)
