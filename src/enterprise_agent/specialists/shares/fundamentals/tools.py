"""Alpha Vantage fundamentals tools."""

from __future__ import annotations

from langchain_core.tools import tool

from enterprise_agent.specialists.shares.client import compact_json, query
from enterprise_agent.specialists.shares.common import search_ticker

OVERVIEW_FIELDS = (
    "Symbol",
    "Name",
    "Description",
    "Exchange",
    "Currency",
    "Country",
    "Sector",
    "Industry",
    "MarketCapitalization",
    "PERatio",
    "EPS",
    "DividendYield",
    "52WeekHigh",
    "52WeekLow",
    "AnalystTargetPrice",
    "SharesOutstanding",
)


@tool
def get_company_overview(symbol: str) -> str:
    """Company profile and key fundamentals for a ticker (sector, market cap, PE, EPS)."""
    data = query(function="OVERVIEW", symbol=symbol.upper())
    if not isinstance(data, dict) or "Symbol" not in data:
        return compact_json(data)
    return compact_json({k: data.get(k) for k in OVERVIEW_FIELDS})


def get_tools():
    return [search_ticker, get_company_overview]
