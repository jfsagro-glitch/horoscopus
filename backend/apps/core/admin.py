from django.contrib import admin

from apps.core.models import AuditLog, Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "state", "country", "timezone")
    search_fields = ("name", "city", "state", "country")
    list_filter = ("country", "timezone")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "created_at")
    search_fields = ("action", "metadata")
    autocomplete_fields = ("actor",)

