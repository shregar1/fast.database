"""Organization and Membership Repositories.

Data access for Organization, OrganizationInvite, and OrganizationMember.
OrganizationRepository: create org, get_by_id, get_by_urn, list_by_owner.
OrganizationMemberRepository: add member, get role, list members, remove.
OrganizationInviteRepository: create invite, get by token, list pending, accept/revoke.
All extend :class:`~fastx_database.persistence.repositories.repository.IRepository`. Used by org and invite flows.

Usage:
    >>> from fastx_database.persistence.repositories.organization import OrganizationRepository, OrganizationMemberRepository
    >>> org_repo = OrganizationRepository(session=db_session)
    >>> org = org_repo.create(urn="urn:org:1", name="Acme", owner_id=1)
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from fastx_database.persistence.repositories.abstraction import IRepository
from fastx_database.persistence.models.organization import (
    Organization,
    OrganizationInvite,
    OrganizationMember,
)


class OrganizationRepository(IRepository):
    """Repository for Organization (tenant/org) CRUD and lookup.

    Methods:
        create: Create organization (urn, name, owner_id, optional slug).
        get_by_id, get_by_urn: Lookup by id or urn.
        list_by_owner: List organizations owned by user.

    """

    def __init__(
        self,
        session: Session | None = None,
        *,
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
            model=Organization,
            cache=None,
        )
        self._session = session
        if not self._session:
            raise RuntimeError("DB session not found")

    @property
    def session(self) -> Session:
        """Execute session operation.

        Returns:
            The result of the operation.
        """
        return self._session

    def create(
        self, urn: str, name: str, owner_id: int, slug: str | None = None
    ) -> Organization:
        """Execute create operation.

        Args:
            urn: The urn parameter.
            name: The name parameter.
            owner_id: The owner_id parameter.
            slug: The slug parameter.

        Returns:
            The result of the operation.
        """
        now = datetime.now(timezone.utc)
        org = Organization(
            urn=urn, name=name, owner_id=owner_id, slug=slug, created_at=now
        )
        self.session.add(org)
        self.session.commit()
        self.session.refresh(org)

        return org

    def get_by_id(self, org_id: int) -> Organization | None:
        """Execute get_by_id operation.

        Args:
            org_id: The org_id parameter.

        Returns:
            The result of the operation.
        """
        return (
            self.session.query(Organization).filter(Organization.id == org_id).first()
        )

    def get_by_urn(self, urn: str) -> Organization | None:
        """Execute get_by_urn operation.

        Args:
            urn: The urn parameter.

        Returns:
            The result of the operation.
        """
        return self.session.query(Organization).filter(Organization.urn == urn).first()

    def list_by_owner(self, owner_id: int) -> list[Organization]:
        """Execute list_by_owner operation.

        Args:
            owner_id: The owner_id parameter.

        Returns:
            The result of the operation.
        """
        return list(
            self.session.query(Organization)
            .filter(Organization.owner_id == owner_id)
            .all()
        )


class OrganizationMemberRepository(IRepository):
    """Repository for OrganizationMember (user–org role) and membership operations.

    Methods: add member with role, get member by org and user, list members for org,
    remove member. Used for org membership and role checks.
    """

    def __init__(
        self,
        session: Session | None = None,
        *,
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
            model=OrganizationMember,
            cache=None,
        )
        self._session = session
        if not self._session:
            raise RuntimeError("DB session not found")

    @property
    def session(self) -> Session:
        """Execute session operation.

        Returns:
            The result of the operation.
        """
        return self._session

    def add(self, organization_id: int, user_id: int, role: str) -> OrganizationMember:
        """Execute add operation.

        Args:
            organization_id: The organization_id parameter.
            user_id: The user_id parameter.
            role: The role parameter.

        Returns:
            The result of the operation.
        """
        rec = OrganizationMember(
            organization_id=organization_id, user_id=user_id, role=role
        )
        self.session.add(rec)
        self.session.commit()
        self.session.refresh(rec)

        return rec

    def get(self, organization_id: int, user_id: int) -> OrganizationMember | None:
        """Execute get operation.

        Args:
            organization_id: The organization_id parameter.
            user_id: The user_id parameter.

        Returns:
            The result of the operation.
        """
        return (
            self.session.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
            )
            .first()
        )

    def list_by_organization(self, organization_id: int) -> list[OrganizationMember]:
        """Execute list_by_organization operation.

        Args:
            organization_id: The organization_id parameter.

        Returns:
            The result of the operation.
        """
        return list(
            self.session.query(OrganizationMember)
            .filter(OrganizationMember.organization_id == organization_id)
            .all()
        )

    def list_by_user(self, user_id: int) -> list[OrganizationMember]:
        """Execute list_by_user operation.

        Args:
            user_id: The user_id parameter.

        Returns:
            The result of the operation.
        """
        return list(
            self.session.query(OrganizationMember)
            .filter(OrganizationMember.user_id == user_id)
            .all()
        )

    def remove(self, organization_id: int, user_id: int) -> bool:
        """Execute remove operation.

        Args:
            organization_id: The organization_id parameter.
            user_id: The user_id parameter.

        Returns:
            The result of the operation.
        """
        rec = self.get(organization_id, user_id)
        if not rec:
            return False
        self.session.delete(rec)

        self.session.commit()

        return True

    def set_role(self, organization_id: int, user_id: int, role: str) -> bool:
        """Execute set_role operation.

        Args:
            organization_id: The organization_id parameter.
            user_id: The user_id parameter.
            role: The role parameter.

        Returns:
            The result of the operation.
        """
        rec = self.get(organization_id, user_id)
        if not rec:
            return False
        rec.role = role

        self.session.commit()
        self.session.refresh(rec)

        return True


class OrganizationInviteRepository(IRepository):
    """Repository for OrganizationInvite (pending invites by token/email).

    Methods: create invite (org, email, role, token, invited_by, expires_at),
    get_by_token, list_pending_by_organization, mark_accepted, revoke. Used by
    invite flow and accept/revoke endpoints.
    """

    def __init__(
        self,
        session: Session | None = None,
        *,
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
            model=OrganizationInvite,
            cache=None,
        )
        self._session = session
        if not self._session:
            raise RuntimeError("DB session not found")

    @property
    def session(self) -> Session:
        """Execute session operation.

        Returns:
            The result of the operation.
        """
        return self._session

    def create(
        self,
        organization_id: int,
        email: str,
        role: str,
        token: str,
        invited_by_id: int,
        expires_at: datetime,
    ) -> OrganizationInvite:
        """Execute create operation.

        Args:
            organization_id: The organization_id parameter.
            email: The email parameter.
            role: The role parameter.
            token: The token parameter.
            invited_by_id: The invited_by_id parameter.
            expires_at: The expires_at parameter.

        Returns:
            The result of the operation.
        """
        rec = OrganizationInvite(
            organization_id=organization_id,
            email=email,
            role=role,
            token=token,
            invited_by_id=invited_by_id,
            expires_at=expires_at,
        )
        self.session.add(rec)
        self.session.commit()
        self.session.refresh(rec)

        return rec

    def get_by_token(self, token: str) -> OrganizationInvite | None:
        """Execute get_by_token operation.

        Args:
            token: The token parameter.

        Returns:
            The result of the operation.
        """
        return (
            self.session.query(OrganizationInvite)
            .filter(OrganizationInvite.token == token)
            .first()
        )

    def list_pending_by_organization(
        self, organization_id: int
    ) -> list[OrganizationInvite]:
        """Execute list_pending_by_organization operation.

        Args:
            organization_id: The organization_id parameter.

        Returns:
            The result of the operation.
        """
        now = datetime.now(timezone.utc)

        return list(
            self.session.query(OrganizationInvite)
            .filter(
                OrganizationInvite.organization_id == organization_id,
                OrganizationInvite.accepted_at.is_(None),
                OrganizationInvite.expires_at > now,
            )
            .all()
        )

    def mark_accepted(self, invite_id: int) -> bool:
        """Execute mark_accepted operation.

        Args:
            invite_id: The invite_id parameter.

        Returns:
            The result of the operation.
        """
        rec = (
            self.session.query(OrganizationInvite)
            .filter(OrganizationInvite.id == invite_id)
            .first()
        )
        if not rec:
            return False
        rec.accepted_at = datetime.now(timezone.utc)

        self.session.commit()

        return True

    def delete(self, invite_id: int, organization_id: int) -> bool:
        """Execute delete operation.

        Args:
            invite_id: The invite_id parameter.
            organization_id: The organization_id parameter.

        Returns:
            The result of the operation.
        """
        rec = (
            self.session.query(OrganizationInvite)
            .filter(
                OrganizationInvite.id == invite_id,
                OrganizationInvite.organization_id == organization_id,
            )
            .first()
        )
        if not rec:
            return False
        self.session.delete(rec)

        self.session.commit()

        return True
