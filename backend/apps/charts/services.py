from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from math import fabs
from typing import Dict, Iterable, List

import structlog
from django.db import transaction

from apps.charts.models import (
    CelestialBody,
    NatalChart,
    PlanetPosition,
    PlanetStrength,
    Aspect,
    IntegralIndicator,
)
from apps.integrations.ephemeris import EphemerisClient
from apps.charts.interpretation import (
    generate_integral_insights,
    generate_planet_insights,
)
from apps.charts.interpretation.utils import ZONE_BY_SIGN

logger = structlog.get_logger(__name__)

SIGN_ELEMENTS = {
    "aries": "fire",
    "taurus": "earth",
    "gemini": "air",
    "cancer": "water",
    "leo": "fire",
    "virgo": "earth",
    "libra": "air",
    "scorpio": "water",
    "sagittarius": "fire",
    "capricorn": "earth",
    "aquarius": "air",
    "pisces": "water",
}

SIGN_MODALITIES = {
    "aries": "cardinal",
    "taurus": "fixed",
    "gemini": "mutable",
    "cancer": "cardinal",
    "leo": "fixed",
    "virgo": "mutable",
    "libra": "cardinal",
    "scorpio": "fixed",
    "sagittarius": "mutable",
    "capricorn": "cardinal",
    "aquarius": "fixed",
    "pisces": "mutable",
}

RULERSHIP = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "pluto",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "uranus",
    "pisces": "neptune",
}

DETRIMENT = {
    "aries": "venus",
    "taurus": "mars",
    "gemini": "jupiter",
    "cancer": "saturn",
    "leo": "saturn",
    "virgo": "neptune",
    "libra": "mars",
    "scorpio": "venus",
    "sagittarius": "mercury",
    "capricorn": "moon",
    "aquarius": "sun",
    "pisces": "mercury",
}

ASPECT_RULES = {
    Aspect.AspectType.CONJUNCTION: {"angle": 0.0, "orb": 8.0},
    Aspect.AspectType.OPPOSITION: {"angle": 180.0, "orb": 8.0},
    Aspect.AspectType.TRINE: {"angle": 120.0, "orb": 7.0},
    Aspect.AspectType.SQUARE: {"angle": 90.0, "orb": 7.0},
    Aspect.AspectType.SEXTILE: {"angle": 60.0, "orb": 5.0},
    Aspect.AspectType.QUINCUNX: {"angle": 150.0, "orb": 3.0},
    Aspect.AspectType.QUINTILE: {"angle": 72.0, "orb": 2.0},
    Aspect.AspectType.BIQUINTILE: {"angle": 144.0, "orb": 2.0},
    Aspect.AspectType.SEMISEXTILE: {"angle": 30.0, "orb": 2.0},
    Aspect.AspectType.SEMISQUARE: {"angle": 45.0, "orb": 2.0},
}


@dataclass
class ChartComputationResult:
    positions: Iterable[PlanetPosition]
    aspects: Iterable[Aspect]
    strengths: Iterable[PlanetStrength]
    indicators: Iterable[IntegralIndicator]
    metadata: dict


def calculate_natal_chart(chart: NatalChart, force: bool = False) -> None:
    """
    Pull ephemeris data, compute positions and derived metrics, populate storage.
    """
    logger.info("charts.calculate_natal_chart.started", chart_id=chart.id, force=force)

    if chart.planet_positions.exists() and not force:
        logger.info("charts.calculate_natal_chart.skipped", chart_id=chart.id)
        return

    ephemeris_client = EphemerisClient()
    data = ephemeris_client.get_natal_ephemeris(
        dt_utc=chart.event_datetime,
        location=chart.event_location,
    )
    computation = _run_bioastro_pipeline(chart=chart, ephemeris=data)

    with transaction.atomic():
        chart.planet_positions.all().delete()
        chart.aspects.all().delete()
        chart.strength_metrics.all().delete()
        chart.integral_indicators.all().delete()

        PlanetPosition.objects.bulk_create(computation.positions)
        Aspect.objects.bulk_create(computation.aspects)
        PlanetStrength.objects.bulk_create(computation.strengths)
        IntegralIndicator.objects.bulk_create(computation.indicators)

        chart.metadata = computation.metadata
        chart.save(update_fields=["metadata", "updated_at"])

    logger.info("charts.calculate_natal_chart.completed", chart_id=chart.id)


