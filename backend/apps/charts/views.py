from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from apps.charts.models import NatalChart
from apps.charts.serializers import NatalChartSerializer
from apps.charts.tasks import compute_natal_chart_async


class NatalChartViewSet(viewsets.ModelViewSet):
    serializer_class = NatalChartSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return (
            NatalChart.objects.select_related("owner", "profile", "event_location")
            .prefetch_related(
                "planet_positions__body",
                "aspects__source_body",
                "aspects__target_body",
                "strength_metrics__body",
                "integral_indicators",
            )
            .filter(owner=self.request.user)
        )

    def perform_create(self, serializer):
        profile = serializer.validated_data.get("profile")
        if profile and profile.user != self.request.user:
            raise PermissionDenied("Профиль принадлежит другому пользователю.")
        chart = serializer.save(owner=self.request.user)
        compute_natal_chart_async.delay(chart_id=chart.id)

    @action(detail=True, methods=["post"])
    def recompute(self, request, pk=None):
        chart = self.get_object()
        compute_natal_chart_async.delay(chart_id=chart.id, force=True)
        return Response({"status": "queued"}, status=status.HTTP_202_ACCEPTED)

