from __future__ import annotations

from src.agents.tools.web_search_tool import web_search


async def test_returns_stub_message() -> None:
    result = await web_search.ainvoke({"query": "latest Python release"})
    assert "Web search stub" in result
    assert "latest Python release" in result


async def test_long_query_handled() -> None:
    result = await web_search.ainvoke({"query": "x" * 200})
    assert "Web search stub" in result


async def test_result_mentions_configuration() -> None:
    result = await web_search.ainvoke({"query": "anything"})
    assert "BING_SEARCH_API_KEY" in result or "DuckDuckGo" in result