def _run_bioastro_pipeline(chart: NatalChart, ephemeris: dict) -> ChartComputationResult:
    bodies_data = ephemeris.get("bodies", {})
    houses = ephemeris.get("houses", {})
    cusps = houses.get("cusps", [n * 30.0 for n in range(1, 13)])
    angles = houses.get("angles", {})

    body_models = {
        body.slug: body
        for body in CelestialBody.objects.filter(slug__in=bodies_data.keys())
    }

    positions: List[PlanetPosition] = []
    raw_positions: List[dict] = []

    for slug, data in bodies_data.items():
        body = body_models.get(slug)
        if not body:
            logger.warning("charts.bioastro_pipeline.body_missing", slug=slug)
            continue
        longitude = Decimal(str(data.get("longitude", 0.0))).quantize(Decimal("0.001"))
        speed = data.get("speed")
        positions.append(
            PlanetPosition(
                chart=chart,
                body=body,
                sign=data.get("sign", ""),
                house=data.get("house", 1),
                absolute_degree=longitude,
                retrograde=data.get("retrograde", False),
                speed=Decimal(str(speed)).quantize(Decimal("0.00001")) if speed is not None else None,
            )
        )
        raw_positions.append(
            {
                "body": body,
                "slug": slug,
                "longitude": float(longitude),
                "sign": data.get("sign", ""),
                "house": data.get("house", 1),
                "retrograde": data.get("retrograde", False),
                "speed": speed or 0.0,
            }
        )

    aspects = _calculate_aspects(chart, raw_positions)
    strengths = _calculate_strengths(chart, raw_positions)
    indicators = _calculate_integral_indicators(chart, raw_positions)

    logger.debug(
        "charts.bioastro_pipeline.completed",
        chart_id=chart.id,
        house_system=chart.house_system,
        positions=len(positions),
        aspects=len(aspects),
    )
    planet_insights = generate_planet_insights(raw_positions)
    integral_insights = generate_integral_insights(
        [
            {
                "name": indicator.name,
                "category": indicator.category,
                "value": indicator.value,
            }
            for indicator in indicators
        ]
    )

    metadata = {
        "pipeline": "bioastro-2.0",
        "version": "0.2.0",
        "houses": {
            "cusps": [round(c, 3) for c in cusps],
            "angles": {key: round(value, 3) for key, value in angles.items()},
        },
        "source": ephemeris.get("source"),
        "interpretation": {
            "planets": planet_insights,
            "integral": integral_insights,
        },
    }
    return ChartComputationResult(
        positions=positions,
        aspects=aspects,
        strengths=strengths,
        indicators=indicators,
        metadata=metadata,
    )


def _calculate_aspects(chart: NatalChart, positions: List[dict]) -> List[Aspect]:
    results: List[Aspect] = []
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            a = positions[i]
            b = positions[j]
            angle = _angular_distance(a["longitude"], b["longitude"])
            for aspect_type, rule in ASPECT_RULES.items():
                diff = min(fabs(angle - rule["angle"]), fabs(360.0 - angle - rule["angle"]))
                if diff <= rule["orb"]:
                    intensity = max(0.0, 1 - (diff / rule["orb"]))
                    results.append(
                        Aspect(
                            chart=chart,
                            source_body=a["body"],
                            target_body=b["body"],
                            aspect_type=aspect_type,
                            orb=Decimal(str(diff)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                            intensity=Decimal(str(intensity)).quantize(
                                Decimal("0.01"), rounding=ROUND_HALF_UP
                            ),
                        )
                    )
                    break
    return results


def _angular_distance(a: float, b: float) -> float:
    diff = (a - b) % 360.0
    if diff > 180.0:
        diff = 360.0 - diff
    return diff


def _calculate_strengths(chart: NatalChart, positions: List[dict]) -> List[PlanetStrength]:
    strengths: List[PlanetStrength] = []
    for payload in positions:
        slug = payload["slug"]
        body = payload["body"]
        sign = payload["sign"]
        retrograde = payload["retrograde"]
        base = 50.0
        if RULERSHIP.get(sign) == slug:
            base += 20.0
        if DETRIMENT.get(sign) == slug:
            base -= 15.0
        if retrograde:
            base -= 10.0
        speed = payload["speed"]
        if abs(speed) > 1.0:
            base += 5.0

        score = max(0.0, min(100.0, base))
        strengths.append(
            PlanetStrength(
                chart=chart,
                body=body,
                metric_name="bio_strength",
                score=Decimal(str(score)).quantize(Decimal("0.001")),
                weight=Decimal("1.000"),
                metadata={
                    "sign": sign,
                    "retrograde": retrograde,
                    "speed": speed,
                },
            )
        )
    return strengths


def _calculate_integral_indicators(chart: NatalChart, positions: List[dict]) -> List[IntegralIndicator]:
    element_totals: Dict[str, float] = {"fire": 0.0, "earth": 0.0, "air": 0.0, "water": 0.0}
    modality_totals: Dict[str, float] = {"cardinal": 0.0, "fixed": 0.0, "mutable": 0.0}
    zone_totals: Dict[str, float] = {"first_zone": 0.0, "second_zone": 0.0, "third_zone": 0.0}

    for payload in positions:
        sign = payload["sign"]
        weight = 1.0
        element = SIGN_ELEMENTS.get(sign)
        modality = SIGN_MODALITIES.get(sign)
        zone = ZONE_BY_SIGN.get(sign)
        if element:
            element_totals[element] += weight
        if modality:
            modality_totals[modality] += weight
        if zone:
            zone_totals[zone] += weight

    total_weight = sum(element_totals.values()) or 1.0
    total_modality = sum(modality_totals.values()) or 1.0
    total_zones = sum(zone_totals.values()) or 1.0

    indicators: List[IntegralIndicator] = []
    for element, value in element_totals.items():
        indicators.append(
            IntegralIndicator(
                chart=chart,
                name=element,
                category="element",
                value=Decimal(str((value / total_weight) * 100)).quantize(Decimal("0.01")),
                metadata={},
            )
        )
    for modality, value in modality_totals.items():
        indicators.append(
            IntegralIndicator(
                chart=chart,
                name=modality,
                category="modality",
                value=Decimal(str((value / total_modality) * 100)).quantize(Decimal("0.01")),
                metadata={},
            )
        )
    for zone, value in zone_totals.items():
        indicators.append(
            IntegralIndicator(
                chart=chart,
                name=zone,
                category="zone",
                value=Decimal(str((value / total_zones) * 100)).quantize(Decimal("0.01")),
                metadata={},
            )
        )
    return indicators

