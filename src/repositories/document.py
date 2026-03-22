"""
Document Repository.

Data access layer for the Document model (uploaded file metadata: resume, JD,
storage path, virus scan status). Provides create, retrieve by id, filtered
listing (user_id, session_id, document_type), and hard delete. Extends
:class:`~fast_database.repositories.repository.IRepository` with ``model=Document``.

Usage:
    >>> from fast_database.repositories.document import DocumentRepository
    >>> repo = DocumentRepository(session=db_session)
    >>> doc = repo.create_record(record=document_instance)
    >>> docs, total = repo.retrieve_records(user_id=1, document_type="resume")
"""



from sqlalchemy.orm import Session

from fast_database.repositories.abstraction import IRepository
from fast_database.models.document import Document


class DocumentRepository(IRepository):
    """
    Repository for Document (uploaded file metadata) database operations.

    Create document records, fetch by id, list with optional filters (user_id,
    session_id, document_type), and delete_record (hard delete). Used by
    upload and document-listing flows.

    Methods:
        create_record: Add and commit a Document instance.
        retrieve_record_by_id: Fetch by primary key.
        retrieve_records: Paginated list with optional filters; returns (items, total).
        delete_record: Delete by id (returns bool).
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
            model=Document,
            cache=None,
        )
        self._session = session

    @property
    def session(self) -> Session:

        return self._session

    @session.setter
    def session(self, value: Session) -> None:
        self._session = value

    def create_record(self, record: Document) -> Document:
        self.logger.debug(f"Creating document: user_id={record.user_id}, type={record.document_type}")
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        self.logger.info(f"Created document with ID: {record.id}")

        return record

    def retrieve_record_by_id(self, record_id: int) -> Document | None:

        return self.session.query(Document).filter(Document.id == record_id).first()

    def retrieve_records(
        self,
        user_id: int | None = None,
        session_id: int | None = None,
        document_type: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Document], int]:
        query = self.session.query(Document)
        if user_id is not None:
            query = query.filter(Document.user_id == user_id)
        if session_id is not None:
            query = query.filter(Document.session_id == session_id)
        if document_type is not None:
            query = query.filter(Document.document_type == document_type)
        total = query.count()

        items = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

        return items, total

    def delete_record(self, record_id: int) -> bool:
        record = self.retrieve_record_by_id(record_id)
        if not record:

            return False
        self.session.delete(record)

        self.session.commit()
        self.logger.info(f"Deleted document: {record_id}")

        return True
