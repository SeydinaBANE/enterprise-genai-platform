from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    task: str
    messages: Annotated[list[BaseMessage], add_messages]
    retrieved_context: list[str]
    intermediate_steps: list[dict[str, str]]
    final_answer: str
    next: str
