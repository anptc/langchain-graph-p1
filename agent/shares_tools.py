"""Alpha Vantage tools used only by the shares sub-agent."""

from __future__ import annotations

from langchain_core.tools import tool

from agent.alphavantage import compact_json, query

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
def search_ticker(keywords: str) -> str:
    """Search Alpha Vantage for ticker symbols matching a company name or keywords."""
    data = query(function="SYMBOL_SEARCH", keywords=keywords)
    matches = data.get("bestMatches", data)[:8] if isinstance(data.get("bestMatches"), list) else data
    return compact_json({"bestMatches": matches} if isinstance(matches, list) else matches)


@tool
def get_share_quote(symbol: str) -> str:
    """Latest daily quote for a ticker (price, change, volume). Free tier is end-of-day."""
    return compact_json(query(function="GLOBAL_QUOTE", symbol=symbol.upper()))


@tool
def get_company_overview(symbol: str) -> str:
    """Company profile and key fundamentals for a ticker (sector, market cap, PE, EPS)."""
    data = query(function="OVERVIEW", symbol=symbol.upper())
    if not isinstance(data, dict) or "Symbol" not in data:
        return compact_json(data)
    return compact_json({k: data.get(k) for k in OVERVIEW_FIELDS})


@tool
def get_daily_prices(symbol: str, last_n_days: int = 7) -> str:
    """Recent daily OHLCV candles for a ticker. last_n_days is 1–15 (default 7)."""
    days = max(1, min(int(last_n_days), 15))
    data = query(function="TIME_SERIES_DAILY", symbol=symbol.upper(), outputsize="compact")
    series = data.get("Time Series (Daily)")
    if not isinstance(series, dict):
        return compact_json(data)
    dates = sorted(series.keys(), reverse=True)[:days]
    return compact_json(
        {
            "meta": data.get("Meta Data"),
            "daily": {d: series[d] for d in dates},
        }
    )


@tool
def get_share_news(symbol: str, limit: int = 5) -> str:
    """Recent news and sentiment for a ticker from Alpha Vantage NEWS_SENTIMENT."""
    cap = max(1, min(int(limit), 10))
    data = query(function="NEWS_SENTIMENT", tickers=symbol.upper(), limit=str(cap), sort="LATEST")
    feed = data.get("feed")
    if not isinstance(feed, list):
        return compact_json(data)
    articles = []
    for item in feed[:cap]:
        articles.append(
            {
                "title": item.get("title"),
                "source": item.get("source"),
                "time_published": item.get("time_published"),
                "summary": (item.get("summary") or "")[:400],
                "overall_sentiment_label": item.get("overall_sentiment_label"),
                "overall_sentiment_score": item.get("overall_sentiment_score"),
                "url": item.get("url"),
            }
        )
    return compact_json(
        {
            "sentiment_score_definition": data.get("sentiment_score_definition"),
            "articles": articles,
        }
    )


@tool
def get_market_movers() -> str:
    """Top gainers, losers, and most actively traded US tickers."""
    data = query(function="TOP_GAINERS_LOSERS")
    if not isinstance(data, dict):
        return compact_json(data)
    return compact_json(
        {
            "last_updated": data.get("last_updated"),
            "top_gainers": (data.get("top_gainers") or [])[:8],
            "top_losers": (data.get("top_losers") or [])[:8],
            "most_actively_traded": (data.get("most_actively_traded") or [])[:8],
        }
    )


def get_shares_tools():
    return [
        search_ticker,
        get_share_quote,
        get_company_overview,
        get_daily_prices,
        get_share_news,
        get_market_movers,
    ]
