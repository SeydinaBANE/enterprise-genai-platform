from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import src.agents.orchestrator as orch
from src.agents.orchestrator import run_agent


async def test_run_agent_with_mocked_graph() -> None:
    mock_message = MagicMock()
    mock_message.content = "Final answer"
    mock_message.type = "ai"

    mock_graph = AsyncMock()
    mock_graph.ainvoke.return_value = {"messages": [mock_message]}

    with patch("src.agents.orchestrator.get_graph", return_value=mock_graph):
        result = await run_agent("What is 2+2?")

    assert result.task == "What is 2+2?"
    assert result.output == "Final answer"
    assert result.latency_ms >= 0


async def test_run_agent_empty_messages() -> None:
    mock_graph = AsyncMock()
    mock_graph.ainvoke.return_value = {"messages": []}

    with patch("src.agents.orchestrator.get_graph", return_value=mock_graph):
        result = await run_agent("task")

    assert result.output == "No response generated."


async def test_run_agent_captures_steps() -> None:
    msg1 = MagicMock()
    msg1.content = "thinking..."
    msg1.type = "human"
    msg2 = MagicMock()
    msg2.content = "answer"
    msg2.type = "ai"

    mock_graph = AsyncMock()
    mock_graph.ainvoke.return_value = {"messages": [msg1, msg2]}

    with patch("src.agents.orchestrator.get_graph", return_value=mock_graph):
        result = await run_agent("task")

    assert len(result.steps) == 2
    assert result.output == "answer"


def test_get_graph_caches_result() -> None:
    original = orch._graph
    orch._graph = None
    try:
        with patch("src.agents.orchestrator._build_graph", return_value=MagicMock()) as mock_build:
            g1 = orch.get_graph()
            g2 = orch.get_graph()
        mock_build.assert_called_once()
        assert g1 is g2
    finally:
        orch._graph = original


async def test_run_agent_with_litellm_mock() -> None:
    original_graph = orch._graph
    orch._graph = None
    try:
        mock_resp = MagicMock()
        mock_resp.choices[0].message.content = "Mocked answer"
        mock_resp.choices[0].message.tool_calls = None

        with patch("litellm.acompletion", new_callable=AsyncMock, return_value=mock_resp):
            result = await run_agent("Tell me something.")

        assert result.output == "Mocked answer"
        assert result.task == "Tell me something."
    finally:
        orch._graph = original_graph
