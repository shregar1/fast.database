"""Logical layout of :mod:`fastx_database` (aligned with ``fastx_platform`` taxonomy).

- **persistence** — ORM models and repository implementations
- **core** — mixins, table constants, soft-delete helpers, optimistic locking, test factories
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Final

__all__ = [
    "FastDatabaseSection",
    "SECTION_SUBPACKAGES",
    "discover_leaf_subpackages",
]


class FastDatabaseSection(str, Enum):
    """Represents the FastDatabaseSection class."""

    PERSISTENCE = "persistence"
    CORE = "core"


# Physical subpackages directly under ``fastx_database/`` (excluding ``taxonomy``).
SECTION_SUBPACKAGES: Final[dict[FastDatabaseSection, frozenset[str]]] = {
    FastDatabaseSection.PERSISTENCE: frozenset({"models", "repositories"}),
    FastDatabaseSection.CORE: frozenset({"constants", "factories"}),
}


def discover_leaf_subpackages(package_root: Path | None = None) -> frozenset[str]:
    """Names of subpackages under ``persistence/`` and ``core/`` (e.g. ``models``)."""
    root = package_root or Path(__file__).resolve().parent
    names: set[str] = set()
    for section in FastDatabaseSection:
        d = root / section.value
        if not d.is_dir():
            continue
        for p in d.iterdir():
            if p.is_dir() and (p / "__init__.py").is_file():
                names.add(p.name)
    return frozenset(names)
