from __future__ import annotations

import ast
import contextlib
import io

from langchain_core.tools import tool

from src.observability.logging import get_logger

logger = get_logger(__name__)

_FORBIDDEN = {"import os", "import sys", "subprocess", "open(", "__import__", "exec(", "eval("}
MAX_OUTPUT_CHARS = 2000


@tool
def execute_python(code: str) -> str:
    """Execute a small Python snippet and return stdout. Safe sandbox — no I/O or imports."""
    for forbidden in _FORBIDDEN:
        if forbidden in code:
            logger.warning("code_exec_blocked", reason=forbidden)
            return f"Execution blocked: '{forbidden}' is not allowed."

    try:
        ast.parse(code)
    except SyntaxError as e:
        return f"Syntax error: {e}"

    stdout = io.StringIO()
    local_vars: dict[str, object] = {}
    try:
        safe_builtins = {
            "print": print,
            "len": len,
            "range": range,
            "int": int,
            "float": float,
            "str": str,
            "list": list,
            "dict": dict,
            "sum": sum,
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "enumerate": enumerate,
            "zip": zip,
        }
        with contextlib.redirect_stdout(stdout):
            exec(code, {"__builtins__": safe_builtins}, local_vars)  # noqa: S102
        output = stdout.getvalue()
        if not output and local_vars:
            last_val = list(local_vars.values())[-1]
            output = str(last_val)
        logger.info("code_exec_success", output_len=len(output))
        return output[:MAX_OUTPUT_CHARS] or "(no output)"
    except Exception as exc:
        logger.warning("code_exec_error", error=str(exc))
        return f"Runtime error: {exc}"
