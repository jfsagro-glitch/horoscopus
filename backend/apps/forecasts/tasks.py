from __future__ import annotations

import structlog
from celery import shared_task
from django.db import transaction

from apps.forecasts import services
from apps.forecasts.models import ForecastBatch

logger = structlog.get_logger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def generate_forecast_batch_async(self, batch_id: int, force: bool = False) -> None:
    logger.info("forecasts.generate_forecast_batch_async.started", batch_id=batch_id, force=force)
    with transaction.atomic():
        batch = ForecastBatch.objects.select_for_update().get(pk=batch_id)
        services.generate_forecast_batch(batch=batch, force=force)
    logger.info("forecasts.generate_forecast_batch_async.completed", batch_id=batch_id)

