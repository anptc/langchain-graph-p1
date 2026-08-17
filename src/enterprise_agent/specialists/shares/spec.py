"""Shares specialist catalog entry. Nested quote/fundamentals graphs live under this domain."""

from __future__ import annotations

from enterprise_agent.catalog.models import AgentSpec


def _get_agent():
    from enterprise_agent.specialists.shares.graph import get_shares_agent

    return get_shares_agent()


def _no_direct_tools():
    return []


SYSTEM_PROMPT = (
    "You are a shares research supervisor. You do not call market APIs yourself. "
    "Route each task to a nested specialist. If both price and company facts are "
    "needed, call both specialists then combine. "
    "Do not invent market numbers. This is market data, not financial advice. "
    "If a specialist is not available for this user, say you cannot retrieve that data."
)

SPEC = AgentSpec(
    id="shares",
    display_name="Shares research",
    description=(
        "Delegate a stock/share question to the shares supervisor. "
        "Use for quotes, company overview, daily prices, ticker lookup, share news, "
        "or top gainers/losers. Pass a complete task, including the ticker or company name."
    ),
    routing_hint="stocks, shares, tickers, company fundamentals, share prices, market movers, or equity news",
    required_scopes=frozenset({"agent:shares"}),
    system_prompt=SYSTEM_PROMPT,
    get_tools=_no_direct_tools,
    get_agent=_get_agent,
    agent_node="shares_agent",
    tools_node="shares_tools",
)
