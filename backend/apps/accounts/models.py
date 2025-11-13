from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.models import Location, TimeStampedModel


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    birth_datetime = models.DateTimeField()
    birth_location = models.ForeignKey(
        Location, on_delete=models.PROTECT, related_name="birth_profiles"
    )
    current_location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True, related_name="residents"
    )
    timezone = models.CharField(max_length=64)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self) -> str:
        return f"Profile for {self.user}"

