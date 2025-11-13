from typing import Any, Dict, Iterable, List, Optional

from apps.charts.knowledge import PLANET_KNOWLEDGE

from .utils import HOUSE_KEYS, SIGN_TRANSLATIONS


def generate_planet_insights(positions: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Produce knowledge-based interpretations for natal planet positions.
    """
    insights: List[Dict[str, Any]] = []

    for position in positions:
        slug: str = position.get("slug") or position.get("body_slug") or ""
        knowledge = PLANET_KNOWLEDGE.get(slug)
        if not knowledge:
            continue

        sign_ru = SIGN_TRANSLATIONS.get(position.get("sign", "").lower())
        sign_data: Optional[Dict[str, Any]] = (
            knowledge.get("in_signs_detailed", {}).get(sign_ru) if sign_ru else None
        )

        house_key = HOUSE_KEYS.get(position.get("house"))
        house_data: Optional[Dict[str, Any]] = (
            knowledge.get("in_houses_detailed", {}).get(house_key) if house_key else None
        )

        spectrum = knowledge.get("functional_spectrum")
        retrograde_data = (
            knowledge.get("retrograde_interpretation") if position.get("retrograde") else None
        )

        insights.append(
            {
                "slug": slug,
                "sign": position.get("sign"),
                "house": position.get("house"),
                "retrograde": position.get("retrograde"),
                "core_essence": knowledge.get("core_essence"),
                "functional_spectrum": spectrum,
                "sign_expression": sign_data,
                "house_expression": house_data,
                "aspects_interpretation": knowledge.get("aspects_interpretation"),
                "strength_assessment": knowledge.get("strength_assessment"),
                "retrograde_interpretation": retrograde_data,
            }
        )

    return insights

