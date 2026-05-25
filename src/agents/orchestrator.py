from __future__ import annotations

import time
from typing import Any

import litellm
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from src.agents.state import AgentState
from src.agents.tools.code_exec_tool import execute_python
from src.agents.tools.rag_tool import rag_query
from src.agents.tools.web_search_tool import web_search
from src.core.config import settings
from src.core.models import AgentResult
from src.observability.logging import get_logger
from src.observability.tracing import traced

logger = get_logger(__name__)

TOOLS = [rag_query, web_search, execute_python]

SUPERVISOR_PROMPT = """You are an expert research and analysis assistant with access to tools.

Available tools:
- rag_query: Search the knowledge base for relevant documents
- web_search: Search the web for current information
- execute_python: Run Python code for calculations or data processing

Instructions:
1. Break the task into steps.
2. Use tools to gather information before answering.
3. Provide a well-structured, cited final answer.
"""


def _build_graph() -> Any:  # noqa: ANN401
    tool_node = ToolNode(TOOLS)

    async def agent_node(state: AgentState) -> AgentState:
        messages = state["messages"]
        if not messages:
            messages = [
                SystemMessage(content=SUPERVISOR_PROMPT),
                HumanMessage(content=state["task"]),
            ]

        response = await litellm.acompletion(
            model=settings.llm_model,
            messages=[
                {"role": m.type if hasattr(m, "type") else "user", "content": m.content}
                for m in messages
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.args_schema.schema() if t.args_schema else {},
                    },
                }
                for t in TOOLS
            ],
            api_base=settings.litellm_api_base,
            api_key=settings.openrouter_api_key,
        )

        from langchain_core.messages import AIMessage

        msg = response.choices[0].message
        ai_message = AIMessage(content=msg.content or "")

        if msg.tool_calls:
            ai_message.tool_calls = [
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "args": tc.function.arguments,
                }
                for tc in msg.tool_calls
            ]

        return {**state, "messages": [*messages, ai_message]}

    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return str(END)

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")

    return graph.compile()


_graph = None


def get_graph() -> Any:  # noqa: ANN401
    global _graph
    if _graph is None:
        _graph = _build_graph()
    return _graph


@traced("agent.run")
async def run_agent(task: str) -> AgentResult:
    start = time.perf_counter()
    graph = get_graph()

    result = await graph.ainvoke(
        {
            "task": task,
            "messages": [],
            "retrieved_context": [],
            "intermediate_steps": [],
            "final_answer": "",
            "next": "",
        },
    )

    messages = result.get("messages", [])
    final = messages[-1].content if messages else "No response generated."
    latency_ms = (time.perf_counter() - start) * 1000

    steps = [
        {"role": m.type if hasattr(m, "type") else "unknown", "content": str(m.content)[:200]}
        for m in messages
    ]

    logger.info(
        "agent_run_done", task_len=len(task), steps=len(steps), latency_ms=round(latency_ms, 2)
    )

    return AgentResult(
        task=task,
        output=final,
        steps=steps,
        model=settings.llm_model,
        latency_ms=latency_ms,
    )
