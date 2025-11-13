from rest_framework import permissions, viewsets

from apps.accounts.models import UserProfile
from apps.accounts.serializers import UserProfileSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return (
            UserProfile.objects.select_related(
                "user",
                "birth_location",
                "current_location",
            )
            .filter(user=self.request.user)
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

