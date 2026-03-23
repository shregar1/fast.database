"""
Document Model.

SQLAlchemy ORM model for uploaded file metadata (resumes, job descriptions).
Actual file content lives in object storage; this table stores path, type,
size, content type, virus scan status, and optional links to user/session/organisation.

Usage:
    >>> from fast_database.persistence.models.document import Document
    >>> # document_type: 'resume' | 'jd'; virus_scan_status: 'pending' | 'clean' | 'infected'
"""



from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    String,
)
from fast_database.core.constants.table import Table
from fast_database.persistence.models import Base


class Document(Base):
    """
    Uploaded document metadata; file bytes are stored in object storage.

    One row per uploaded file. storage_path is the backend key/path; storage_url
    optional public or signed URL. virus_scan_status and checksum_sha256 support
    security and integrity. Optional session_id and organization_id link the
    document to a session or org.

    Attributes:
        id: Primary key.
        user_id: Owner (FK to user).
        session_id: Optional FK to session.
        organization_id: Optional FK to organization.
        document_type: e.g. "resume" or "jd".
        original_filename, content_type, size_bytes: File metadata.
        storage_path: Path/key in storage backend.
        storage_url: Optional URL (e.g. S3 or local).
        virus_scan_status: pending | clean | infected.
        checksum_sha256: Optional integrity hash.
        created_at: When the file was uploaded.
    """



    __tablename__ = Table.DOCUMENT

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger,
        ForeignKey(Table.USER + ".id"),
        nullable=False,
        index=True,
    )
    session_id = Column(
        BigInteger,
        ForeignKey(Table.SESSION + ".id"),
        nullable=True,
        index=True,
    )
    organization_id = Column(
        BigInteger,
        ForeignKey(Table.ORGANIZATION + ".id"),
        nullable=True,
        index=True,
    )

    document_type = Column(String(32), nullable=False, index=True)  # "resume" | "jd"
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(128), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    storage_path = Column(String(512), nullable=False)  # path/key in storage backend
    storage_url = Column(String(1024), nullable=True)  # URL or s3:// style

    virus_scan_status = Column(
        String(32),
        nullable=False,
        default="pending",
    )  # pending | clean | infected

    checksum_sha256 = Column(String(64), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def to_dict(self) -> dict:

        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "organization_id": self.organization_id,
            "document_type": self.document_type,
            "original_filename": self.original_filename,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
            "storage_path": self.storage_path,
            "storage_url": self.storage_url,
            "virus_scan_status": self.virus_scan_status,
            "checksum_sha256": self.checksum_sha256,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
