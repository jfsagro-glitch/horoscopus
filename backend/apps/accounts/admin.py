from django.contrib import admin

from apps.accounts.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "birth_datetime",
        "birth_location",
        "current_location",
        "timezone",
        "created_at",
    )
    search_fields = ("user__email", "user__username")
    list_filter = ("timezone", "birth_location__country")
    autocomplete_fields = ("birth_location", "current_location")

