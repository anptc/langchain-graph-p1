"""Shares quote nested catalog entry. Not registered on the parent catalog."""

from __future__ import annotations

from enterprise_agent.catalog.models import AgentSpec
from enterprise_agent.specialists.shares.quote.tools import get_tools


def _get_agent():
    from enterprise_agent.specialists.shares.quote.graph import get_quote_agent

    return get_quote_agent()


SYSTEM_PROMPT = (
    "You are a shares quote specialist. Use Alpha Vantage tools for quotes, "
    "daily prices, ticker search, news, and market movers. "
    "Prefer a ticker (e.g. IBM, AAPL). If the user gives a company name, search first. "
    "Do not look up company fundamentals (PE, sector, market cap overview). "
    "Summarize numbers clearly. If the API returns Note/Information (rate limit), say so. "
    "This is market data, not financial advice."
)

SPEC = AgentSpec(
    id="shares_quote",
    display_name="Shares quote",
    description=(
        "Delegate a price/tape question: latest quote, daily candles, movers, or share news. "
        "Pass a complete task including the ticker or company name."
    ),
    routing_hint="share prices, latest quotes, daily candles, market movers, or share news",
    required_scopes=frozenset({"agent:shares:quote"}),
    system_prompt=SYSTEM_PROMPT,
    get_tools=get_tools,
    get_agent=_get_agent,
    agent_node="quote_agent",
    tools_node="quote_tools",
)
