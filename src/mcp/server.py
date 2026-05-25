from __future__ import annotations

import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from src.observability.logging import get_logger

logger = get_logger(__name__)

app = Server("genai-platform")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="rag_query",
            description="Query the knowledge base using RAG. Returns relevant document chunks.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "Question to answer"},
                    "top_k": {"type": "integer", "description": "Number of results", "default": 5},
                },
                "required": ["question"],
            },
        ),
        Tool(
            name="run_agent",
            description="Run a multi-step research agent on a complex task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Task description for the agent"},
                },
                "required": ["task"],
            },
        ),
        Tool(
            name="list_documents",
            description="List all indexed documents in the knowledge base.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:  # type: ignore[type-arg]
    logger.info("mcp_tool_called", tool=name)

    if name == "rag_query":
        from src.agents.tools.rag_tool import rag_query

        result = await rag_query.ainvoke({"question": arguments["question"]})
        return [TextContent(type="text", text=result)]

    if name == "run_agent":
        from src.agents.orchestrator import run_agent

        result = await run_agent(arguments["task"])
        return [TextContent(type="text", text=result.output)]

    if name == "list_documents":
        return [TextContent(type="text", text="Document listing not yet implemented.")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main() -> None:
    logger.info("mcp_server_starting")
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
