from django.db import models

from apps.core.models import TimeStampedModel


class UsageMetric(TimeStampedModel):
    key = models.CharField(max_length=128)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    labels = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["key"])]

