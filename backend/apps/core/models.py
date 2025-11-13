from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that tracks creation and update times.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)


class Location(TimeStampedModel):
    """
    Stores a normalized location with geographic coordinates and timezone.
    """

    name = models.CharField(max_length=255)
    city = models.CharField(max_length=128)
    state = models.CharField(max_length=128, blank=True)
    country = models.CharField(max_length=128)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
    )
    timezone = models.CharField(max_length=64)
    external_id = models.CharField(max_length=128, blank=True)

    class Meta:
        unique_together = ("city", "state", "country", "latitude", "longitude")
        ordering = ("country", "city")

    def __str__(self) -> str:
        components = [self.city, self.state, self.country]
        return ", ".join(filter(None, components))


class AuditLog(TimeStampedModel):
    """
    Lightweight audit trail for key domain events.
    """

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=128)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

