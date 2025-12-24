"""
Shared pytest fixtures for MCP server testing.

Provides fixtures for testing MCP tool registration and invocation.
"""

import os
import pytest
from unittest.mock import MagicMock, patch
import respx
from httpx import Response
from src.server import mcp


@pytest.fixture
def mock_mealie_client():
    """Create a mocked MealieClient for server tests.

    This fixture provides a fully mocked MealieClient that can be
    injected into tool functions to avoid real HTTP calls during testing.

    Returns:
        MagicMock: Mocked client instance with context manager support
    """
    # Create mock instance
    mock_instance = MagicMock()
    mock_instance.__enter__ = MagicMock(return_value=mock_instance)
    mock_instance.__exit__ = MagicMock(return_value=None)

    # Mock common HTTP methods
    mock_instance.get = MagicMock(return_value={"items": [], "total": 0})
    mock_instance.post = MagicMock(return_value={"id": "test-123"})
    mock_instance.put = MagicMock(return_value={"id": "test-123"})
    mock_instance.delete = MagicMock(return_value=None)

    # Create mock class that returns the instance
    mock_client_class = MagicMock(return_value=mock_instance)

    return mock_client_class, mock_instance


@pytest.fixture
def mcp_server():
    """Get the FastMCP server instance.

    Returns the configured MCP server from src.server with all tools
    registered. This allows testing tool registration and metadata.

    Returns:
        FastMCP: The configured MCP server instance
    """
    return mcp


@pytest.fixture
def mealie_env():
    """Set up environment variables for Mealie MCP tests.

    This fixture ensures MEALIE_URL and MEALIE_API_TOKEN are set
    so that MealieClient can be instantiated without errors.
    """
    original_url = os.environ.get('MEALIE_URL')
    original_token = os.environ.get('MEALIE_API_TOKEN')

    # Set test environment
    os.environ['MEALIE_URL'] = 'https://test.mealie.example.com'
    os.environ['MEALIE_API_TOKEN'] = 'test-token-12345'

    yield

    # Restore original environment
    if original_url is None:
        os.environ.pop('MEALIE_URL', None)
    else:
        os.environ['MEALIE_URL'] = original_url

    if original_token is None:
        os.environ.pop('MEALIE_API_TOKEN', None)
    else:
        os.environ['MEALIE_API_TOKEN'] = original_token


@pytest.fixture
def invoke_mcp_tool(mealie_env):
    """Helper fixture to invoke MCP tools programmatically.

    This fixture provides a function to invoke any MCP tool
    by name with specified parameters. It mocks HTTP responses
    using respx to avoid real API calls.

    Args:
        tool_name: Name of the tool to invoke (e.g., "mealie_recipes_search")
        mock_response: Optional dict to return as JSON response
        **kwargs: Tool parameters

    Returns:
        ToolResult: The tool's result object

    Example:
        result = await invoke_mcp_tool(
            "mealie_recipes_search",
            mock_response={"items": [...]},
            query="pasta"
        )
    """
    async def _invoke(tool_name: str, mock_response: dict = None, **kwargs):
        """Invoke an MCP tool with mocked HTTP responses.

        Args:
            tool_name: Tool name to invoke
            mock_response: Optional dict to return as JSON from HTTP calls
            **kwargs: Tool parameters

        Returns:
            ToolResult from FastMCP
        """
        # Default mock response
        if mock_response is None:
            mock_response = {"items": [], "total": 0}

        # Mock HTTP responses with respx
        with respx.mock:
            # Mock all HTTP methods to return the mock response
            respx.get(url__startswith="https://test.mealie.example.com").mock(
                return_value=Response(200, json=mock_response)
            )
            respx.post(url__startswith="https://test.mealie.example.com").mock(
                return_value=Response(200, json=mock_response)
            )
            respx.put(url__startswith="https://test.mealie.example.com").mock(
                return_value=Response(200, json=mock_response)
            )
            respx.delete(url__startswith="https://test.mealie.example.com").mock(
                return_value=Response(204)
            )

            # Get the tool
            tools = await mcp.get_tools()
            if tool_name not in tools:
                raise ValueError(f"Tool '{tool_name}' not found. Available: {list(tools.keys())}")

            tool = tools[tool_name]

            # Invoke with parameters
            result = await tool.run(kwargs)
            return result

    return _invoke
