"""Read replica support with automatic read/write splitting for SQLAlchemy.

Provides a routing session that automatically directs SELECT queries to read
replicas and write operations to the primary database, with configurable
replica selection strategies.

Usage::

    from fastx_database.read_replicas import (
        ReplicaConfig,
        ReplicaSessionFactory,
        create_replica_engines,
        use_primary,
    )

    config = ReplicaConfig(
        primary_url="postgresql://primary:5432/mydb",
        replica_urls=[
            "postgresql://replica1:5432/mydb",
            "postgresql://replica2:5432/mydb",
        ],
        strategy="round_robin",
    )

    engines = create_replica_engines(config)
    session_factory = ReplicaSessionFactory(
        primary_engine=engines["primary"],
        replica_engines=engines["replicas"],
        strategy=config.strategy,
    )

    # Automatic routing: SELECTs go to replicas, writes go to primary.
    with session_factory() as session:
        users = session.execute(select(User)).scalars().all()  # replica
        session.add(User(name="new"))                          # primary
        session.commit()

    # Force primary for read-after-write consistency:
    with session_factory() as session:
        session.add(User(name="new"))
        session.commit()
        with use_primary(session):
            user = session.execute(select(User)).scalars().first()  # primary
"""

from __future__ import annotations

import logging
import random
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Generator, Literal

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)

# Thread-local storage for force-primary flag.
_local = threading.local()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class ReplicaConfig:
    """Configuration for primary/replica database topology.

    Attributes:
        primary_url: SQLAlchemy connection URL for the primary (read-write) database.
        replica_urls: SQLAlchemy connection URLs for read-only replicas.
        strategy: Replica selection strategy.
        engine_kwargs: Extra keyword arguments forwarded to ``create_engine``
            for every engine (primary and replicas).
    """

    primary_url: str
    replica_urls: list[str] = field(default_factory=list)
    strategy: Literal["round_robin", "random", "least_connections"] = "round_robin"
    engine_kwargs: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Engine creation
# ---------------------------------------------------------------------------


def create_replica_engines(config: ReplicaConfig) -> dict[str, Any]:
    """Create SQLAlchemy engines for primary and all replicas.

    Returns a dict with ``"primary"`` (a single :class:`~sqlalchemy.engine.Engine`)
    and ``"replicas"`` (a list of :class:`~sqlalchemy.engine.Engine`).

    Args:
        config: A :class:`ReplicaConfig` describing the database topology.

    Returns:
        ``{"primary": Engine, "replicas": [Engine, ...]}``

    Example::

        engines = create_replica_engines(config)
        primary = engines["primary"]
        replicas = engines["replicas"]
    """
    kwargs = dict(config.engine_kwargs)

    primary_engine = create_engine(config.primary_url, **kwargs)
    logger.info("Created primary engine: %s", _safe_url(config.primary_url))

    replica_engines: list[Engine] = []
    for url in config.replica_urls:
        engine = create_engine(url, **kwargs)
        replica_engines.append(engine)
        logger.info("Created replica engine: %s", _safe_url(url))

    return {"primary": primary_engine, "replicas": replica_engines}


def _safe_url(url: str) -> str:
    """Mask password in a connection URL for safe logging."""
    try:
        from sqlalchemy.engine.url import make_url

        parsed = make_url(url)
        return str(parsed.set(password="***")) if parsed.password else str(parsed)
    except Exception:
        return "<url>"


# ---------------------------------------------------------------------------
# Replica selection strategies
# ---------------------------------------------------------------------------


class _ReplicaSelector:
    """Base class for replica selection strategies."""

    def __init__(self, replicas: list[Engine]) -> None:
        self._replicas = replicas

    def select(self) -> Engine:
        raise NotImplementedError


class _RoundRobinSelector(_ReplicaSelector):
    """Cycle through replicas in order."""

    def __init__(self, replicas: list[Engine]) -> None:
        super().__init__(replicas)
        self._lock = threading.Lock()
        self._index = 0

    def select(self) -> Engine:
        with self._lock:
            engine = self._replicas[self._index % len(self._replicas)]
            self._index += 1
            return engine


