"""Database seeder / factory module for test and development databases.

Provides factory-boy-style model factories with auto-discovery for seeding
databases.  Uses only the Python stdlib by default (random, string, uuid,
datetime) but will transparently delegate to ``faker`` when it is installed.

Usage::

    from sqlalchemy.orm import Session
    from fastx_database.seeder import Seeder, ModelFactory, auto_factory

    # --- Quick auto-seed from a models module ---
    seeder = Seeder(session)
    seeder.auto_discover(my_app.models)
    seeder.seed_all(count=20)

    # --- Custom factory ---
    class UserFactory(ModelFactory):
        class Meta:
            model = User
        email = fake_email()
        name  = fake_name()

    user = UserFactory.create(session=session, name="Override")

    # --- One-off auto factory ---
    ProductFactory = auto_factory(Product)
    products = ProductFactory.create_batch(50, session=session)
"""

from __future__ import annotations

import inspect as _inspect
import logging
import random
import string
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
)

from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import RelationshipProperty, Session

logger = logging.getLogger(__name__)

T = TypeVar("T")

# ---------------------------------------------------------------------------
# Optional Faker integration
# ---------------------------------------------------------------------------

_faker_instance: Any = None

try:
    from faker import Faker as _Faker  # type: ignore[import-untyped]

    _faker_instance = _Faker()
    _HAS_FAKER = True
except ImportError:
    _HAS_FAKER = False


# ---------------------------------------------------------------------------
# Field generators
# ---------------------------------------------------------------------------


class _FieldGenerator:
    """Callable wrapper that produces a fake value on each call.

    When used as a class attribute on :class:`ModelFactory`, the factory
    invokes it (no args) to obtain a per-instance value.
    """

    def __init__(self, func: Callable[[], Any]) -> None:
        self._func = func

    def __call__(self) -> Any:  # noqa: D401
        return self._func()

    def __repr__(self) -> str:
        return f"<FieldGenerator {self._func.__name__}>"


