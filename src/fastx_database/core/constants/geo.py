"""Geo / shard constants."""

from __future__ import annotations

from typing import Final

EARTH_RADIUS_KM: Final[int] = 6371


class Shard:
    US_EAST: Final[str] = "us-east"
    US_WEST: Final[str] = "us-west"
    EU_WEST: Final[str] = "eu-west"
    EU_CENTRAL: Final[str] = "eu-central"
    APAC_TOKYO: Final[str] = "apac-tokyo"
    APAC_SINGAPORE: Final[str] = "apac-singapore"
    APAC_SYDNEY: Final[str] = "apac-sydney"
