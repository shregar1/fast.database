"""
fastmvc_db_models
==================

Shared SQLAlchemy ORM models intended to be reused across multiple apps.

The canonical declarative `Base` is exposed here for convenience:
`from fastmvc_db_models import Base`.
"""

from fastmvc_db_models.models import Base

__all__ = ["Base"]