def _rand_str(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def _rand_digits(length: int = 10) -> str:
    return "".join(random.choices(string.digits, k=length))


# --- Public generators ---


def fake_name() -> _FieldGenerator:
    """Generate a random full name."""
    if _HAS_FAKER:
        return _FieldGenerator(lambda: _faker_instance.name())
    return _FieldGenerator(
        lambda: f"{_rand_str(6).capitalize()} {_rand_str(8).capitalize()}"
    )


def fake_email() -> _FieldGenerator:
    """Generate a random email address."""
    if _HAS_FAKER:
        return _FieldGenerator(lambda: _faker_instance.email())
    return _FieldGenerator(lambda: f"{_rand_str(8)}@{_rand_str(6)}.com")


def fake_text(max_length: int = 200) -> _FieldGenerator:
    """Generate a random text paragraph."""
    if _HAS_FAKER:
        return _FieldGenerator(lambda: _faker_instance.text(max_nb_chars=max_length))
    return _FieldGenerator(
        lambda: " ".join(_rand_str(random.randint(3, 10)) for _ in range(20))[
            :max_length
        ]
    )


def fake_int(min_val: int = 1, max_val: int = 100_000) -> _FieldGenerator:
    """Generate a random integer in *[min_val, max_val]*."""
    return _FieldGenerator(lambda: random.randint(min_val, max_val))


def fake_float(min_val: float = 0.0, max_val: float = 100_000.0) -> _FieldGenerator:
    """Generate a random float in *[min_val, max_val)*."""
    return _FieldGenerator(lambda: random.uniform(min_val, max_val))


def fake_datetime(
    start_year: int = 2020,
    end_year: int = 2026,
) -> _FieldGenerator:
    """Generate a random timezone-aware datetime."""
    if _HAS_FAKER:
        return _FieldGenerator(
            lambda: _faker_instance.date_time_between(
                start_date=f"-{end_year - start_year}y",
                end_date="now",
                tzinfo=timezone.utc,
            )
        )

    def _gen() -> datetime:
        start = datetime(start_year, 1, 1, tzinfo=timezone.utc)
        end = datetime(end_year, 12, 31, tzinfo=timezone.utc)
        delta = end - start
        return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

    return _FieldGenerator(_gen)


def fake_date(start_year: int = 2020, end_year: int = 2026) -> _FieldGenerator:
    """Generate a random date."""
    if _HAS_FAKER:
        return _FieldGenerator(
            lambda: _faker_instance.date_between(
                start_date=f"-{end_year - start_year}y",
                end_date="today",
            )
        )

    def _gen() -> date:
        start = date(start_year, 1, 1)
        end = date(end_year, 12, 31)
        delta = end - start
        return start + timedelta(days=random.randint(0, delta.days))

    return _FieldGenerator(_gen)


def fake_bool() -> _FieldGenerator:
    """Generate a random boolean."""
    return _FieldGenerator(lambda: random.choice([True, False]))


def fake_uuid() -> _FieldGenerator:
    """Generate a random UUID4 string."""
    return _FieldGenerator(lambda: str(uuid.uuid4()))


def fake_phone() -> _FieldGenerator:
    """Generate a random phone number string."""
    if _HAS_FAKER:
        return _FieldGenerator(lambda: _faker_instance.phone_number())
    return _FieldGenerator(lambda: f"+1{_rand_digits(10)}")


def fake_address() -> _FieldGenerator:
    """Generate a random street address."""
    if _HAS_FAKER:
        return _FieldGenerator(lambda: _faker_instance.address())
    return _FieldGenerator(
        lambda: f"{random.randint(1, 9999)} {_rand_str(8).capitalize()} St"
    )


def fake_url() -> _FieldGenerator:
    """Generate a random URL."""
    if _HAS_FAKER:
        return _FieldGenerator(lambda: _faker_instance.url())
    return _FieldGenerator(lambda: f"https://{_rand_str(10)}.example.com/{_rand_str(5)}")


def fake_ip() -> _FieldGenerator:
    """Generate a random IPv4 address string."""
    if _HAS_FAKER:
        return _FieldGenerator(lambda: _faker_instance.ipv4())
    return _FieldGenerator(
        lambda: ".".join(str(random.randint(1, 254)) for _ in range(4))
    )


# ---------------------------------------------------------------------------
# Column-type to generator mapping
# ---------------------------------------------------------------------------

# Lazy imports are avoided; we import column types conditionally from
# sqlalchemy so that columns like ``Numeric`` work even when the user's
# SQLAlchemy build is minimal.

_SQLA_TYPE_MAP: Dict[str, Callable[[], _FieldGenerator]] = {}


def _build_sqla_type_map() -> Dict[str, Callable[[], _FieldGenerator]]:
    """Build the mapping once, keyed on SQLAlchemy type class name."""
    if _SQLA_TYPE_MAP:
        return _SQLA_TYPE_MAP

    _SQLA_TYPE_MAP.update(
        {
            "String": fake_name,
            "VARCHAR": fake_name,
            "Text": fake_text,
            "TEXT": fake_text,
            "Integer": fake_int,
            "INTEGER": fake_int,
            "SmallInteger": lambda: fake_int(1, 32_000),
            "SMALLINT": lambda: fake_int(1, 32_000),
            "BigInteger": lambda: fake_int(1, 2_000_000),
            "BIGINT": lambda: fake_int(1, 2_000_000),
            "Float": fake_float,
            "FLOAT": fake_float,
            "Numeric": fake_float,
            "NUMERIC": fake_float,
            "DECIMAL": fake_float,
            "Boolean": fake_bool,
            "BOOLEAN": fake_bool,
            "DateTime": fake_datetime,
            "DATETIME": fake_datetime,
            "TIMESTAMP": fake_datetime,
            "Date": fake_date,
            "DATE": fake_date,
            "UUID": fake_uuid,
            "Uuid": fake_uuid,
            "JSON": lambda: fake_text(50),
            "JSONB": lambda: fake_text(50),
            "ARRAY": lambda: fake_text(50),
            "LargeBinary": lambda: _FieldGenerator(lambda: _rand_str(20).encode()),
            "BLOB": lambda: _FieldGenerator(lambda: _rand_str(20).encode()),
            "Enum": lambda: _FieldGenerator(lambda: None),  # handled specially
        }
    )
    return _SQLA_TYPE_MAP


def _generator_for_column(col: Any) -> _FieldGenerator | None:
    """Return an appropriate :class:`_FieldGenerator` for a SQLAlchemy column.

    Returns ``None`` when no suitable generator can be determined (e.g. for
    primary-key columns with auto-increment or server defaults).
    """
    type_map = _build_sqla_type_map()
    col_type = type(col.type)
    type_name = col_type.__name__

    # Enum columns: pick from the enum members when possible.
    if type_name in ("Enum", "ENUM"):
        enums = getattr(col.type, "enums", None) or []
        if enums:
            return _FieldGenerator(lambda e=list(enums): random.choice(e))
        enum_cls = getattr(col.type, "enum_class", None)
        if enum_cls is not None:
            members = list(enum_cls)
            return _FieldGenerator(lambda m=members: random.choice(m))
        return None

    # String columns with a short length hint likely want something compact.
    if type_name in ("String", "VARCHAR"):
        length = getattr(col.type, "length", None) or 255
        if length <= 50:
            return _FieldGenerator(lambda ln=length: _rand_str(min(ln, 12)))
        # Detect email-like columns by name.
        name_lower = (col.name or "").lower()
        if "email" in name_lower:
            return fake_email()
        if "phone" in name_lower:
            return fake_phone()
        if "url" in name_lower or "website" in name_lower:
            return fake_url()
        if "ip" in name_lower:
            return fake_ip()
        if "address" in name_lower:
            return fake_address()
        if "urn" in name_lower or "uuid" in name_lower:
            return fake_uuid()
        return fake_name()

    factory_fn = type_map.get(type_name)
    if factory_fn is not None:
        return factory_fn()

    # Fallback: walk MRO of the column type to find a registered superclass.
    for parent_cls in col_type.__mro__:
        parent_name = parent_cls.__name__
        factory_fn = type_map.get(parent_name)
        if factory_fn is not None:
            return factory_fn()

    return None


# ---------------------------------------------------------------------------
# ModelFactory
# ---------------------------------------------------------------------------


class _FactoryMeta(type):
    """Metaclass that collects :class:`_FieldGenerator` class attributes."""

    def __new__(
        mcs,
        name: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any],
    ) -> _FactoryMeta:
        generators: Dict[str, _FieldGenerator] = {}
        # Inherit generators from parents.
        for base in bases:
            generators.update(getattr(base, "_field_generators", {}))
        # Collect generators declared directly on this class.
        for attr_name, attr_val in namespace.items():
            if isinstance(attr_val, _FieldGenerator):
                generators[attr_name] = attr_val
        namespace["_field_generators"] = generators
        return super().__new__(mcs, name, bases, namespace)


