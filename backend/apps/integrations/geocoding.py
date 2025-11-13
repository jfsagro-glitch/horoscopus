from __future__ import annotations

import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, List

import requests
import structlog
from django.conf import settings
from django.core.cache import cache
from django.db import transaction

from apps.core.models import Location

logger = structlog.get_logger(__name__)


@dataclass
class GeocodingResult:
    location: Location
    score: float


class BaseGeocoder:
    name: str = "base"
    rate_limit_seconds: float = 1.0
    _last_call: float = 0.0

    def autocomplete(self, query: str, limit: int = 5) -> List[GeocodingResult]:
        raise NotImplementedError

    def _respect_rate_limit(self) -> None:
        delta = time.monotonic() - self._last_call
        if delta < self.rate_limit_seconds:
            time.sleep(self.rate_limit_seconds - delta)
        self._last_call = time.monotonic()


class NominatimGeocoder(BaseGeocoder):
    name = "nominatim"
    base_url: str

    def __init__(self) -> None:
        self.base_url = settings.NOMINATIM_BASE_URL

    def autocomplete(self, query: str, limit: int = 5) -> List[GeocodingResult]:
        self._respect_rate_limit()
        params = {
            "q": query,
            "format": "jsonv2",
            "limit": limit,
            "addressdetails": 1,
            "extratags": 1,
        }
        headers = {"User-Agent": settings.NOMINATIM_USER_AGENT}

        response = requests.get(self.base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        results: List[GeocodingResult] = []
        for item in data:
            try:
                result = self._build_location(item)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("integrations.geocoding.nominatim.skip", reason=str(exc))
                continue
            results.append(result)
        return results

    def _build_location(self, payload: dict) -> GeocodingResult:
        lat = Decimal(payload["lat"])
        lon = Decimal(payload["lon"])
        address = payload.get("address", {})
        name = payload.get("display_name", "")
        city = address.get("city") or address.get("town") or address.get("village") or address.get("hamlet") or ""
        country = address.get("country") or ""
        state = address.get("state") or address.get("region") or ""
        timezone = payload.get("extratags", {}).get("timezone") or ""
        if not timezone:
            raise ValueError("timezone not provided")

        with transaction.atomic():
            location, _ = Location.objects.get_or_create(
                latitude=lat.quantize(Decimal("0.000001")),
                longitude=lon.quantize(Decimal("0.000001")),
                defaults={
                    "name": name[:255] or city or country,
                    "city": city[:128],
                    "state": state[:128],
                    "country": country[:128],
                    "timezone": timezone,
                    "external_id": f"osm:{payload.get('osm_id')}",
                },
            )
            # Refresh metadata if missing
            updated_fields = []
            if not location.name and name:
                location.name = name[:255]
                updated_fields.append("name")
            if not location.state and state:
                location.state = state[:128]
                updated_fields.append("state")
            if timezone and location.timezone != timezone:
                location.timezone = timezone
                updated_fields.append("timezone")
            if updated_fields:
                location.save(update_fields=updated_fields + ["updated_at"])

        score = float(payload.get("importance", 0.0))
        return GeocodingResult(location=location, score=score)


class GeoapifyGeocoder(BaseGeocoder):
    name = "geoapify"
    rate_limit_seconds = 0.2
    endpoint = "https://api.geoapify.com/v1/geocode/autocomplete"

    def autocomplete(self, query: str, limit: int = 5) -> List[GeocodingResult]:
        api_key = settings.GEOAPIFY_API_KEY
        if not api_key:
            logger.debug("integrations.geocoding.geoapify.disabled")
            return []
        self._respect_rate_limit()
        params = {
            "text": query,
            "apiKey": api_key,
            "limit": limit,
        }
        response = requests.get(self.endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        features = data.get("features", [])
        results: List[GeocodingResult] = []
        for feature in features:
            properties = feature.get("properties", {})
            if "lat" not in properties or "lon" not in properties:
                continue
            timezone = properties.get("timezone") or "UTC"
            location, _ = Location.objects.get_or_create(
                latitude=Decimal(str(properties["lat"])).quantize(Decimal("0.000001")),
                longitude=Decimal(str(properties["lon"])).quantize(Decimal("0.000001")),
                defaults={
                    "name": properties.get("formatted")[:255],
                    "city": properties.get("city", "")[:128],
                    "state": properties.get("state", "")[:128],
                    "country": properties.get("country", "")[:128],
                    "timezone": timezone,
                    "external_id": f"geoapify:{properties.get('place_id')}",
                },
            )
            results.append(
                GeocodingResult(
                    location=location,
                    score=float(properties.get("rank", {}).get("confidence", 0.0)),
                )
            )
        return results


class GoogleGeocoder(BaseGeocoder):
    name = "google"
    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"

    def autocomplete(self, query: str, limit: int = 5) -> List[GeocodingResult]:
        api_key = settings.GOOGLE_GEOCODING_API_KEY
        if not api_key:
            logger.debug("integrations.geocoding.google.disabled")
            return []
        self._respect_rate_limit()
        params = {
            "address": query,
            "key": api_key,
        }
        response = requests.get(self.endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "OK":
            logger.warning("integrations.geocoding.google.status", status=data.get("status"))
            return []
        results: List[GeocodingResult] = []
        for result in data.get("results", [])[:limit]:
            geometry = result.get("geometry", {}).get("location", {})
            if not geometry:
                continue
            lat = Decimal(str(geometry["lat"])).quantize(Decimal("0.000001"))
            lon = Decimal(str(geometry["lng"])).quantize(Decimal("0.000001"))
            address_components = {comp["types"][0]: comp["long_name"] for comp in result.get("address_components", []) if comp.get("types")}
            timezone = result.get("timezone") or "UTC"  # Requires additional API call; placeholder

            location, _ = Location.objects.get_or_create(
                latitude=lat,
                longitude=lon,
                defaults={
                    "name": result.get("formatted_address", "")[:255],
                    "city": address_components.get("locality", "")[:128],
                    "state": address_components.get("administrative_area_level_1", "")[:128],
                    "country": address_components.get("country", "")[:128],
                    "timezone": timezone or "",
                    "external_id": f"google:{result.get('place_id')}",
                },
            )
            results.append(
                GeocodingResult(
                    location=location,
                    score=float(result.get("geometry", {}).get("location_type") == "ROOFTOP"),
                )
            )
        return results


class GeocodingService:
    cache_timeout = 30 * 24 * 60 * 60  # 30 дней

    def __init__(self) -> None:
        self.providers: List[BaseGeocoder] = self._build_providers()

    def autocomplete(self, query: str, limit: int = 5) -> List[GeocodingResult]:
        query_normalised = query.strip()
        if not query_normalised:
            return []

        cache_key = f"geocode:{query_normalised.lower()}:{limit}"
        cached_ids = cache.get(cache_key)
        if cached_ids:
            locations = Location.objects.in_bulk([item["id"] for item in cached_ids])
            logger.debug("integrations.geocoding.cache.hit", key=cache_key)
            return [
                GeocodingResult(location=locations[item["id"]], score=item["score"])
                for item in cached_ids
                if item["id"] in locations
            ]

        for provider in self.providers:
            try:
                results = provider.autocomplete(query_normalised, limit)
            except requests.RequestException as exc:
                logger.warning(
                    "integrations.geocoding.provider.error",
                    provider=provider.name,
                    error=str(exc),
                )
                continue
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning(
                    "integrations.geocoding.provider.error",
                    provider=provider.name,
                    error=str(exc),
                )
                continue
            if results:
                payload = [{"id": result.location.id, "score": result.score} for result in results]
                cache.set(cache_key, payload, timeout=self.cache_timeout)
                logger.info("integrations.geocoding.cache.store", provider=provider.name, key=cache_key)
                return results

        return []

    def _build_providers(self) -> List[BaseGeocoder]:
        mapping = {
            "nominatim": NominatimGeocoder(),
            "geoapify": GeoapifyGeocoder(),
            "google": GoogleGeocoder(),
        }
        ordered = [
            settings.GEOCODING_PRIMARY,
            settings.GEOCODING_FALLBACK,
            settings.GEOCODING_SECOND_FALLBACK,
        ]
        providers: List[BaseGeocoder] = []
        for name in ordered:
            provider = mapping.get(name)
            if provider and provider not in providers:
                providers.append(provider)
        if not providers:
            providers.append(NominatimGeocoder())
        return providers
