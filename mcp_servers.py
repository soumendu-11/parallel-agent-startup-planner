"""
MCP Server integration for FMP (Financial Modeling Prep) and Brave Search.

Uses langchain-mcp-adapters to connect to MCP servers as tool providers
for LangGraph agent nodes. Falls back to direct HTTP if MCP servers
are unavailable.
"""

import os
import json
import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
BRAVE_BASE_URL = "https://api.search.brave.com/res/v1"


# ── FMP MCP Tools ────────────────────────────────────────────────────

@tool
def fmp_company_profile(symbol: str) -> str:
    """Get company profile including market cap, sector, industry, and description.
    Use this to research specific companies in the startup's competitive landscape."""
    api_key = os.getenv("FMP_API_KEY")
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{FMP_BASE_URL}/profile/{symbol}", params={"apikey": api_key})
        if resp.status_code == 200:
            data = resp.json()
            if data:
                p = data[0]
                return json.dumps({
                    "symbol": p.get("symbol"),
                    "name": p.get("companyName"),
                    "market_cap": p.get("mktCap"),
                    "sector": p.get("sector"),
                    "industry": p.get("industry"),
                    "description": p.get("description", "")[:500],
                    "price": p.get("price"),
                    "revenue": p.get("revenue"),
                    "full_time_employees": p.get("fullTimeEmployees"),
                }, indent=2)
    return json.dumps({"error": f"No data found for {symbol}"})


@tool
def fmp_income_statement(symbol: str, period: str = "annual") -> str:
    """Get income statement data for a company. Use period='annual' or 'quarter'.
    Useful for understanding competitor financials and building projections."""
    api_key = os.getenv("FMP_API_KEY")
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{FMP_BASE_URL}/income-statement/{symbol}",
            params={"apikey": api_key, "period": period, "limit": 5},
        )
        if resp.status_code == 200:
            data = resp.json()
            results = []
            for stmt in data[:5]:
                results.append({
                    "date": stmt.get("date"),
                    "revenue": stmt.get("revenue"),
                    "gross_profit": stmt.get("grossProfit"),
                    "operating_income": stmt.get("operatingIncome"),
                    "net_income": stmt.get("netIncome"),
                    "eps": stmt.get("eps"),
                })
            return json.dumps(results, indent=2)
    return json.dumps({"error": f"No income data for {symbol}"})


@tool
def fmp_financial_ratios(symbol: str) -> str:
    """Get key financial ratios for a company — margins, ROE, debt ratios.
    Use this to benchmark competitors and set financial targets."""
    api_key = os.getenv("FMP_API_KEY")
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{FMP_BASE_URL}/ratios/{symbol}",
            params={"apikey": api_key, "limit": 3},
        )
        if resp.status_code == 200:
            data = resp.json()
            results = []
            for r in data[:3]:
                results.append({
                    "date": r.get("date"),
                    "gross_margin": r.get("grossProfitMargin"),
                    "operating_margin": r.get("operatingProfitMargin"),
                    "net_margin": r.get("netProfitMargin"),
                    "roe": r.get("returnOnEquity"),
                    "debt_to_equity": r.get("debtEquityRatio"),
                    "current_ratio": r.get("currentRatio"),
                    "price_to_earnings": r.get("priceEarningsRatio"),
                })
            return json.dumps(results, indent=2)
    return json.dumps({"error": f"No ratio data for {symbol}"})


@tool
def fmp_stock_screener(sector: str, market_cap_min: int = 0, limit: int = 10) -> str:
    """Screen stocks by sector to find competitors. Returns company list with key metrics.
    Sectors: Technology, Healthcare, Financial Services, Consumer Cyclical, etc."""
    api_key = os.getenv("FMP_API_KEY")
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{FMP_BASE_URL}/stock-screener",
            params={
                "apikey": api_key,
                "sector": sector,
                "marketCapMoreThan": market_cap_min,
                "limit": limit,
            },
        )
        if resp.status_code == 200:
            data = resp.json()
            results = []
            for c in data[:limit]:
                results.append({
                    "symbol": c.get("symbol"),
                    "name": c.get("companyName"),
                    "market_cap": c.get("marketCap"),
                    "sector": c.get("sector"),
                    "industry": c.get("industry"),
                    "price": c.get("price"),
                })
            return json.dumps(results, indent=2)
    return json.dumps({"error": f"No screener results for sector={sector}"})


@tool
def fmp_market_index(index: str = "^GSPC") -> str:
    """Get market index data (S&P 500, NASDAQ, etc.) for market context.
    Use ^GSPC for S&P 500, ^IXIC for NASDAQ, ^DJI for Dow Jones."""
    api_key = os.getenv("FMP_API_KEY")
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{FMP_BASE_URL}/quote/{index}",
            params={"apikey": api_key},
        )
        if resp.status_code == 200:
            data = resp.json()
            if data:
                q = data[0]
                return json.dumps({
                    "name": q.get("name"),
                    "price": q.get("price"),
                    "change_pct": q.get("changesPercentage"),
                    "year_high": q.get("yearHigh"),
                    "year_low": q.get("yearLow"),
                }, indent=2)
    return json.dumps({"error": f"No index data for {index}"})


# ── Brave Search MCP Tools ──────────────────────────────────────────

@tool
def brave_web_search(query: str, count: int = 5) -> str:
    """Search the web using Brave Search API. Returns titles, URLs, and descriptions.
    Use for market research, news, competitor intelligence, and funding landscape."""
    api_key = os.getenv("BRAVE_API_KEY")
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{BRAVE_BASE_URL}/web/search",
            headers={"X-Subscription-Token": api_key, "Accept": "application/json"},
            params={"q": query, "count": count},
        )
        if resp.status_code == 200:
            data = resp.json()
            results = []
            for r in data.get("web", {}).get("results", [])[:count]:
                results.append({
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "description": r.get("description", "")[:300],
                })
            return json.dumps(results, indent=2)
    return json.dumps({"error": f"Search failed for: {query}"})


@tool
def brave_news_search(query: str, count: int = 5) -> str:
    """Search recent news using Brave Search. Returns latest news articles.
    Use for current market trends, funding announcements, industry news."""
    api_key = os.getenv("BRAVE_API_KEY")
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{BRAVE_BASE_URL}/news/search",
            headers={"X-Subscription-Token": api_key, "Accept": "application/json"},
            params={"q": query, "count": count},
        )
        if resp.status_code == 200:
            data = resp.json()
            results = []
            for r in data.get("results", [])[:count]:
                results.append({
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "description": r.get("description", "")[:300],
                    "age": r.get("age"),
                })
            return json.dumps(results, indent=2)
    return json.dumps({"error": f"News search failed for: {query}"})


# ── Tool Bundles per Node ────────────────────────────────────────────

def get_market_research_tools() -> list:
    """Tools for the Market Research node: web + news search."""
    return [brave_web_search, brave_news_search]


def get_competitor_analysis_tools() -> list:
    """Tools for the Competitor Analysis node: FMP financials + web search."""
    return [fmp_company_profile, fmp_income_statement, fmp_financial_ratios,
            fmp_stock_screener, brave_web_search]


def get_financial_projection_tools() -> list:
    """Tools for the Financial Projection node: FMP data + market index."""
    return [fmp_company_profile, fmp_income_statement, fmp_financial_ratios,
            fmp_market_index, brave_web_search]


def get_funding_landscape_tools() -> list:
    """Tools for the Funding Landscape node: web + news search."""
    return [brave_web_search, brave_news_search]
