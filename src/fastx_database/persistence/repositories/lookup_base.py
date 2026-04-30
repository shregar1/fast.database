"""
Lookup Repository Base Module.

Provides a base class for lookup table repositories to eliminate
duplicate boilerplate code across lookup repositories.

Lookup repositories typically have identical initialization patterns
and a list_all() method - this base class provides that standard
implementation.

Example:
    >>> from fastx_database.persistence.repositories.lookup_base import LookupRepositoryBase
    >>> from fastx_database.persistence.models.status_lk import StatusLk
    >>> 
    >>> class StatusLkRepository(LookupRepositoryBase[StatusLk]):
    ...     def __init__(self, session, **kwargs):
    ...         super().__init__(model=StatusLk, session=session, order_by="code", **kwargs)
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

from fastx_database.persistence.repositories.abstraction import IRepository


ModelT = TypeVar("ModelT")


class LookupRepositoryBase(IRepository, Generic[ModelT]):
    """
    Base class for lookup table repositories.
    
    Eliminates duplicate boilerplate across lookup repositories by providing:
    - Standard initialization with session and context fields
    - list_all() method with configurable ordering
    
    Type Parameters:
        ModelT: The SQLAlchemy model class for this lookup table.
    
    Attributes:
        session: SQLAlchemy ORM session.
        _order_by: Field name to use for ordering in list_all().
    
    Example:
        >>> from fastx_database.persistence.repositories.lookup_base import LookupRepositoryBase
        >>> from fastx_database.persistence.models.status_lk import StatusLk
        >>> 
        >>> class StatusLkRepository(LookupRepositoryBase[StatusLk]):
        ...     """Repository for StatusLk records."""
        ...     
        ...     def __init__(self, session: Session, **kwargs):
        ...         super().__init__(
        ...             model=StatusLk, 
        ...             session=session, 
        ...             order_by="code",
        ...             **kwargs
        ...         )
        >>> 
        >>> repo = StatusLkRepository(session=db_session)
        >>> all_statuses = repo.list_all()  # Ordered by code
    
    Example with different ordering:
        >>> from fastx_database.persistence.models.language_lk import LanguageLk
        >>> 
        >>> class LanguageLkRepository(LookupRepositoryBase[LanguageLk]):
        ...     """Repository for LanguageLk records."""
        ...     
        ...     def __init__(self, session: Session, **kwargs):
        ...         super().__init__(
        ...             model=LanguageLk, 
        ...             session=session, 
        ...             order_by="description",  # Order by description instead
        ...             **kwargs
        ...         )
    """

    def __init__(
        self,
        model: type[ModelT],
        session: Session,
        order_by: str = "code",
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ):
        """
        Initialize the lookup repository.
        
        Args:
            model: The SQLAlchemy model class for this lookup table.
            session: SQLAlchemy ORM session.
            order_by: Field name to use for ordering in list_all().
                      Defaults to "code".
            urn: Unique Request Number for tracing.
            user_urn: User's unique resource name.
            api_name: Name of the API endpoint.
            user_id: Database identifier of the user.
        """
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            cache=None,
            model=model,
        )
        self._session = session
        self._order_by = order_by

    @property
    def session(self) -> Session:
        """SQLAlchemy ORM session."""
        return self._session

    @session.setter
    def session(self, value: Session) -> None:
        self._session = value

    def list_all(self) -> list[ModelT]:
        """
        Return all lookup entries ordered by the configured field.
        
        Returns:
            List of all lookup records, ordered by the field specified
            in the constructor (defaults to "code").
            
        Example:
            >>> repo = StatusLkRepository(session=db_session)
            >>> all_statuses = repo.list_all()
            >>> # Equivalent to: session.query(StatusLk).order_by(StatusLk.code).all()
        """
        order_column = getattr(self.model, self._order_by)
        return (
            self.session.query(self.model)
            .order_by(order_column)
            .all()
        )

    def find_by_code(self, code: str) -> ModelT | None:
        """
        Find a lookup record by its unique code.
        
        Args:
            code: The unique code to search for.
            
        Returns:
            The matching record, or None if not found.
            
        Example:
            >>> status = repo.find_by_code("active")
            >>> if status:
            ...     print(f"Found: {status.description}")
        """
        return self.retrieve_record_by_filter(
            filters={"code": code},
            include_deleted=True,  # Lookup tables typically don't use soft delete
        )

    def find_by_urn(self, urn: str) -> ModelT | None:
        """
        Find a lookup record by its URN.
        
        Args:
            urn: The URN to search for.
            
        Returns:
            The matching record, or None if not found.
            
        Example:
            >>> status = repo.find_by_urn("urn:status:active")
        """
        return self.retrieve_record_by_filter(
            filters={"urn": urn},
            include_deleted=True,
        )
