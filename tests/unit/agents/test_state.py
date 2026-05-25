from __future__ import annotations

from src.agents.state import AgentState


def test_agent_state_has_expected_keys() -> None:
    state: AgentState = {
        "task": "test task",
        "messages": [],
        "retrieved_context": [],
        "intermediate_steps": [],
        "final_answer": "",
        "next": "",
    }
    assert state["task"] == "test task"
    assert state["messages"] == []
    assert state["retrieved_context"] == []


def test_agent_state_accepts_steps() -> None:
    state: AgentState = {
        "task": "analyze",
        "messages": [],
        "retrieved_context": ["ctx1"],
        "intermediate_steps": [{"role": "tool", "content": "result"}],
        "final_answer": "42",
        "next": "",
    }
    assert state["final_answer"] == "42"
    assert len(state["intermediate_steps"]) == 1
