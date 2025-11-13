from __future__ import annotations

from io import BytesIO
from typing import Any, Dict

import structlog
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils import timezone

from apps.charts.models import NatalChart
from apps.reports.models import Report

logger = structlog.get_logger(__name__)

try:  # pragma: no cover - optional dependency
    from weasyprint import HTML

    HAS_WEASYPRINT = True
except Exception:  # pragma: no cover - optional dependency
    HAS_WEASYPRINT = False


def generate_report(report: Report, force: bool = False) -> None:
    if report.status == Report.Status.READY and not force:
        logger.info("reports.generate_report.skipped", report_id=report.id)
        return

    logger.info("reports.generate_report.started", report_id=report.id)
    report.status = Report.Status.GENERATING
    report.save(update_fields=["status", "updated_at"])

    context = _build_context(report)
    pdf_bytes, engine = _render_pdf(report, context)

    report.file.save(
        f"report-{report.id}.pdf",
        ContentFile(pdf_bytes),
        save=False,
    )
    report.status = Report.Status.READY
    report.metadata = {
        "engine": engine,
        "generated_at": timezone.now().isoformat(),
        "context": {"chart_id": report.chart_id, "forecast_id": report.forecast_batch_id},
    }
    report.save(update_fields=["file", "status", "metadata", "updated_at"])

    logger.info("reports.generate_report.completed", report_id=report.id)


def _build_context(report: Report) -> Dict[str, Any]:
    chart = report.chart
    forecast = report.forecast_batch
    positions = []
    aspects = []
    strengths = []
    indicators = []

    if chart:
        chart = (
            NatalChart.objects.prefetch_related(
                "planet_positions__body",
                "aspects__source_body",
                "aspects__target_body",
                "strength_metrics__body",
                "integral_indicators",
            )
            .select_related("owner")
            .get(pk=chart.pk)
        )
        positions = chart.planet_positions.all()
        aspects = chart.aspects.all()
        strengths = chart.strength_metrics.all()
        indicators = chart.integral_indicators.all()

    return {
        "report": report,
        "chart": chart,
        "forecast": forecast,
        "owner": report.owner,
        "positions": positions,
        "aspects": aspects,
        "strengths": strengths,
        "indicators": indicators,
        "generated_at": timezone.now(),
    }


def _render_pdf(report: Report, context: Dict[str, Any]) -> tuple[bytes, str]:
    engine = settings.REPORTS_PDF_ENGINE.lower()
    template_name = report.template or "reports/natal_report.html"

    if engine == "weasyprint":
        if not HAS_WEASYPRINT:
            logger.warning(
                "reports.render_pdf.weasyprint_unavailable",
                template=template_name,
            )
            return _render_plain_text(context, template_name), "plaintext"
        html = render_to_string(template_name, context)
        pdf_bytes = HTML(string=html, base_url=str(settings.BASE_DIR)).write_pdf()
        return pdf_bytes, "weasyprint"

    if engine == "reportlab":  # pragma: no cover - optional branch
        return _render_reportlab(context), "reportlab"

    # fallback plain text for unsupported engines
    return _render_plain_text(context, template_name), "plaintext"


def _render_reportlab(context: Dict[str, Any]) -> bytes:  # pragma: no cover - heavy dependency
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Horoscopus Report")
    pdf.drawString(50, 750, "Horoscopus Report")
    pdf.drawString(50, 735, f"Generated: {context['generated_at'].isoformat()}")
    if context["chart"]:
        pdf.drawString(50, 705, f"Chart title: {context['chart'].title}")
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.read()


def _render_plain_text(context: Dict[str, Any], template: str) -> bytes:
    buffer = BytesIO()
    buffer.write(f"Horoscopus Report\nTemplate: {template}\n".encode("utf-8"))
    chart = context.get("chart")
    if chart:
        buffer.write(f"Chart: {chart.title} ({chart.event_datetime:%Y-%m-%d %H:%M})\n".encode("utf-8"))
    buffer.seek(0)
    return buffer.read()

