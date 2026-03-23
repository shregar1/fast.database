"""
Product Repository.

Data access layer for the Product model. Provides CRUD, retrieve by id/urn,
filtered listing (category, is_active, search), and soft delete when the
model exposes `is_deleted`. Uses IRepository base (urn, user_urn, api_name,
user_id, model=Product).
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from fast_database.persistence.repositories.abstraction import IRepository
from fast_database.core.soft_delete import filter_active, mark_soft_deleted
from fast_database.persistence.models.product import Product


def _has_soft_delete() -> bool:
    return hasattr(Product, "is_deleted")


def _active_products_query(session: Session):
    q = session.query(Product)
    if _has_soft_delete():
        q = filter_active(q, Product.is_deleted)
    return q


class ProductRepository(IRepository):
    """
    Repository for Product database operations.
    """

    def __init__(
        self,
        session: Session | None = None,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        self._cache = None
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            cache=self._cache,
            model=Product,
        )
        self._session = session

    @property
    def session(self) -> Session | None:
        return self._session

    @session.setter
    def session(self, value: Session | None) -> None:
        self._session = value

    def create_record(self, record: Product) -> Product:
        """Create a new product record."""
        self.logger.debug(f"Creating product: {record.name}")
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        self.logger.info(f"Created product with ID: {record.id}")

        return record

    def retrieve_record_by_id(self, record_id: int) -> Product | None:
        """Retrieve a product by ID."""
        self.logger.debug(f"Retrieving product by ID: {record_id}")

        q = self.session.query(Product).filter(Product.id == record_id)
        if _has_soft_delete():
            q = filter_active(q, Product.is_deleted)
        return q.first()

    def retrieve_record_by_urn(self, urn: str) -> Product | None:
        """Retrieve a product by URN."""
        self.logger.debug(f"Retrieving product by URN: {urn}")

        q = self.session.query(Product).filter(Product.urn == urn)
        if _has_soft_delete():
            q = filter_active(q, Product.is_deleted)
        return q.first()

    def retrieve_all_records(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> list[Product]:
        """Retrieve all products with pagination."""
        self.logger.debug(f"Retrieving products: skip={skip}, limit={limit}")
        query = _active_products_query(self.session)

        if active_only:
            query = query.filter(Product.is_active)

        return query.offset(skip).limit(limit).all()

    def list_records(
        self,
        skip: int = 0,
        limit: int = 100,
        active: bool | None = None,
        search: str | None = None,
    ) -> tuple[list[Product], int]:
        """List products with optional filters."""
        query = _active_products_query(self.session)
        if active is not None:
            query = query.filter(Product.is_active.is_(active))
        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(
                (Product.name.ilike(term)) | (Product.description.ilike(term))
            )
        total = query.count()

        items = query.order_by(Product.id).offset(skip).limit(limit).all()

        return list(items), total

    def retrieve_record_by_id_or_urn(self, id_or_urn: str) -> Product | None:
        """Retrieve a product by ID (int) or URN (str)."""
        stripped = (id_or_urn or "").strip()
        if not stripped:
            return None
        try:
            record_id = int(stripped)
            return self.retrieve_record_by_id(record_id)
        except ValueError:
            return self.retrieve_record_by_urn(stripped)

    def update_record(self, record: Product) -> Product:
        """Update an existing product record."""
        self.logger.debug(f"Updating product: {record.id}")
        self.session.commit()
        self.session.refresh(record)
        self.logger.info(f"Updated product: {record.id}")

        return record

    def delete_record(self, record_id: int, deleted_by: int) -> bool:
        """
        Soft delete when `is_deleted` exists; otherwise hard-delete the row.
        """
        self.logger.debug(f"Deleting product: {record_id}")
        record = self.retrieve_record_by_id(record_id)

        if not record:
            return False

        if _has_soft_delete():
            mark_soft_deleted(record)
            record.updated_by = deleted_by
            self.session.commit()
            self.logger.info(f"Soft deleted product: {record_id}")
            return True

        self.session.delete(record)
        self.session.commit()
        self.logger.info(f"Hard deleted product: {record_id}")
        return True

    def count_records(self, active_only: bool = True) -> int:
        """Count total product records."""
        query = _active_products_query(self.session)

        if active_only:
            query = query.filter(Product.is_active)

        return query.count()
