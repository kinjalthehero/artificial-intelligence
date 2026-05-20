import os
from typing import Any, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

SerpApiClient: Any = None
try:
    from serpapi import Client as SerpApiClient
except ImportError:
    SerpApiClient = None

LegacyGoogleSearch: Any = None
try:
    from serpapi import GoogleSearch as LegacyGoogleSearch
except ImportError:
    LegacyGoogleSearch = None


class StockSearchInput(BaseModel):
    query: str = Field(
        ..., description="The stock ticker or company name to search for."
    )


class StockSearchTool(BaseTool):
    name: str = "StockNewsSearch"
    description: str = (
        "Search for the latest news and information about a stock using SerpAPI."
    )
    args_schema: Type[BaseModel] = StockSearchInput

    def _run(self, query: str) -> str:
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": os.getenv("SERPAPI_KEY"),
                "tbm": "nws",
                "num": 3,
            }
            if SerpApiClient:
                client = SerpApiClient(api_key=params["api_key"])
                results = client.search(
                    {"engine": "google_news", "q": query, "num": 3}
                )
            elif LegacyGoogleSearch:
                search = LegacyGoogleSearch(params)
                results = search.get_dict()
            else:
                return "SerpAPI client is not installed."
            news = results.get(
                "news_results", results.get("organic_results", [])
            )
            if not news:
                return "No news found for the given query."
            output = []
            for item in news[:3]:
                title = item.get("title", "")
                snippet = item.get("snippet", item.get("description", ""))
                output.append(f"Title: {title}: {snippet[:100]}")
            return "\n\n".join(output)
        except Exception as e:
            return f"Error fetching news: {str(e)}"
