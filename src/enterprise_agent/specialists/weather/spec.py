"""Weather specialist catalog entry."""

from __future__ import annotations

from enterprise_agent.catalog.models import AgentSpec
from enterprise_agent.specialists.weather.tools import get_tools


def _get_agent():
    from enterprise_agent.specialists.weather.graph import get_weather_agent

    return get_weather_agent()

SYSTEM_PROMPT = (
    "You are a weather specialist. Use Open-Meteo tools only. "
    "If the user gives a city or place name, geocode it first, then call weather "
    "or air-quality with that latitude and longitude. "
    "Summarize in the place's local timezone. Temperatures are Celsius unless asked otherwise. "
    "This is a forecast, not a warning service."
)

SPEC = AgentSpec(
    id="weather",
    display_name="Weather",
    description=(
        "Delegate a weather, forecast, or air-quality question to the Open-Meteo specialist. "
        "Pass a complete task including the city or coordinates. Use for current "
        "conditions, multi-day forecast, or air quality. Not for stocks."
    ),
    routing_hint="weather, forecasts, temperature, rain, wind, or air quality",
    required_scopes=frozenset({"agent:weather"}),
    system_prompt=SYSTEM_PROMPT,
    get_tools=get_tools,
    get_agent=_get_agent,
    agent_node="weather_agent",
    tools_node="weather_tools",
)
