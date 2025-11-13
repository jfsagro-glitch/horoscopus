from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.core.models import Location
from apps.core.serializers import LocationSerializer
from apps.integrations.geocoding import GeocodingService


class LocationViewSet(viewsets.ModelViewSet):
    serializer_class = LocationSerializer
    queryset = Location.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filterset_fields = ("city", "country")
    search_fields = ("name", "city", "state", "country")

    @action(detail=False, methods=["get"], url_path="autocomplete")
    def autocomplete(self, request):
        query = request.query_params.get("q", "")
        limit = int(request.query_params.get("limit", 5))
        if not query:
            return Response([])
        service = GeocodingService()
        results = [
            {
                "id": result.location.id,
                "name": result.location.name,
                "city": result.location.city,
                "state": result.location.state,
                "country": result.location.country,
                "latitude": float(result.location.latitude),
                "longitude": float(result.location.longitude),
                "timezone": result.location.timezone,
                "score": result.score,
            }
            for result in service.autocomplete(query=query, limit=limit)
        ]
        return Response(results)