class _RandomSelector(_ReplicaSelector):
    """Pick a random replica for each query."""

    def select(self) -> Engine:
        return random.choice(self._replicas)


class _LeastConnectionsSelector(_ReplicaSelector):
    """Pick the replica with the fewest checked-out connections.

    Falls back to round-robin when pool sizes are equal.
    """

    def select(self) -> Engine:
        return min(
            self._replicas,
            key=lambda e: e.pool.checkedout() if hasattr(e.pool, "checkedout") else 0,
        )


_STRATEGY_MAP: dict[str, type[_ReplicaSelector]] = {
    "round_robin": _RoundRobinSelector,
    "random": _RandomSelector,
    "least_connections": _LeastConnectionsSelector,
}


def _make_selector(
    strategy: str, replicas: list[Engine]
) -> _ReplicaSelector:
    cls = _STRATEGY_MAP.get(strategy)
    if cls is None:
        raise ValueError(
            f"Unknown replica strategy {strategy!r}. "
            f"Choose from: {', '.join(_STRATEGY_MAP)}"
        )
    return cls(replicas)


# ---------------------------------------------------------------------------
# RoutingSession
# ---------------------------------------------------------------------------


class RoutingSession(Session):
    """A SQLAlchemy :class:`~sqlalchemy.orm.Session` that routes queries
    to primary or replica engines based on the SQL operation.

    * ``SELECT`` statements are sent to a read replica.
    * All other statements (``INSERT``, ``UPDATE``, ``DELETE``, DDL) are sent
      to the primary engine.
    * When :func:`use_primary` is active, **all** statements go to primary.
    * After any flush (i.e., after a write within the same transaction),
      subsequent reads are automatically routed to primary for the remainder
      of the transaction to ensure read-after-write consistency.

    This class is not instantiated directly; use :class:`ReplicaSessionFactory`.
    """

    _primary_engine: Engine
    _replica_selector: _ReplicaSelector
    _force_primary: bool

    def __init__(
        self,
        primary_engine: Engine,
        replica_selector: _ReplicaSelector,
        **kwargs: Any,
    ) -> None:
        self._primary_engine = primary_engine
        self._replica_selector = replica_selector
        self._force_primary = False
        super().__init__(bind=primary_engine, **kwargs)

    # -- SQLAlchemy 2.0 bind routing -----------------------------------------

    def get_bind(
        self,
        mapper: Any = None,
        *,
        clause: Any = None,
        **kwargs: Any,
    ) -> Engine:
        """Route to primary or replica based on statement type.

        Returns the primary engine for write operations and when
        ``use_primary`` is active, otherwise returns a replica engine
        selected via the configured strategy.
        """
        # Always use primary if forced (context manager or post-flush).
        if self._force_primary or getattr(_local, "force_primary", False):
            return self._primary_engine

        # If there are no replicas, fall back to primary.
        if not self._replica_selector._replicas:
            return self._primary_engine

        # Detect read vs write from the clause/statement.
        if clause is not None and _is_read_statement(clause):
            engine = self._replica_selector.select()
            logger.debug("Routing read to replica: %s", engine.url)
            return engine

        # Default: writes go to primary.
        return self._primary_engine

    # -- Automatic force-primary after flush ---------------------------------

    def flush(self, objects: Any = None) -> None:  # type: ignore[override]
        """After flushing, pin subsequent reads to primary for consistency."""
        super().flush(objects=objects)
        self._force_primary = True

    def commit(self) -> None:
        """Commit and reset the force-primary flag."""
        super().commit()
        self._force_primary = False

    def rollback(self) -> None:
        """Rollback and reset the force-primary flag."""
        super().rollback()
        self._force_primary = False

    def close(self) -> None:
        """Close the session and reset the force-primary flag."""
        self._force_primary = False
        super().close()


def _is_read_statement(clause: Any) -> bool:
    """Return ``True`` if *clause* represents a SELECT (read) operation."""
    # ClauseElement instances expose .is_select on compiled forms;
    # we also inspect the string representation as a reliable fallback.
    if hasattr(clause, "is_select") and clause.is_select:
        return True
    # Handle text() clauses and other raw SQL.
    text = str(clause).strip()
    return text.upper().startswith("SELECT") or text.upper().startswith("WITH")


