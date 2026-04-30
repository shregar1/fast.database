"""Mixin column wiring."""

from __future__ import annotations

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session, declared_attr, sessionmaker

from fastx_database.persistence.models import Base
from fastx_database.core.mixins import (
    AuditActorMixin,
    OptimisticLockMixin,
    OrganizationScopedMixin,
    TenantIdMixin,
)


def test_tenant_id_mixin_columns():
    """Execute test_tenant_id_mixin_columns operation.

    Returns:
        The result of the operation.
    """

    class T(Base, TenantIdMixin):
        """Represents the T class."""

        __tablename__ = "t_tenant"
        id = Column(Integer, primary_key=True)

    assert "tenant_id" in T.__table__.c


def test_organization_scoped_mixin_fk():
    """Execute test_organization_scoped_mixin_fk operation.

    Returns:
        The result of the operation.
    """

    class O(Base, OrganizationScopedMixin):
        """Represents the O class."""

        __tablename__ = "t_org_scoped"
        id = Column(Integer, primary_key=True)

    fk = list(O.__table__.c.organization_id.foreign_keys)[0]
    assert "organizations" in str(fk._colspec)


def test_audit_actor_mixin_fk():
    """Execute test_audit_actor_mixin_fk operation.

    Returns:
        The result of the operation.
    """

    class A(Base, AuditActorMixin):
        """Represents the A class."""

        __tablename__ = "t_audit"
        id = Column(Integer, primary_key=True)

    assert "created_by_id" in A.__table__.c
    assert "updated_by_id" in A.__table__.c


def test_optimistic_lock_version_mapper():
    """Execute test_optimistic_lock_version_mapper operation.

    Returns:
        The result of the operation.
    """

    class V(Base, OptimisticLockMixin):
        """Represents the V class."""

        __tablename__ = "t_versioned"
        id = Column(Integer, primary_key=True)
        name = Column(String(32), nullable=False)

        @declared_attr
        def __mapper_args__(cls):  # noqa: N805 — SQLAlchemy class API
            """Execute __mapper_args__ operation.

            Returns:
                The result of the operation.
            """
            return {"version_id_col": cls.version}

    from sqlalchemy import create_engine

    engine = create_engine("sqlite:///:memory:")
    V.__table__.create(engine)
    Session_ = sessionmaker(bind=engine)
    session: Session = Session_()
    row = V(name="a")
    session.add(row)
    session.commit()
    assert row.version == 1
    row.name = "b"
    session.commit()
    session.refresh(row)
    assert row.version == 2
