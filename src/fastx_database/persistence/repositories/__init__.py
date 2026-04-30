"""Concrete SQLAlchemy repositories for ``fastx_database`` tables.

Every repository class subclasses :class:`~fastx_database.persistence.repositories.repository.IRepository`
and passes the appropriate SQLAlchemy model to ``super().__init__(model=..., ...)``.

Shipped in the same distribution as the ORM models:

.. code-block:: bash

    pip install "fast-database"

Example:

.. code-block:: python

    from fastx_database.persistence.repositories import FilterOperator, IRepository
    from fastx_database.persistence.repositories.user import UserRepository

"""

from fastx_database.persistence.repositories.filter_operator import FilterOperator
from fastx_database.persistence.repositories.abstraction import IRepository

__all__: list[str] = ["FilterOperator", "IRepository"]
