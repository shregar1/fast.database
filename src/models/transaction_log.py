"""
Transaction Log Model.

SQLAlchemy ORM model for API request/response logging. Each row is one API
call: api_id (from api_lk), reference_number, request/response payloads and
headers (JSONB or encrypted binary), timestamps, HTTP status, IP. Unique on
(api_id, reference_number). Used for audit and debugging.

Usage:
    >>> from fastmvc_db_models.models.transaction_log import TransactionLog
    >>> # api_id -> api_lk; reference_number is idempotency or request id
"""



from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, LargeBinary, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from src.constants.db.table import Table
from src.models import Base


class TransactionLog(Base):
    """
    Per-request log of an API transaction (request/response and metadata).

    Links to api_lk for endpoint identity. Stores request/response payloads
    and headers (plain JSONB or encrypted LargeBinary), timestamps, http_status_code,
    ip_address. Unique on (api_id, reference_number) for idempotent logging.

    Attributes:
        id: Primary key.
        urn: Unique Resource Name (optional).
        api_id: FK to api_lk.
        reference_number: Request/idempotency identifier.
        request_payload, request_headers, request_timestamp: Request data.
        encrypted_request_payload, encrypted_request_headers: Optional encrypted.
        response_headers, response_payload, response_timestamp: Response data.
        encrypted_response_headers, encrypted_response_payload: Optional encrypted.
        http_status_code: HTTP status of response.
        ip_address: Client IP.
        created_at, updated_at, created_by, updated_by: Audit fields.
    """



    __tablename__ = Table.TRANSACTION_LOG
    __table_args__ = (
        UniqueConstraint(
            "api_id", "reference_number", name="uq_transaction_log_api_ref"
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String(128), nullable=True, unique=True, index=True)
    api_id = Column(BigInteger, ForeignKey("api_lk.id"), nullable=False, index=True)
    reference_number = Column(String(128), nullable=False, index=True)
    request_payload = Column(JSONB, nullable=True)
    request_headers = Column(JSONB, nullable=True)
    request_timestamp = Column(DateTime(timezone=True), nullable=True)
    encrypted_request_payload = Column(LargeBinary, nullable=True)
    encrypted_request_headers = Column(LargeBinary, nullable=True)
    response_headers = Column(JSONB, nullable=True)
    response_payload = Column(JSONB, nullable=True)
    response_timestamp = Column(DateTime(timezone=True), nullable=True)
    encrypted_response_headers = Column(LargeBinary, nullable=True)
    encrypted_response_payload = Column(LargeBinary, nullable=True)
    http_status_code = Column(BigInteger, nullable=True)
    ip_address = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    updated_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    def to_dict(self) -> dict:

        return {
            "urn": self.urn,
            "api_id": self.api_id,
            "reference_number": self.reference_number,
            "request_timestamp": self.request_timestamp.isoformat()
            if self.request_timestamp
            else None,
            "response_timestamp": self.response_timestamp.isoformat()
            if self.response_timestamp
            else None,
            "http_status_code": self.http_status_code,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
