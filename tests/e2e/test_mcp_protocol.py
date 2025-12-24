"""
E2E tests for MCP protocol functionality.

These tests validate the Model Context Protocol implementation including:
- Server initialization handshake
- Tool registration and invocation
- Resource registration and reading
- JSON-RPC protocol compliance
"""

import pytest
from typing import Dict, Any


@pytest.mark.e2e
def test_mcp_initialization(mcp_client: Dict[str, Any]):
    """Test that MCP server initializes with proper handshake."""
    # The mcp_client fixture performs initialization automatically
    # Verify that server_info was populated
    assert "server_info" in mcp_client
    server_info = mcp_client["server_info"]

    # Verify server capabilities
    assert "capabilities" in server_info
    capabilities = server_info["capabilities"]

    # FastMCP servers should expose tools capability
    assert "tools" in capabilities or len(capabilities) > 0

    # Verify server info
    assert "serverInfo" in server_info
    assert server_info["serverInfo"]["name"] == "mealie"


@pytest.mark.e2e
def test_mcp_tools_list(mcp_tools_list: list[Dict[str, Any]]):
    """Test that MCP server exposes expected tools."""
    # Verify we got a list of tools
    assert isinstance(mcp_tools_list, list)
    assert len(mcp_tools_list) > 0, "Server should expose at least one tool"

    # Verify tool structure
    first_tool = mcp_tools_list[0]
    assert "name" in first_tool, "Tool should have a name"
    assert "description" in first_tool, "Tool should have a description"
    assert "inputSchema" in first_tool, "Tool should have an inputSchema"

    # Verify expected tools are present
    tool_names = [tool["name"] for tool in mcp_tools_list]

    # Core tools that should always be present
    expected_tools = [
        "ping",
        "mealie_recipes_search",
        "mealie_recipes_get",
        "mealie_mealplans_list",
        "mealie_shopping_lists_list",
    ]

    for tool_name in expected_tools:
        assert tool_name in tool_names, f"Expected tool '{tool_name}' not found"


@pytest.mark.e2e
def test_mcp_tool_invocation(
    mcp_tool_caller: callable,
    docker_mealie_client,
    docker_unique_id: str,
    docker_test_cleanup: dict
):
    """Test that MCP tools can be invoked via protocol."""
    # Create a test recipe via HTTP client for setup
    recipe = docker_mealie_client.create_recipe(
        name=f"MCP Test Recipe {docker_unique_id}",
        description="Created for MCP protocol testing"
    )
    docker_test_cleanup["recipes"].append(recipe["slug"])

    # Now fetch it via MCP tool invocation
    result = mcp_tool_caller("mealie_recipes_get", slug=recipe["slug"])

    # Result should be JSON string
    assert isinstance(result, (str, dict)), "Tool should return result"

    # Parse if string
    if isinstance(result, str):
        import json
        result = json.loads(result)

    # Verify recipe data
    assert result["name"] == f"MCP Test Recipe {docker_unique_id}"
    assert result["slug"] == recipe["slug"]


@pytest.mark.e2e
def test_mcp_resources_list(mcp_resources_list: list[Dict[str, Any]]):
    """Test that MCP server exposes expected resources."""
    # Verify we got a list of resources
    assert isinstance(mcp_resources_list, list)
    assert len(mcp_resources_list) > 0, "Server should expose at least one resource"

    # Verify resource structure
    first_resource = mcp_resources_list[0]
    assert "uri" in first_resource, "Resource should have a URI"
    assert "name" in first_resource, "Resource should have a name"

    # Verify expected resources are present
    resource_uris = [resource["uri"] for resource in mcp_resources_list]

    # Core resources that should always be present
    expected_resources = [
        "recipes://list",
        "mealplans://current",
        "mealplans://today",
        "shopping://lists",
    ]

    for resource_uri in expected_resources:
        assert resource_uri in resource_uris, f"Expected resource '{resource_uri}' not found"


@pytest.mark.e2e
def test_mcp_resource_reading(mcp_resource_reader: callable):
    """Test that MCP resources can be read via protocol."""
    # Read the recipes list resource
    result = mcp_resource_reader("recipes://list")

    # Result should be structured content
    assert isinstance(result, (str, dict, list)), "Resource should return content"

    # Parse if string
    if isinstance(result, str):
        # Should be markdown or JSON
        assert len(result) > 0, "Resource content should not be empty"


@pytest.mark.e2e
def test_mcp_tool_error_handling(mcp_tool_caller: callable):
    """Test that MCP tool errors are handled properly."""
    # Try to get a non-existent recipe
    with pytest.raises(RuntimeError) as exc_info:
        mcp_tool_caller("mealie_recipes_get", slug="non-existent-recipe-xyz")

    # Error should contain meaningful message
    assert "error" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower()


@pytest.mark.e2e
def test_mcp_ping_tool(mcp_tool_caller: callable):
    """Test the ping utility tool."""
    result = mcp_tool_caller("ping")

    # Result should be a success message
    assert isinstance(result, str)
    assert "pong" in result.lower()
    assert "running" in result.lower()
