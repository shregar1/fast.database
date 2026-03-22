"""
Consent Model.

SQLAlchemy ORM model for recording user acceptance of legal documents (Terms of
Service, Privacy Policy). Each row is one acceptance event: type (e.g. tos,
privacy), version string, and accepted_at timestamp.

Usage:
    >>> from fast_database.models.consent import ConsentRecord
    >>> # type is typically 'tos' or 'privacy'; version tracks policy version
"""



from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from fast_database.constants.db.table import Table
from fast_database.models import Base


class ConsentRecord(Base):
    """
    Single consent event: user accepted a specific version of ToS or Privacy.

    Used for compliance: who accepted which policy version and when. Multiple
    rows per user are expected when policies are updated (one row per acceptance).

    Attributes:
        id: Primary key.
        user_id: FK to user.
        type: Consent type (e.g. "tos", "privacy").
        version: Policy version identifier.
        accepted_at: When the user accepted.
    """



    __tablename__ = Table.CONSENT

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger,
        ForeignKey(Table.USER + ".id"),
        nullable=False,
        index=True,
    )
    type = Column(String(32), nullable=False, index=True)  # "tos" | "privacy"
    version = Column(String(64), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def to_dict(self) -> dict:

        return {
            "user_id": self.user_id,
            "type": self.type,
            "version": self.version,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
        }
