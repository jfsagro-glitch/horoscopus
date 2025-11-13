from rest_framework import serializers

from apps.accounts.models import UserProfile
from apps.core.models import Location


class UserProfileSerializer(serializers.ModelSerializer):
    birth_location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), write_only=True
    )
    birth_location_detail = serializers.SerializerMethodField(read_only=True)
    current_location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), allow_null=True, required=False, write_only=True
    )
    current_location_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "user",
            "birth_datetime",
            "birth_location",
            "birth_location",
            "birth_location_detail",
            "current_location",
            "current_location_detail",
            "timezone",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("user", "created_at", "updated_at")

    def get_birth_location_detail(self, obj):
        return self._serialize_location(obj.birth_location)

    def get_current_location_detail(self, obj):
        if obj.current_location is None:
            return None
        return self._serialize_location(obj.current_location)

    def _serialize_location(self, location: Location):
        return {
            "id": location.id,
            "name": location.name,
            "city": location.city,
            "state": location.state,
            "country": location.country,
            "timezone": location.timezone,
        }

