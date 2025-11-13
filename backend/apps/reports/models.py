from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.charts.models import NatalChart
from apps.core.models import TimeStampedModel
from apps.forecasts.models import ForecastBatch


class Report(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        GENERATING = "generating", "Generating"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports"
    )
    chart = models.ForeignKey(
        NatalChart, on_delete=models.CASCADE, related_name="reports", null=True, blank=True
    )
    forecast_batch = models.ForeignKey(
        ForecastBatch,
        on_delete=models.CASCADE,
        related_name="reports",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=128)
    template = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    file = models.FileField(upload_to="reports/", blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)

