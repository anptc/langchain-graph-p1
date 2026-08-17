"""Ticker search shared by quote and fundamentals nested graphs."""

from __future__ import annotations

from langchain_core.tools import tool

from enterprise_agent.specialists.shares.client import compact_json, query


@tool
def search_ticker(keywords: str) -> str:
    """Search Alpha Vantage for ticker symbols matching a company name or keywords."""
    data = query(function="SYMBOL_SEARCH", keywords=keywords)
    matches = data.get("bestMatches", data)[:8] if isinstance(data.get("bestMatches"), list) else data
    return compact_json({"bestMatches": matches} if isinstance(matches, list) else matches)
