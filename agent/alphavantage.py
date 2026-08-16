"""Alpha Vantage HTTP helper. Key comes from ALPHAVANTAGE_API_KEY, never from code."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://www.alphavantage.co/query"


def _api_key() -> str:
    key = (os.getenv("ALPHAVANTAGE_API_KEY") or "").strip()
    if not key:
        raise RuntimeError(
            "ALPHAVANTAGE_API_KEY is not set. Add it to .env "
            "(see https://www.alphavantage.co/support/#api-key)."
        )
    return key


def query(**params) -> dict:
    payload = {k: v for k, v in params.items() if v is not None and v != ""}
    payload["apikey"] = _api_key()
    url = f"{BASE_URL}?{urllib.parse.urlencode(payload)}"
    request = urllib.request.Request(url, headers={"User-Agent": "langchain-graph-p1"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        return {"error": f"HTTP {exc.code}", "body": exc.read().decode()[:500]}
    except urllib.error.URLError as exc:
        return {"error": str(exc.reason)}
    return data


def compact_json(data: dict, max_chars: int = 4000) -> str:
    text = json.dumps(data, indent=2, default=str)
    if len(text) > max_chars:
        return text[:max_chars] + "\n...[truncated]"
    return text
