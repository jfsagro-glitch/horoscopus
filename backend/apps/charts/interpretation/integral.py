from decimal import Decimal
from typing import Any, Dict, Iterable, Optional

from apps.charts.knowledge import INTEGRAL_INDICATORS_KNOWLEDGE

from .utils import CROSS_NAMES, ELEMENT_NAMES, ZONE_NAMES


def generate_integral_insights(indicators: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    elements: Dict[str, float] = {}
    crosses: Dict[str, float] = {}
    zones: Dict[str, float] = {}

    for indicator in indicators:
        value = indicator.get("value")
        if isinstance(value, Decimal):
            value = float(value)
        elif isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                value = None
        if value is None:
            continue

        category = indicator.get("category")
        name = indicator.get("name")
        if category == "element":
            elements[name] = value
        elif category == "modality":
            crosses[name] = value
        elif category == "zone":
            zones[name] = value

    knowledge = INTEGRAL_INDICATORS_KNOWLEDGE

    return {
        "elements": _build_category_block(
            values=elements,
            knowledge=knowledge["elements"],
            label_map=ELEMENT_NAMES,
        ),
        "crosses": _build_category_block(
            values=crosses,
            knowledge=knowledge["crosses"],
            label_map=CROSS_NAMES,
        ),
        "zones": _build_category_block(
            values=zones,
            knowledge=knowledge["zones"],
            label_map=ZONE_NAMES,
        ),
        "practical_application": knowledge.get("practical_application"),
        "therapeutic_approaches": knowledge.get("practical_application", {}).get(
            "therapeutic_approaches"
        ),
    }


def _build_category_block(
    values: Dict[str, float],
    knowledge: Dict[str, Any],
    label_map: Dict[str, str],
) -> Dict[str, Any]:
    dominant_key = _get_dominant_key(values)
    return {
        "values": {label_map.get(k, k): v for k, v in values.items()},
        "dominant": {
            "key": dominant_key,
            "label": label_map.get(dominant_key, dominant_key) if dominant_key else None,
            "knowledge": _get_knowledge_for_key(knowledge, dominant_key),
        },
        "knowledge": knowledge,
    }


def _get_dominant_key(values: Dict[str, float]) -> Optional[str]:
    if not values:
        return None
    return max(values, key=values.get)


def _get_knowledge_for_key(knowledge: Dict[str, Any], key: Optional[str]) -> Optional[Dict[str, Any]]:
    if not key:
        return None
    return knowledge.get(key)

