"""
Plan Repository.

Data access for the Plan model (plan definitions and limits keyed by plan_code).
Extends :class:`~fast_database.persistence.repositories.repository.IRepository` with ``model=Plan``.
get_by_plan_code and list_all for catalog and rate-limit/entitlement resolution.

Usage:
    >>> from fast_database.persistence.repositories.plan import PlanRepository
    >>> repo = PlanRepository(session=db_session)
    >>> plan = repo.get_by_plan_code("pro")
    >>> plans = repo.list_all()
"""



from sqlalchemy.orm import Session

from fast_database.persistence.repositories.abstraction import IRepository
from fast_database.persistence.models.plan import Plan


class PlanRepository(IRepository):
    """
    Repository for Plan (plan definition) fetch by plan_code and list.

    Methods:
        get_by_plan_code: Return Plan by plan_code (e.g. "free", "pro").
        list_all: Return all plans ordered by plan_code (catalog/pricing).
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
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            model=Plan,
            cache=None,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session) -> None:
        self._session = value

    def get_by_plan_code(self, plan_code: str) -> Plan | None:

        return self.session.query(Plan).filter(Plan.plan_code == plan_code).first()

    def list_all(self) -> list[Plan]:
        """Return all plans (e.g. for catalog / pricing page)."""

        return list(self.session.query(Plan).order_by(Plan.plan_code).all())