# ---------------------------------------------------------------------------
# ReplicaSessionFactory
# ---------------------------------------------------------------------------


class ReplicaSessionFactory:
    """Callable factory that produces :class:`RoutingSession` instances.

    Args:
        primary_engine: The read-write engine.
        replica_engines: A list of read-only replica engines.
        strategy: Replica selection strategy name
            (``"round_robin"``, ``"random"``, or ``"least_connections"``).

    Example::

        factory = ReplicaSessionFactory(primary, replicas, "round_robin")
        session = factory()
        try:
            result = session.execute(select(User))
        finally:
            session.close()
    """

    def __init__(
        self,
        primary_engine: Engine,
        replica_engines: list[Engine],
        strategy: str = "round_robin",
    ) -> None:
        self._primary_engine = primary_engine
        self._replica_engines = replica_engines
        self._selector = _make_selector(strategy, replica_engines)

    def __call__(self, **kwargs: Any) -> RoutingSession:
        """Create and return a new :class:`RoutingSession`."""
        return RoutingSession(
            primary_engine=self._primary_engine,
            replica_selector=self._selector,
            **kwargs,
        )


# ---------------------------------------------------------------------------
# use_primary context manager
# ---------------------------------------------------------------------------


@contextmanager
def use_primary(session: RoutingSession | None = None) -> Generator[None, None, None]:
    """Force all queries to use the primary database within this block.

    Can operate at two levels:

    * **Session-level** -- pass a :class:`RoutingSession` to pin only that
      session to primary.
    * **Thread-level** -- omit the *session* argument to pin **all**
      ``RoutingSession`` instances in the current thread.

    This is useful for read-after-write scenarios where replica lag could
    return stale data.

    Example::

        with use_primary(session):
            # This SELECT goes to primary, not a replica.
            fresh = session.execute(select(User).where(User.id == new_id)).scalar_one()
    """
    if session is not None:
        previous = session._force_primary
        session._force_primary = True
        try:
            yield
        finally:
            session._force_primary = previous
    else:
        previous = getattr(_local, "force_primary", False)
        _local.force_primary = True
        try:
            yield
        finally:
            _local.force_primary = previous


# ---------------------------------------------------------------------------
# ReadReplicaMixin for repositories
# ---------------------------------------------------------------------------


class ReadReplicaMixin:
    """Mixin for repository classes that adds explicit replica/primary control.

    The host repository must expose a ``session`` attribute that is (or wraps)
    a :class:`RoutingSession`.

    Example::

        class UserRepository(IRepository, ReadReplicaMixin):
            def get_dashboard_stats(self):
                # Explicitly read from a replica.
                with self.read_from_replica():
                    return self.session.execute(select(func.count(User.id))).scalar()

            def get_after_write(self, user_id: int):
                # Explicitly read from primary for consistency.
                with self.read_from_primary():
                    return self.session.execute(
                        select(User).where(User.id == user_id)
                    ).scalar_one()
    """

    session: RoutingSession  # expected on the host class

    @contextmanager
    def read_from_replica(self) -> Generator[None, None, None]:
        """Ensure reads within this block go to a replica.

        If the session's ``_force_primary`` flag was set (e.g., after a flush),
        this temporarily unsets it so that reads are routed to replicas.
        """
        session = self._get_routing_session()
        previous = session._force_primary
        session._force_primary = False
        try:
            yield
        finally:
            session._force_primary = previous

    @contextmanager
    def read_from_primary(self) -> Generator[None, None, None]:
        """Force reads within this block to go to the primary database."""
        session = self._get_routing_session()
        previous = session._force_primary
        session._force_primary = True
        try:
            yield
        finally:
            session._force_primary = previous

    def _get_routing_session(self) -> RoutingSession:
        """Retrieve the underlying :class:`RoutingSession`.

        Raises:
            TypeError: If ``self.session`` is not a :class:`RoutingSession`.
        """
        session = self.session
        if not isinstance(session, RoutingSession):
            raise TypeError(
                f"ReadReplicaMixin requires a RoutingSession, got {type(session).__name__}. "
                "Ensure the repository's session was created by a ReplicaSessionFactory."
            )
        return session
