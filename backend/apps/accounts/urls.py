from rest_framework.routers import DefaultRouter

from apps.accounts.views import UserProfileViewSet

router = DefaultRouter()
router.register(r"profiles", UserProfileViewSet, basename="user-profile")

urlpatterns = router.urls

