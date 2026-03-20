"""
API Lookup Model.

SQLAlchemy ORM model for API endpoint definitions used in transaction logging.
One row per (method, endpoint): name, common_name, description. Unique on
(method, endpoint). Referenced by transaction_log.api_id.

Usage:
    >>> from fastmvc_db_models.models.api_lk import ApiLk
    >>> # Used to identify which API was called in TransactionLog
"""



from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String, UniqueConstraint

from fastmvc_db_models.constants.db.table import Table
from fastmvc_db_models.models import Base


class ApiLk(Base):
    """
    Lookup: API definition (method + endpoint) for transaction logging.

    Attributes:
        id: Primary key.
        urn: Unique Resource Name (optional).
        name, common_name: Identifiers for the API.
        method: HTTP method (e.g. GET, POST).
        description: Endpoint description.
        endpoint: Path or endpoint pattern.
        created_at, updated_at: Timestamps.
    """



    __tablename__ = Table.API_LK
    __table_args__ = (UniqueConstraint("method", "endpoint", name="uq_api_lk_method_endpoint"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), unique=True, index=True)
    name = Column(String(128), nullable=False, index=True)
    common_name = Column(String(128), nullable=False, index=True)
    method = Column(String(16), nullable=False)
    description = Column(String(512), nullable=False)
    endpoint = Column(String(512), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:

        return {
            "urn": self.urn,
            "name": self.name,
            "common_name": self.common_name,
            "method": self.method,
            "description": self.description,
            "endpoint": self.endpoint,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
