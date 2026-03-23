"""
Concrete SQLAlchemy repositories for ``fast_database`` tables.

Every repository class subclasses :class:`~fast_database.persistence.repositories.repository.IRepository`
and passes the appropriate SQLAlchemy model to ``super().__init__(model=..., ...)``.

Shipped in the same distribution as the ORM models:

.. code-block:: bash

    pip install "fast-database"

Example:

.. code-block:: python

    from fast_database.persistence.repositories import FilterOperator, IRepository
    from fast_database.persistence.repositories.user import UserRepository
"""

from fast_database.persistence.repositories.filter_operator import FilterOperator
from fast_database.persistence.repositories.abstraction import IRepository

__all__: list[str] = ["FilterOperator", "IRepository"]
