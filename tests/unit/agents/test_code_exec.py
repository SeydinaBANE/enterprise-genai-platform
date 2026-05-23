from src.agents.tools.code_exec_tool import execute_python


def test_simple_arithmetic() -> None:
    result = execute_python.invoke({"code": "result = 2 + 2\nprint(result)"})
    assert "4" in result


def test_blocked_import_os() -> None:
    result = execute_python.invoke({"code": "import os\nos.listdir('/')"})
    assert "blocked" in result.lower()


def test_blocked_subprocess() -> None:
    result = execute_python.invoke({"code": "subprocess.run(['ls'])"})
    assert "blocked" in result.lower()


def test_syntax_error_handled() -> None:
    result = execute_python.invoke({"code": "def broken(:"})
    assert "syntax" in result.lower() or "error" in result.lower()


def test_no_output_returns_placeholder() -> None:
    result = execute_python.invoke({"code": "x = 1"})
    assert result  # should return something (last var or placeholder)
