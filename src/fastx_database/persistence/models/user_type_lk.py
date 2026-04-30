"""User Type Lookup Model.

SQLAlchemy ORM model for user type codes (e.g. candidate, employer). Lookup
table referenced by user.user_type_id.

Uses LookupModelMixin for standard lookup table schema:
- id, urn, code, description, created_at, updated_at
- to_dict() serialization method

Usage:
    >>> from fastx_database.persistence.models.user_type_lk import UserTypeLk
    >>> # Seed data; code is used in business logic and APIs
"""

from fastx_database.core.constants.table import Table
from fastx_database.core.mixins import LookupModelMixin
from fastx_database.persistence.models import Base


class UserTypeLk(Base, LookupModelMixin):
    """Lookup: user type (e.g. candidate, employer).

    Attributes (from LookupModelMixin):
        id: Primary key.
        urn: Unique Resource Name.
        code: Unique code (e.g. "candidate", "employer").
        description: Human-readable label.
        created_at, updated_at: Timestamps.
    """

    __tablename__ = Table.USER_TYPE_LK
