from rest_framework.routers import DefaultRouter

from apps.reports.views import ReportViewSet

router = DefaultRouter()
router.register(r"reports", ReportViewSet, basename="reports")

urlpatterns = router.urls

