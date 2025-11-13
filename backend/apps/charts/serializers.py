from rest_framework import serializers

from apps.charts.models import (
    Aspect,
    CelestialBody,
    IntegralIndicator,
    NatalChart,
    PlanetPosition,
    PlanetStrength,
)


class CelestialBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = CelestialBody
        fields = ("id", "name", "slug", "body_type", "symbol", "is_retrograde_capable")


class PlanetPositionSerializer(serializers.ModelSerializer):
    body = CelestialBodySerializer()

    class Meta:
        model = PlanetPosition
        fields = (
            "id",
            "body",
            "sign",
            "house",
            "absolute_degree",
            "retrograde",
            "speed",
            "created_at",
        )


class AspectSerializer(serializers.ModelSerializer):
    source_body = CelestialBodySerializer()
    target_body = CelestialBodySerializer()

    class Meta:
        model = Aspect
        fields = (
            "id",
            "source_body",
            "target_body",
            "aspect_type",
            "orb",
            "intensity",
            "created_at",
        )


class PlanetStrengthSerializer(serializers.ModelSerializer):
    body = CelestialBodySerializer()

    class Meta:
        model = PlanetStrength
        fields = (
            "id",
            "body",
            "metric_name",
            "score",
            "weight",
            "metadata",
            "created_at",
        )


class IntegralIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegralIndicator
        fields = (
            "id",
            "name",
            "category",
            "value",
            "metadata",
            "created_at",
        )


class NatalChartSerializer(serializers.ModelSerializer):
    planet_positions = PlanetPositionSerializer(many=True, read_only=True)
    aspects = AspectSerializer(many=True, read_only=True)
    strength_metrics = PlanetStrengthSerializer(many=True, read_only=True)
    integral_indicators = IntegralIndicatorSerializer(many=True, read_only=True)
    event_location_detail = serializers.SerializerMethodField(read_only=True)
    profile_detail = serializers.SerializerMethodField(read_only=True)

    def get_event_location_detail(self, obj):
        location = obj.event_location
        return {
            "id": location.id,
            "name": location.name,
            "city": location.city,
            "state": location.state,
            "country": location.country,
            "timezone": location.timezone,
        }

    def get_profile_detail(self, obj):
        profile = obj.profile
        if profile is None:
            return None
        return {
            "id": profile.id,
            "birth_datetime": profile.birth_datetime,
            "timezone": profile.timezone,
        }

    class Meta:
        model = NatalChart
        fields = (
            "id",
            "owner",
            "profile",
            "profile_detail",
            "title",
            "event_datetime",
            "event_location",
            "event_location_detail",
            "house_system",
            "notes",
            "calculation_version",
            "metadata",
            "planet_positions",
            "aspects",
            "strength_metrics",
            "integral_indicators",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "owner",
            "calculation_version",
            "metadata",
            "created_at",
            "updated_at",
        )

