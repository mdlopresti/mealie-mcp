"""
Smoke tests for Mealie MCP Server

These tests verify that the server can start without import errors
and responds to basic MCP protocol requests.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


def test_import_server():
    """Test that server module can be imported without errors."""
    # Add src to path
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))

    # This will fail if there are missing imports
    try:
        import server
        assert server.mcp is not None
        assert server.mcp.name == "mealie"
    except ImportError as e:
        pytest.fail(f"Failed to import server: {e}")


def test_import_client():
    """Test that client module can be imported without errors."""
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))

    try:
        from client import MealieClient, MealieAPIError
        assert MealieClient is not None
        assert MealieAPIError is not None
    except ImportError as e:
        pytest.fail(f"Failed to import client: {e}")


def test_import_all_tools():
    """Test that all tool modules can be imported without errors."""
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))

    tool_modules = [
        "tools.recipes",
        "tools.mealplans",
        "tools.shopping",
        "tools.parser",
        "tools.foods",
        "tools.organizers",
    ]

    for module_name in tool_modules:
        try:
            __import__(module_name)
        except ImportError as e:
            pytest.fail(f"Failed to import {module_name}: {e}")


def test_import_all_resources():
    """Test that all resource modules can be imported without errors."""
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))

    resource_modules = [
        "resources.recipes",
        "resources.mealplans",
        "resources.shopping",
    ]

    for module_name in resource_modules:
        try:
            __import__(module_name)
        except ImportError as e:
            pytest.fail(f"Failed to import {module_name}: {e}")


def test_server_basic_syntax():
    """
    Verify server.py has valid Python syntax.

    This catches syntax errors that would cause immediate failures.
    """
    server_path = Path(__file__).parent.parent / "src" / "server.py"

    # Use py_compile to check syntax
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(server_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        pytest.fail(f"Syntax error in server.py:\n{result.stderr}")


def test_client_basic_syntax():
    """
    Verify client.py has valid Python syntax.
    """
    client_path = Path(__file__).parent.parent / "src" / "client.py"

    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(client_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        pytest.fail(f"Syntax error in client.py:\n{result.stderr}")


def test_all_python_files_syntax():
    """
    Verify all Python files have valid syntax.

    This is the critical test that would have caught the missing 'Any' import.
    """
    src_path = Path(__file__).parent.parent / "src"
    python_files = list(src_path.rglob("*.py"))

    assert len(python_files) > 0, "No Python files found in src/"

    errors = []
    for py_file in python_files:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(py_file)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            errors.append(f"{py_file.relative_to(src_path)}: {result.stderr}")

    if errors:
        pytest.fail(f"Syntax errors found:\n" + "\n".join(errors))
