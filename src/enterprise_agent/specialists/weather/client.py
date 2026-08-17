"""Open-Meteo HTTP client. No API key."""

from __future__ import annotations

from enterprise_agent.core.http import compact_json, http_get_json

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def get(url: str, **params) -> dict:
    return http_get_json(url, **params)


__all__ = ["AIR_QUALITY_URL", "FORECAST_URL", "GEOCODE_URL", "compact_json", "get"]
