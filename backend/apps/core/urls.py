from rest_framework.routers import DefaultRouter

from apps.core.views import LocationViewSet

router = DefaultRouter()
router.register(r"locations", LocationViewSet, basename="location")

urlpatterns = router.urls

