from __future__ import annotations

from langchain_core.tools import tool

from src.observability.logging import get_logger

logger = get_logger(__name__)


@tool
async def web_search(query: str) -> str:
    """Search the web for current information. Use for recent events or facts not in documents."""
    logger.info("web_search_called", query=query[:80])
    # Stub — replace with DuckDuckGo or Bing Search API for production
    return (
        f"[Web search stub] Query: '{query}'\n"
        "No live web search configured. "
        "Set BING_SEARCH_API_KEY or use DuckDuckGoSearchRun to enable."
    )