class ModelFactory(metaclass=_FactoryMeta):
    """Base class for declarative model factories.

    Subclasses declare a nested ``Meta`` class with ``model`` pointing to the
    SQLAlchemy model.  Field generators are declared as class attributes::

        class UserFactory(ModelFactory):
            class Meta:
                model = User
            name = fake_name()
            email = fake_email()

    Then::

        user = UserFactory.create(session=db)
        users = UserFactory.create_batch(10, session=db)
        unsaved = UserFactory.build()
    """

    class Meta:
        """Override in subclasses to specify the target model."""

        model: Type[Any] | None = None

    # Populated by metaclass.
    _field_generators: Dict[str, _FieldGenerator]

    # ---- internal helpers ----

    @classmethod
    def _resolve_model(cls) -> Type[Any]:
        model = getattr(cls.Meta, "model", None)
        if model is None:
            raise TypeError(
                f"{cls.__name__}.Meta.model must be set to a SQLAlchemy model class."
            )
        return model

    @classmethod
    def _generate_fields(cls, overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Merge generators with explicit overrides."""
        values: Dict[str, Any] = {}
        for name, gen in cls._field_generators.items():
            if name in overrides:
                values[name] = overrides.pop(name)
            else:
                values[name] = gen()
        # Any remaining overrides are passed through (user-supplied extras).
        values.update(overrides)
        return values

    # ---- public API ----

    @classmethod
    def build(cls, **overrides: Any) -> Any:
        """Instantiate the model without persisting it."""
        model = cls._resolve_model()
        values = cls._generate_fields(overrides)
        return model(**values)

    @classmethod
    def create(cls, *, session: Session, **overrides: Any) -> Any:
        """Create an instance, add it to *session*, and flush."""
        instance = cls.build(**overrides)
        session.add(instance)
        session.flush()
        return instance

    @classmethod
    def create_batch(
        cls,
        count: int,
        *,
        session: Session,
        **overrides: Any,
    ) -> List[Any]:
        """Create *count* instances, add them to *session*, and flush."""
        instances = [cls.build(**dict(overrides)) for _ in range(count)]
        session.add_all(instances)
        session.flush()
        return instances


# ---------------------------------------------------------------------------
# auto_factory
# ---------------------------------------------------------------------------


def auto_factory(
    model_class: Type[Any],
    *,
    name: str | None = None,
) -> Type[ModelFactory]:
    """Inspect a SQLAlchemy model and return a :class:`ModelFactory` subclass.

    Columns are mapped to appropriate generators based on their type.  Primary
    key columns with ``autoincrement`` are skipped.  Nullable columns produce
    ``None`` ~30 % of the time.  Columns with a Python-side ``default`` are
    skipped so the ORM default fires.  Foreign key columns are generated as
    ``fake_int()`` (the :class:`Seeder` handles FK ordering).

    Parameters
    ----------
    model_class:
        A mapped SQLAlchemy ORM class.
    name:
        Optional class name for the generated factory.  Defaults to
        ``<Model>AutoFactory``.

    Returns
    -------
    type[ModelFactory]
        A dynamically-created subclass of :class:`ModelFactory`.
    """
    mapper = sa_inspect(model_class)
    generators: Dict[str, _FieldGenerator] = {}

    for col_prop in mapper.column_attrs:
        col = col_prop.columns[0]
        col_name: str = col_prop.key

        # Skip server-side or auto-increment primary keys.
        if col.primary_key:
            if getattr(col, "autoincrement", False) or col.server_default is not None:
                continue
            # If the PK is not auto-increment, it might be a UUID or similar.
            gen = _generator_for_column(col)
            if gen is not None:
                generators[col_name] = gen
            continue

        # Skip columns with a server default.
        if col.server_default is not None:
            continue

        # Skip columns that have a Python-level default or onupdate.
        if col.default is not None or col.onupdate is not None:
            continue

        # Foreign key columns: generate an int (Seeder resolves ordering).
        if col.foreign_keys:
            generators[col_name] = fake_int(1, 1_000_000)()
            continue

        gen = _generator_for_column(col)
        if gen is None:
            if col.nullable:
                generators[col_name] = _FieldGenerator(lambda: None)
            continue

        # Wrap nullable columns so they occasionally produce None.
        if col.nullable:
            inner_gen = gen

            def _nullable_gen(g: _FieldGenerator = inner_gen) -> Any:
                return None if random.random() < 0.3 else g()

            generators[col_name] = _FieldGenerator(_nullable_gen)
        else:
            generators[col_name] = gen

    # Handle unique constraints: append a counter to string generators.
    unique_cols: Set[str] = set()
    for col_prop in mapper.column_attrs:
        col = col_prop.columns[0]
        if col.unique and col_prop.key in generators:
            unique_cols.add(col_prop.key)

    _counter: Dict[str, int] = {}

    for uname in unique_cols:
        original = generators[uname]

        def _make_unique(orig: _FieldGenerator = original, cn: str = uname) -> Any:
            _counter.setdefault(cn, 0)
            _counter[cn] += 1
            val = orig()
            if isinstance(val, str):
                return f"{val}_{_counter[cn]}"
            return val

        generators[uname] = _FieldGenerator(_make_unique)

    factory_name = name or f"{model_class.__name__}AutoFactory"
    meta = type("Meta", (), {"model": model_class})
    namespace: Dict[str, Any] = {"Meta": meta}
    namespace.update(generators)
    return _FactoryMeta(factory_name, (ModelFactory,), namespace)


# ---------------------------------------------------------------------------
# Topological sort for FK dependencies
# ---------------------------------------------------------------------------


def _topological_sort(models: Iterable[Type[Any]]) -> List[Type[Any]]:
    """Sort *models* so that parents (FK targets) come before children.

    Uses Kahn's algorithm.  Models with no FK dependencies appear first.
    Raises :class:`ValueError` on circular dependencies.
    """
    model_set = list(models)
    table_to_model: Dict[str, Type[Any]] = {}
    for m in model_set:
        tname = getattr(m, "__tablename__", None) or sa_inspect(m).mapped_table.name
        table_to_model[tname] = m

    # Build adjacency: child -> set of parent table names.
    deps: Dict[str, Set[str]] = {t: set() for t in table_to_model}
    for tname, model in table_to_model.items():
        mapper = sa_inspect(model)
        for col_prop in mapper.column_attrs:
            col = col_prop.columns[0]
            for fk in col.foreign_keys:
                parent_table = fk.column.table.name
                if parent_table in table_to_model and parent_table != tname:
                    deps[tname].add(parent_table)

    # Kahn's algorithm.
    in_degree: Dict[str, int] = {t: len(d) for t, d in deps.items()}
    queue: List[str] = [t for t, d in in_degree.items() if d == 0]
    sorted_tables: List[str] = []

    while queue:
        node = queue.pop(0)
        sorted_tables.append(node)
        for t, d in deps.items():
            if node in d:
                d.discard(node)
                in_degree[t] -= 1
                if in_degree[t] == 0:
                    queue.append(t)

    if len(sorted_tables) != len(table_to_model):
        missing = set(table_to_model) - set(sorted_tables)
        raise ValueError(
            f"Circular FK dependency detected among tables: {missing}"
        )

    return [table_to_model[t] for t in sorted_tables]


# ---------------------------------------------------------------------------
# Seeder
# ---------------------------------------------------------------------------


@dataclass
class _Registration:
    """Internal record of a registered model and its factory."""

    model_class: Type[Any]
    factory: Type[ModelFactory]


class Seeder:
    """High-level database seeder that manages model factories.

    Parameters
    ----------
    session:
        A SQLAlchemy :class:`~sqlalchemy.orm.Session`.

    Usage::

        seeder = Seeder(session)
        seeder.register(User, UserFactory)
        seeder.seed("User", count=50)
        seeder.seed_all(count=10)
        seeder.reset("User")
    """

    def __init__(self, session: Session) -> None:
        self.session = session
        self._registry: Dict[str, _Registration] = {}

    # ---- registration ----

    def register(
        self,
        model_class: Type[Any],
        factory: Type[ModelFactory] | None = None,
    ) -> None:
        """Register *model_class* with an optional custom *factory*.

        If *factory* is ``None``, one is generated automatically via
        :func:`auto_factory`.
        """
        name = model_class.__name__
        if factory is None:
            factory = auto_factory(model_class)
        self._registry[name] = _Registration(model_class=model_class, factory=factory)
        logger.debug("Seeder: registered %s", name)

    # ---- seeding ----

    def seed(
        self,
        model_name: str | None = None,
        count: int = 10,
    ) -> List[Any]:
        """Seed a single model (by class name) or all registered models.

        When *model_name* is ``None`` all models are seeded via
        :meth:`seed_all`.  Returns the created instances.
        """
        if model_name is None:
            return self.seed_all(count=count)

        reg = self._registry.get(model_name)
        if reg is None:
            raise KeyError(
                f"Model '{model_name}' is not registered.  "
                f"Available: {list(self._registry)}"
            )

        logger.info("Seeder: seeding %d rows for %s", count, model_name)
        instances = reg.factory.create_batch(count, session=self.session)
        return instances

    def seed_all(self, count: int = 10) -> List[Any]:
        """Seed all registered models, respecting FK ordering.

        Parents are seeded before children so that FK constraints are
        satisfied.
        """
        if not self._registry:
            logger.warning("Seeder: no models registered; nothing to seed.")
            return []

        models = [r.model_class for r in self._registry.values()]
        sorted_models = _topological_sort(models)
        all_instances: List[Any] = []

        for model in sorted_models:
            name = model.__name__
            reg = self._registry.get(name)
            if reg is None:
                continue
            logger.info("Seeder: seeding %d rows for %s", count, name)
            instances = reg.factory.create_batch(count, session=self.session)
            all_instances.extend(instances)

        return all_instances

    # ---- reset ----

    def reset(self, model_name: str | None = None) -> None:
        """Truncate (delete all rows from) one or all registered tables.

        When *model_name* is ``None`` all registered tables are truncated in
        reverse FK order (children first) to satisfy constraints.
        """
        if model_name is not None:
            reg = self._registry.get(model_name)
            if reg is None:
                raise KeyError(
                    f"Model '{model_name}' is not registered.  "
                    f"Available: {list(self._registry)}"
                )
            logger.info("Seeder: resetting %s", model_name)
            self.session.query(reg.model_class).delete()
            self.session.flush()
            return

        # All: reverse FK order so children are deleted before parents.
        models = [r.model_class for r in self._registry.values()]
        sorted_models = _topological_sort(models)
        for model in reversed(sorted_models):
            name = model.__name__
            if name not in self._registry:
                continue
            logger.info("Seeder: resetting %s", name)
            self.session.query(model).delete()
        self.session.flush()

    # ---- auto-discovery ----

    def auto_discover(self, models_module: Any) -> List[str]:
        """Import *models_module*, find SQLAlchemy models, and register them.

        A class is considered a model if it has a ``__tablename__`` attribute
        and descends from a SQLAlchemy declarative base (has
        ``__mapper__`` or is otherwise mapped).

        Returns a list of registered model names.
        """
        registered: List[str] = []
        for attr_name in dir(models_module):
            obj = getattr(models_module, attr_name)
            if not isinstance(obj, type):
                continue
            if not hasattr(obj, "__tablename__"):
                continue
            # Must be a mapped class.
            try:
                sa_inspect(obj)
            except Exception:
                continue
            if obj.__name__ in self._registry:
                continue
            self.register(obj)
            registered.append(obj.__name__)

        logger.info(
            "Seeder: auto-discovered %d models from %s",
            len(registered),
            getattr(models_module, "__name__", models_module),
        )
        return registered
