from __future__ import annotations

import structlog
from celery import shared_task
from django.db import transaction

from apps.charts.models import NatalChart
from apps.charts import services

logger = structlog.get_logger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def compute_natal_chart_async(self, chart_id: int, force: bool = False) -> None:
    logger.info("charts.compute_natal_chart_async.started", chart_id=chart_id, force=force)
    with transaction.atomic():
        chart = NatalChart.objects.select_for_update().get(pk=chart_id)
        services.calculate_natal_chart(chart=chart, force=force)
    logger.info("charts.compute_natal_chart_async.completed", chart_id=chart_id)

