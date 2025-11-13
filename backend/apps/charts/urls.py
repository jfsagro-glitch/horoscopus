from rest_framework.routers import DefaultRouter

from apps.charts.views import NatalChartViewSet

router = DefaultRouter()
router.register(r"natal-charts", NatalChartViewSet, basename="natal-chart")

urlpatterns = router.urls

