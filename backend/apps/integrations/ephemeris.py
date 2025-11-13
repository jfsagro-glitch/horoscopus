from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any, Dict, Iterable

import requests
import structlog
from django.conf import settings
from django.core.cache import cache

from apps.core.models import Location

logger = structlog.get_logger(__name__)

SIGN_NAMES = (
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
)

SWISS_BODIES = {
    "sun": "SUN",
    "moon": "MOON",
    "mercury": "MERCURY",
    "venus": "VENUS",
    "mars": "MARS",
    "jupiter": "JUPITER",
    "saturn": "SATURN",
    "uranus": "URANUS",
    "neptune": "NEPTUNE",
    "pluto": "PLUTO",
    "north_node": "MEAN_NODE",
    "south_node": "MEAN_NODE",
    "lilith": "MEAN_APOG",
}

try:
    import swisseph as swe  # type: ignore

    HAS_SWISSEPH = True
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    swe = None
    HAS_SWISSEPH = False


def _normalise_degree(value: float) -> float:
    return value % 360.0


def _resolve_sign(longitude: float) -> str:
    index = int(_normalise_degree(longitude) // 30)
    return SIGN_NAMES[index]


def _resolve_house(longitude: float, cusps: Iterable[float]) -> int:
    norm = _normalise_degree(longitude)
    ordered = list(cusps)
    if len(ordered) != 12:
        return 1
    for idx in range(12):
        cusp_start = _normalise_degree(ordered[idx])
        cusp_end = _normalise_degree(ordered[(idx + 1) % 12])
        if cusp_start <= cusp_end:
            if cusp_start <= norm < cusp_end:
                return idx + 1
        else:
            if norm >= cusp_start or norm < cusp_end:
                return idx + 1
    return 12


def _format_body_payload(
    slug: str,
    longitude: float,
    latitude: float,
    distance_au: float,
    speed: float,
    cusps: Iterable[float],
) -> dict[str, Any]:
    return {
        "slug": slug,
        "longitude": _normalise_degree(longitude),
        "latitude": latitude,
        "distance_au": distance_au,
        "retrograde": speed < 0,
        "speed": speed,
        "sign": _resolve_sign(longitude),
        "house": _resolve_house(longitude, cusps),
    }


class BaseEphemerisClient:
    provider: str

    def get_natal_ephemeris(self, dt_utc: dt.datetime, location: Location) -> dict[str, Any]:
        raise NotImplementedError


class SwissEphemerisClient(BaseEphemerisClient):
    provider = "swiss"

    def __init__(self) -> None:
        if not HAS_SWISSEPH:
            raise RuntimeError("pyswisseph is not installed")
        swe.set_ephe_path(settings.EPHEMERIS_PATH)

    def get_natal_ephemeris(self, dt_utc: dt.datetime, location: Location) -> dict[str, Any]:
        julian_day = self._calc_julian_day(dt_utc)
        latitude = float(location.latitude)
        longitude = float(location.longitude)
        house_system = b"P"  # Placidus by default

        cusps, ascmc = swe.houses_ex(julian_day, latitude, longitude, house_system)
        bodies: Dict[str, Dict[str, Any]] = {}

        for slug, attr in SWISS_BODIES.items():
            body_id = getattr(swe, attr)
            if slug == "south_node":
                north_node = bodies.get("north_node")
                if north_node:
                    south_longitude = _normalise_degree(north_node["longitude"] + 180.0)
                    bodies[slug] = {
                        **north_node,
                        "slug": slug,
                        "longitude": south_longitude,
                        "sign": _resolve_sign(south_longitude),
                        "house": _resolve_house(south_longitude, cusps),
                    }
                    continue

            longitude, latitude, distance, speed = swe.calc_ut(julian_day, body_id)
            bodies[slug] = _format_body_payload(
                slug=slug,
                longitude=longitude,
                latitude=latitude,
                distance_au=distance,
                speed=speed,
                cusps=cusps,
            )

        payload = {
            "source": "swiss",
            "house_system": "placidus",
            "datetime": dt_utc.isoformat(),
            "location": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "houses": {
                "cusps": list(cusps),
                "angles": {
                    "asc": ascmc[0],
                    "mc": ascmc[1],
                    "vertex": ascmc[3],
                },
            },
            "bodies": bodies,
        }
        logger.info("integrations.ephemeris.swiss.success", datetime=dt_utc.isoformat())
        return payload

    @staticmethod
    def _calc_julian_day(dt_utc: dt.datetime) -> float:
        utc = dt_utc.replace(tzinfo=None)
        fraction = (
            utc.hour + utc.minute / 60 + utc.second / 3600 + utc.microsecond / 3_600_000_000
        )
        return swe.julday(utc.year, utc.month, utc.day, fraction)


class HorizonsEphemerisClient(BaseEphemerisClient):
    provider = "nasa-horizons"

    def get_natal_ephemeris(self, dt_utc: dt.datetime, location: Location) -> dict[str, Any]:
        logger.info(
            "integrations.ephemeris.horizons.request",
            datetime=dt_utc.isoformat(),
            latitude=str(location.latitude),
            longitude=str(location.longitude),
        )
        params = {
            "format": "text",
            "COMMAND": "10",
        }
        try:
            response = requests.get(
                settings.HORIZONS_ENDPOINT,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - network failure
            logger.error("integrations.ephemeris.horizons.error", error=str(exc))
            raise

        logger.warning(
            "integrations.ephemeris.horizons.not_implemented",
            note="Horizons integration placeholder, falling back to stub.",
        )
        raise NotImplementedError("Horizons integration requires further implementation.")


class StubEphemerisClient(BaseEphemerisClient):
    provider = "stub"

    def get_natal_ephemeris(self, dt_utc: dt.datetime, location: Location) -> dict[str, Any]:
        logger.warning(
            "integrations.ephemeris.stub",
            provider=self.provider,
            datetime=dt_utc.isoformat(),
            location_id=location.id,
        )
        bodies = {}
        base_degree = (dt_utc.timetuple().tm_yday % 360)
        cusps = [n * 30.0 for n in range(1, 13)]
        for idx, slug in enumerate(SWISS_BODIES.keys()):
            lon = _normalise_degree(base_degree + idx * 27.5)
            bodies[slug] = _format_body_payload(
                slug=slug,
                longitude=lon,
                latitude=0.0,
                distance_au=1.0,
                speed=1.0,
                cusps=cusps,
            )
        return {
            "source": "stub",
            "house_system": "placidus",
            "datetime": dt_utc.isoformat(),
            "location": {
                "latitude": float(location.latitude),
                "longitude": float(location.longitude),
            },
            "houses": {
                "cusps": cusps,
                "angles": {"asc": 0.0, "mc": 90.0},
            },
            "bodies": bodies,
        }


@dataclass
class EphemerisClient:
    provider: str | None = None

    def __post_init__(self) -> None:
        self.provider = self.provider or settings.EPHEMERIS_PROVIDER

    def get_natal_ephemeris(self, dt_utc: dt.datetime, location: Location) -> dict[str, Any]:
        cache_key = f"ephemeris:{self.provider}:{location.id}:{dt_utc.isoformat()}"
        cached = cache.get(cache_key)
        if cached:
            logger.debug("integrations.ephemeris.cache.hit", key=cache_key)
            return cached

        try:
            payload = self._get_client().get_natal_ephemeris(dt_utc, location)
            cache.set(cache_key, payload, timeout=7 * 24 * 60 * 60)
            logger.debug("integrations.ephemeris.cache.store", key=cache_key)
            return payload
        except Exception as exc:
            logger.exception("integrations.ephemeris.error", provider=self.provider, error=str(exc))
            fallback = StubEphemerisClient().get_natal_ephemeris(dt_utc, location)
            cache.set(cache_key, fallback, timeout=24 * 60 * 60)
            return fallback

    def _get_client(self) -> BaseEphemerisClient:
        if self.provider == "swiss" and HAS_SWISSEPH:
            return SwissEphemerisClient()
        if self.provider == "nasa-horizons":
            return HorizonsEphemerisClient()
        if self.provider == "stub":
            return StubEphemerisClient()
        if HAS_SWISSEPH:
            return SwissEphemerisClient()
        return StubEphemerisClient()

