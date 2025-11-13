from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.reports.models import Report
from apps.reports.serializers import ReportSerializer
from apps.reports.tasks import generate_report_async


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Report.objects.filter(owner=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        chart = serializer.validated_data.get("chart")
        forecast_batch = serializer.validated_data.get("forecast_batch")
        if chart and chart.owner != self.request.user:
            raise PermissionDenied("Нельзя создавать отчет по чужой карте.")
        if forecast_batch and forecast_batch.chart.owner != self.request.user:
            raise PermissionDenied("Нельзя создавать отчет по чужому прогнозу.")
        if not chart and not forecast_batch:
            raise ValidationError("Необходимо указать карту или прогноз для создания отчета.")
        report = serializer.save(owner=self.request.user)
        generate_report_async.delay(report_id=report.id)

    @action(detail=True, methods=["post"])
    def regenerate(self, request, pk=None):
        report = self.get_object()
        generate_report_async.delay(report_id=report.id, force=True)
        return Response({"status": "queued"}, status=status.HTTP_202_ACCEPTED)

