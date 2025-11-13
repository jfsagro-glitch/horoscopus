from __future__ import annotations

import structlog
from celery import shared_task
from django.db import transaction

from apps.reports import services
from apps.reports.models import Report

logger = structlog.get_logger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def generate_report_async(self, report_id: int, force: bool = False) -> None:
    logger.info("reports.generate_report_async.started", report_id=report_id, force=force)
    with transaction.atomic():
        report = Report.objects.select_for_update().get(pk=report_id)
        services.generate_report(report=report, force=force)
    logger.info("reports.generate_report_async.completed", report_id=report_id)

