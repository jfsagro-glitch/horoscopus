from rest_framework.routers import DefaultRouter

from apps.forecasts.views import ForecastBatchViewSet

router = DefaultRouter()
router.register(r"forecasts", ForecastBatchViewSet, basename="forecast-batch")

urlpatterns = router.urls

