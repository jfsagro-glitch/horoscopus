from __future__ import annotations

import datetime as dt
from typing import Iterable

import structlog
from django.utils import timezone

from apps.forecasts.models import ForecastBatch, ForecastEntry

logger = structlog.get_logger(__name__)


def generate_forecast_batch(batch: ForecastBatch, force: bool = False) -> None:
    if batch.entries.exists() and not force:
        logger.info("forecasts.generate_forecast_batch.skipped", batch_id=batch.id)
        return

    logger.info("forecasts.generate_forecast_batch.processing", batch_id=batch.id)
    batch.status = "processing"
    batch.save(update_fields=["status", "updated_at"])

    entries = _compute_entries(batch)

    batch.entries.all().delete()
    ForecastEntry.objects.bulk_create(entries)

    batch.status = "ready"
    batch.metadata = {"generated_at": timezone.now().isoformat()}
    batch.save(update_fields=["status", "metadata", "updated_at"])


def _compute_entries(batch: ForecastBatch) -> Iterable[ForecastEntry]:
    logger.warning(
        "forecasts.compute_entries.stub",
        batch_id=batch.id,
        chart_id=batch.chart_id,
        horizon=batch.horizon,
    )
    timeframe = dt.datetime.combine(batch.start_date, dt.time(), tzinfo=timezone.utc)
    entry = ForecastEntry(
        batch=batch,
        title=f"{batch.get_horizon_display()} forecast",
        timeframe_start=timeframe,
        timeframe_end=timeframe,
        summary="Прогноз будет сформирован после интеграции с BioAstrology 2.0.",
        opportunities="",
        challenges="",
        recommendations="",
        metadata={"engine": "bioastro-2.0", "version": "0.1.0"},
    )
    return [entry]

