"""
Example :class:`~factory.alchemy.SQLAlchemyModelFactory` for :class:`~fast_database.persistence.models.plan.Plan`.

Requires ``factory-boy`` (``fast-database[dev]``).
"""

from __future__ import annotations

import factory

from fast_database.persistence.models.plan import Plan


class PlanFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Build ``Plan`` rows in tests (minimal required fields)."""

    class Meta:
        model = Plan
        sqlalchemy_session_persistence = "flush"

    id = factory.Sequence(lambda n: n + 1)
    plan_code = factory.Sequence(lambda n: f"plan_{n}")
    name = factory.Faker("catch_phrase")
    sessions_per_month = factory.Faker("random_int", min=0, max=1000)
    models_allowed = factory.LazyFunction(list)
    is_active = True
