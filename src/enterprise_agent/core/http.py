"""Shared urllib JSON client. Specialists must not reimplement timeouts or truncation."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

from enterprise_agent.core.config import get_settings


def compact_json(data, max_chars: int | None = None) -> str:
    settings = get_settings()
    limit = max_chars if max_chars is not None else settings.tool_json_max_chars
    text = json.dumps(data, indent=2, default=str)
    if len(text) > limit:
        return text[:limit] + "\n...[truncated]"
    return text


def http_get_json(url: str, **params) -> dict:
    settings = get_settings()
    payload = {k: v for k, v in params.items() if v is not None and v != ""}
    full = f"{url}?{urllib.parse.urlencode(payload, doseq=True)}"
    request = urllib.request.Request(
        full, headers={"User-Agent": settings.http_user_agent}
    )
    try:
        with urllib.request.urlopen(request, timeout=settings.http_timeout_seconds) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        return {"error": f"HTTP {exc.code}", "body": exc.read().decode()[:500]}
    except urllib.error.URLError as exc:
        return {"error": str(exc.reason)}
