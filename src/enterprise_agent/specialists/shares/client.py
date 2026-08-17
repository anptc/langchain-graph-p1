"""Alpha Vantage HTTP client. Key comes from settings, never from the model."""

from __future__ import annotations

from enterprise_agent.core.config import get_settings
from enterprise_agent.core.errors import ConfigurationError
from enterprise_agent.core.http import compact_json, http_get_json

BASE_URL = "https://www.alphavantage.co/query"


def query(**params) -> dict:
    key = (get_settings().alphavantage_api_key or "").strip()
    if not key:
        raise ConfigurationError(
            "ALPHAVANTAGE_API_KEY is not set. Add it to .env "
            "(see https://www.alphavantage.co/support/#api-key)."
        )
    payload = {k: v for k, v in params.items() if v is not None and v != ""}
    payload["apikey"] = key
    return http_get_json(BASE_URL, **payload)


__all__ = ["compact_json", "query"]
