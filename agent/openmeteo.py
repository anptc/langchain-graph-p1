"""Open-Meteo HTTP helper. No API key."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def get(url: str, **params) -> dict:
    payload = {k: v for k, v in params.items() if v is not None and v != ""}
    full = f"{url}?{urllib.parse.urlencode(payload, doseq=True)}"
    request = urllib.request.Request(full, headers={"User-Agent": "langchain-graph-p1"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        return {"error": f"HTTP {exc.code}", "body": exc.read().decode()[:500]}
    except urllib.error.URLError as exc:
        return {"error": str(exc.reason)}


def compact_json(data: dict, max_chars: int = 4000) -> str:
    text = json.dumps(data, indent=2, default=str)
    if len(text) > max_chars:
        return text[:max_chars] + "\n...[truncated]"
    return text
