"""
Organization and membership models.

SQLAlchemy ORM models for organizations (workspaces), organization members,
and pending invites. Referenced by document.organization_id and subscription.organization_id.

Usage:
    >>> from fast_database.models.organization import Organization, OrganizationMember, OrganizationInvite
"""




from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String

from fast_database.constants.table import Table
from fast_database.models import Base


class Organization(Base):
    """
    Organization (tenant/workspace) with an owner.

    Attributes:
        id: Primary key.
        urn: Unique Resource Name.
        name: Display name.
        owner_id: FK to user (owner).
        slug: Optional URL-friendly slug.
        created_at: When the org was created.
    """




    __tablename__ = Table.ORGANIZATION

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    owner_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    slug = Column(String(64), nullable=True, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "urn": self.urn,
            "name": self.name,
            "owner_id": self.owner_id,
            "slug": self.slug,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class OrganizationMember(Base):
    """
    User–organization membership with role.

    Attributes:
        id: Primary key.
        organization_id: FK to organizations.
        user_id: FK to user.
        role: Role (e.g. owner, admin, member).
    """




    __tablename__ = Table.ORGANIZATION_MEMBER

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    organization_id = Column(
        BigInteger,
        ForeignKey(Table.ORGANIZATION + ".id"),
        nullable=False,
        index=True,
    )
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    role = Column(String(32), nullable=False, index=True)


class OrganizationInvite(Base):
    """
    Pending invite to an organization (by email, token, role).

    Attributes:
        id: Primary key.
        organization_id: FK to organizations.
        email: Invitee email.
        role: Role to assign on accept.
        token: Unique token for accept link.
        invited_by_id: FK to user.
        expires_at: When the invite expires.
        accepted_at: Set when accepted (null until then).
    """




    __tablename__ = Table.ORGANIZATION_INVITE

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    organization_id = Column(
        BigInteger,
        ForeignKey(Table.ORGANIZATION + ".id"),
        nullable=False,
        index=True,
    )
    email = Column(String(255), nullable=False, index=True)
    role = Column(String(32), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True, index=True)
    invited_by_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "email": self.email,
            "role": self.role,
            "token": self.token,
            "invited_by_id": self.invited_by_id,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
        }
