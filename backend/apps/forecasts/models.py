from __future__ import annotations

from django.db import models

from apps.charts.models import NatalChart
from apps.core.models import TimeStampedModel


class ForecastBatch(TimeStampedModel):
    class Horizon(models.TextChoices):
        DAY = "day", "Day"
        WEEK = "week", "Week"
        MONTH = "month", "Month"
        QUARTER = "quarter", "Quarter"
        YEAR = "year", "Year"
        FIVE_YEARS = "five_years", "5 Years"
        TEN_YEARS = "ten_years", "10 Years"
        THIRTY_YEARS = "thirty_years", "30 Years"

    chart = models.ForeignKey(
        NatalChart, on_delete=models.CASCADE, related_name="forecast_batches"
    )
    horizon = models.CharField(max_length=32, choices=Horizon.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=16,
        choices=(
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("ready", "Ready"),
            ("failed", "Failed"),
        ),
        default="pending",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-start_date",)
        unique_together = ("chart", "horizon", "start_date", "end_date")


class ForecastEntry(TimeStampedModel):
    batch = models.ForeignKey(
        ForecastBatch, on_delete=models.CASCADE, related_name="entries"
    )
    title = models.CharField(max_length=128)
    timeframe_start = models.DateTimeField()
    timeframe_end = models.DateTimeField()
    summary = models.TextField()
    opportunities = models.TextField(blank=True)
    challenges = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("timeframe_start",)

