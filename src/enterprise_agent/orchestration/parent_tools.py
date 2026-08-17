"""General tools bound on every authenticated principal."""

from __future__ import annotations

from datetime import datetime, timezone

from langchain_core.tools import tool


@tool
def get_current_utc_time() -> str:
    """Return the current UTC date and time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers and return the sum."""
    return a + b


def get_general_tools():
    return [get_current_utc_time, add_numbers]
