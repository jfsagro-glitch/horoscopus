from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from apps.forecasts.models import ForecastBatch
from apps.forecasts.serializers import ForecastBatchSerializer
from apps.forecasts.tasks import generate_forecast_batch_async


class ForecastBatchViewSet(viewsets.ModelViewSet):
    serializer_class = ForecastBatchSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return (
            ForecastBatch.objects.select_related("chart", "chart__owner")
            .prefetch_related("entries")
            .filter(chart__owner=self.request.user)
        )

    def perform_create(self, serializer):
        chart = serializer.validated_data["chart"]
        if chart.owner != self.request.user:
            raise PermissionDenied("Нельзя создавать прогнозы для чужой карты.")
        batch = serializer.save()
        generate_forecast_batch_async.delay(batch_id=batch.id)

    @action(detail=True, methods=["post"])
    def regenerate(self, request, pk=None):
        batch = self.get_object()
        generate_forecast_batch_async.delay(batch_id=batch.id, force=True)
        return Response({"status": "queued"}, status=status.HTTP_202_ACCEPTED)

