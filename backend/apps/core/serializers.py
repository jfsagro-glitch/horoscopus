from rest_framework import serializers

from apps.core.models import Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = (
            "id",
            "name",
            "city",
            "state",
            "country",
            "latitude",
            "longitude",
            "timezone",
            "external_id",
        )

