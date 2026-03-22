"""
Concrete SQLAlchemy repositories for ``fast_database`` tables.

Every repository class subclasses :class:`~fast_repositories.repository.IRepository`
and passes the appropriate SQLAlchemy model to ``super().__init__(model=..., ...)``.

Shipped in the same distribution as the ORM models:

.. code-block:: bash

    pip install "fast-database"

Example:

.. code-block:: python

    from fast_repositories import FilterOperator, IRepository
    from fast_repositories.user import UserRepository
"""

from fast_repositories.filter_operator import FilterOperator
from fast_repositories.repository import IRepository

__all__: list[str] = ["FilterOperator", "IRepository"]
