"""
Coupon Repository.

Data access for the Coupon model (discount codes). Extends
:class:`~fast_repositories.repository.IRepository`.
get_by_code returns an active, valid coupon: within valid_from/valid_until and
under max_redemptions if set. Used at checkout and subscription creation for
discount application.

Usage:
    >>> from fast_repositories.coupon import CouponRepository
    >>> repo = CouponRepository(session=db_session)
    >>> coupon = repo.get_by_code("SAVE20")
"""



from datetime import datetime

from sqlalchemy.orm import Session

from fast_repositories.repository import IRepository
from fast_database.models.coupon import Coupon


class CouponRepository(IRepository):
    """
    Repository for Coupon (discount code) lookup by code.

    get_by_code: Return active coupon by code (case-sensitive) that is within
    valid_from/valid_until and under max_redemptions. Returns None if not found
    or invalid.
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
            model=Coupon,
            cache=None,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session) -> None:
        self._session = value

    def get_by_code(self, code: str) -> Coupon | None:
        """
        Return an active, valid coupon by code (case-sensitive).
        Valid = within valid_from/valid_until and under max_redemptions if set.
        """


        if not (code and code.strip()):

            return None
        now = datetime.utcnow()

        q = (
            self.session.query(Coupon)
            .filter(Coupon.code == code.strip())
            .filter(Coupon.is_active.is_(True))
        )
        # valid_from <= now (or null)
        q = q.filter((Coupon.valid_from.is_(None)) | (Coupon.valid_from <= now))
        # valid_until >= now (or null)
        q = q.filter((Coupon.valid_until.is_(None)) | (Coupon.valid_until >= now))
        # under max_redemptions if set
        q = q.filter(
            (Coupon.max_redemptions.is_(None))
            | (Coupon.redemptions_count < Coupon.max_redemptions)
        )

        return q.first()
