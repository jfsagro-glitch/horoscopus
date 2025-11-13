from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.accounts.models import UserProfile
from apps.core.models import Location, TimeStampedModel


class CelestialBody(TimeStampedModel):
    class BodyType(models.TextChoices):
        PLANET = "planet", "Planet"
        LUMINAR = "luminar", "Luminar"
        NODE = "node", "Node"
        DWARF = "dwarf", "Dwarf planet"
        ASTEROID = "asteroid", "Asteroid"
        POINT = "point", "Calculated point"

    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, unique=True)
    body_type = models.CharField(
        max_length=16, choices=BodyType.choices, default=BodyType.PLANET
    )
    symbol = models.CharField(max_length=16, blank=True)
    is_retrograde_capable = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class NatalChart(TimeStampedModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="natal_charts"
    )
    profile = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="natal_charts",
    )
    title = models.CharField(max_length=128, default="Natal Chart")
    event_datetime = models.DateTimeField()
    event_location = models.ForeignKey(
        Location, on_delete=models.PROTECT, related_name="natal_charts"
    )
    house_system = models.CharField(max_length=32, default="placidus")
    notes = models.TextField(blank=True)
    calculation_version = models.CharField(max_length=32, default="bioastro-2.0")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-event_datetime",)

    def __str__(self) -> str:
        return f"{self.title} ({self.event_datetime:%Y-%m-%d})"


class PlanetPosition(TimeStampedModel):
    chart = models.ForeignKey(
        NatalChart, on_delete=models.CASCADE, related_name="planet_positions"
    )
    body = models.ForeignKey(
        CelestialBody, on_delete=models.CASCADE, related_name="positions"
    )
    sign = models.CharField(max_length=16)
    house = models.PositiveSmallIntegerField()
    absolute_degree = models.DecimalField(max_digits=6, decimal_places=3)
    retrograde = models.BooleanField(default=False)
    speed = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True)

    class Meta:
        unique_together = ("chart", "body")
        ordering = ("chart", "body")

    def __str__(self) -> str:
        return f"{self.body} in {self.sign} (House {self.house})"


class Aspect(TimeStampedModel):
    class AspectType(models.TextChoices):
        CONJUNCTION = "conjunction", "Conjunction"
        OPPOSITION = "opposition", "Opposition"
        TRINE = "trine", "Trine"
        SQUARE = "square", "Square"
        SEXTILE = "sextile", "Sextile"
        QUINCUNX = "quincunx", "Quincunx"
        SEMISEXTILE = "semisextile", "Semi-sextile"
        SEMISQUARE = "semisquare", "Semi-square"
        QUINTILE = "quintile", "Quintile"
        BIQUINTILE = "biquintile", "Bi-quintile"

    chart = models.ForeignKey(
        NatalChart, on_delete=models.CASCADE, related_name="aspects"
    )
    source_body = models.ForeignKey(
        CelestialBody,
        on_delete=models.CASCADE,
        related_name="aspect_sources",
    )
    target_body = models.ForeignKey(
        CelestialBody,
        on_delete=models.CASCADE,
        related_name="aspect_targets",
    )
    aspect_type = models.CharField(max_length=32, choices=AspectType.choices)
    orb = models.DecimalField(max_digits=5, decimal_places=2)
    intensity = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = ("chart", "source_body", "target_body", "aspect_type")
        ordering = ("chart", "source_body__name")

    def __str__(self) -> str:
        return f"{self.source_body} - {self.target_body} ({self.aspect_type})"


class PlanetStrength(TimeStampedModel):
    chart = models.ForeignKey(
        NatalChart, on_delete=models.CASCADE, related_name="strength_metrics"
    )
    body = models.ForeignKey(
        CelestialBody, on_delete=models.CASCADE, related_name="strength_metrics"
    )
    metric_name = models.CharField(max_length=64)
    score = models.DecimalField(max_digits=6, decimal_places=3)
    weight = models.DecimalField(max_digits=4, decimal_places=3, default=1.0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("chart", "body", "metric_name")
        ordering = ("chart", "body", "-score")


class IntegralIndicator(TimeStampedModel):
    chart = models.ForeignKey(
        NatalChart, on_delete=models.CASCADE, related_name="integral_indicators"
    )
    name = models.CharField(max_length=64)
    category = models.CharField(max_length=32)
    value = models.DecimalField(max_digits=6, decimal_places=3)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("chart", "name", "category")
        ordering = ("chart", "category", "name")

