from rest_framework import serializers

from apps.reports.models import Report


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = (
            "id",
            "owner",
            "chart",
            "forecast_batch",
            "title",
            "template",
            "status",
            "file",
            "metadata",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("owner", "status", "file", "metadata", "created_at", "updated_at")

