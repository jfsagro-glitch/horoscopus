from rest_framework import serializers

from apps.forecasts.models import ForecastBatch, ForecastEntry


class ForecastEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ForecastEntry
        fields = (
            "id",
            "title",
            "timeframe_start",
            "timeframe_end",
            "summary",
            "opportunities",
            "challenges",
            "recommendations",
            "metadata",
            "created_at",
        )


class ForecastBatchSerializer(serializers.ModelSerializer):
    entries = ForecastEntrySerializer(many=True, read_only=True)

    class Meta:
        model = ForecastBatch
        fields = (
            "id",
            "chart",
            "horizon",
            "start_date",
            "end_date",
            "status",
            "metadata",
            "entries",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status", "metadata", "created_at", "updated_at")

