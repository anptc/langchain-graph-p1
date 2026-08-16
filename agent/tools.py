"""Tools bound on the parent agent.

General helpers and sub-agent handoffs live here, because the parent is the
caller — not the specialist graphs.
"""

from __future__ import annotations

from datetime import datetime, timezone

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool


def _text(content) -> str:
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("text"):
                parts.append(str(item["text"]))
        return "\n".join(parts) or str(content)
    return str(content or "")


def _run_subagent(get_agent, task: str) -> str:
    result = get_agent().invoke({"messages": [HumanMessage(content=task)]})
    last = result["messages"][-1]
    return _text(getattr(last, "content", last))


@tool
def get_current_utc_time() -> str:
    """Return the current UTC date and time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers and return the sum."""
    return a + b


@tool
def transfer_to_shares_agent(task: str) -> str:
    """Delegate a stock/share question to the Alpha Vantage specialist.

    Use for quotes, company overview, daily prices, ticker lookup, share news,
    or top gainers/losers. Pass a complete task, including the ticker or company name.
    """
    from agent.shares import get_shares_agent

    return _run_subagent(get_shares_agent, task)


@tool
def transfer_to_weather_agent(task: str) -> str:
    """Delegate a weather, forecast, or air-quality question to the Open-Meteo specialist.

    Pass a complete task including the city or coordinates. Use for current
    conditions, multi-day forecast, or air quality. Not for stocks.
    """
    from agent.weather import get_weather_agent

    return _run_subagent(get_weather_agent, task)


def get_tools():
    return [
        get_current_utc_time,
        add_numbers,
        transfer_to_shares_agent,
        transfer_to_weather_agent,
    ]
