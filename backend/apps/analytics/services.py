from __future__ import annotations

import structlog

from apps.analytics.models import UsageMetric

logger = structlog.get_logger(__name__)


def record_metric(key: str, value: float, **labels) -> None:
    UsageMetric.objects.create(key=key, value=value, labels=labels)
    logger.info("analytics.metric.recorded", key=key, value=value, labels=labels)

