"""factory_boy Plan example (optional dev extra)."""

from __future__ import annotations

import pytest

factory = pytest.importorskip("factory")
pytest.importorskip("factory.alchemy")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastx_database.core.factories.plan_factory import PlanFactory
from fastx_database.persistence.models.plan import Plan


@pytest.fixture()
def plan_session():
    """Execute plan_session operation.

    Returns:
        The result of the operation.
    """
    engine = create_engine("sqlite:///:memory:")
    Plan.__table__.create(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    PlanFactory._meta.sqlalchemy_session = sess
    try:
        yield sess
    finally:
        sess.close()


def test_plan_factory_creates_row(plan_session):
    """Execute test_plan_factory_creates_row operation.

    Args:
        plan_session: The plan_session parameter.

    Returns:
        The result of the operation.
    """
    p = PlanFactory()
    plan_session.commit()
    assert p.id is not None
    assert p.plan_code.startswith("plan_")
