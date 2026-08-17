"""Shares fundamentals nested catalog entry. Not registered on the parent catalog."""

from __future__ import annotations

from enterprise_agent.catalog.models import AgentSpec
from enterprise_agent.specialists.shares.fundamentals.tools import get_tools


def _get_agent():
    from enterprise_agent.specialists.shares.fundamentals.graph import get_fundamentals_agent

    return get_fundamentals_agent()


SYSTEM_PROMPT = (
    "You are a shares fundamentals specialist. Use Alpha Vantage tools for company "
    "profile and key ratios (sector, market cap, PE, EPS, dividend). "
    "Prefer a ticker (e.g. IBM, AAPL). If the user gives a company name, search first. "
    "Do not look up live quotes, daily candles, or market movers. "
    "Summarize numbers clearly. If the API returns Note/Information (rate limit), say so. "
    "This is market data, not financial advice."
)

SPEC = AgentSpec(
    id="shares_fundamentals",
    display_name="Shares fundamentals",
    description=(
        "Delegate a company-fundamentals question: overview, sector, PE, EPS, market cap. "
        "Pass a complete task including the ticker or company name."
    ),
    routing_hint="company fundamentals, overview, sector, PE, EPS, or market cap",
    required_scopes=frozenset({"agent:shares:fundamentals"}),
    system_prompt=SYSTEM_PROMPT,
    get_tools=get_tools,
    get_agent=_get_agent,
    agent_node="fundamentals_agent",
    tools_node="fundamentals_tools",
)
