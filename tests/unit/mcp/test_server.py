from __future__ import annotations

from unittest.mock import AsyncMock, patch

from src.core.models import AgentResult


async def test_list_tools_returns_three_tools() -> None:
    from src.mcp.server import list_tools

    tools = await list_tools()
    names = {t.name for t in tools}
    assert "rag_query" in names
    assert "run_agent" in names
    assert "list_documents" in names


async def test_call_tool_list_documents() -> None:
    from src.mcp.server import call_tool

    results = await call_tool("list_documents", {})
    assert len(results) == 1
    assert "not yet implemented" in results[0].text.lower()


async def test_call_tool_unknown_returns_error() -> None:
    from src.mcp.server import call_tool

    results = await call_tool("nonexistent_tool", {})
    assert "Unknown tool" in results[0].text


async def test_call_tool_rag_query() -> None:
    with patch(
        "src.agents.tools.rag_tool.rag_query",
        new_callable=AsyncMock,
    ) as mock_rag:
        mock_rag.ainvoke = AsyncMock(return_value="[1] answer text")
        from src.mcp.server import call_tool

        results = await call_tool("rag_query", {"question": "What is X?"})

    assert len(results) == 1


async def test_call_tool_run_agent() -> None:
    agent_result = AgentResult(
        task="test", output="Agent output", steps=[], model="gpt-4o-mini", latency_ms=100.0
    )
    with patch(
        "src.agents.orchestrator.run_agent",
        new_callable=AsyncMock,
        return_value=agent_result,
    ):
        from src.mcp.server import call_tool

        results = await call_tool("run_agent", {"task": "analyze this"})

    assert len(results) == 1
    assert results[0].text == "Agent output"
