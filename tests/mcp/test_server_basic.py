"""
Basic MCP server tests.

Tests for MCP server initialization, tool registration, and invocation.
"""

import pytest
import json
from tests.mcp.helpers import (
    validate_tool_registration,
    validate_tool_params,
    validate_mcp_response,
    extract_tool_result_text
)


class TestMCPServerInitialization:
    """Test MCP server basic initialization."""

    def test_mcp_server_exists(self, mcp_server):
        """Test that MCP server instance exists."""
        assert mcp_server is not None

    def test_mcp_server_name(self, mcp_server):
        """Test that MCP server has correct name."""
        assert mcp_server.name == "mealie"

    @pytest.mark.asyncio
    async def test_mcp_server_has_tools(self, mcp_server):
        """Test that MCP server has tools registered."""
        tools = await mcp_server.get_tools()
        assert len(tools) > 0


class TestMCPToolRegistration:
    """Test that all expected tools are registered."""

    @pytest.mark.asyncio
    async def test_recipe_tools_registered(self, mcp_server):
        """Test that recipe management tools are registered."""
        tools = await mcp_server.get_tools()
        tool_names = list(tools.keys())

        # Core recipe tools
        assert "mealie_recipes_search" in tool_names
        assert "mealie_recipes_get" in tool_names
        assert "mealie_recipes_list" in tool_names
        assert "mealie_recipes_create" in tool_names
        assert "mealie_recipes_update" in tool_names
        assert "mealie_recipes_delete" in tool_names

    @pytest.mark.asyncio
    async def test_mealplan_tools_registered(self, mcp_server):
        """Test that meal plan tools are registered."""
        tools = await mcp_server.get_tools()
        tool_names = list(tools.keys())

        assert "mealie_mealplans_list" in tool_names
        assert "mealie_mealplans_create" in tool_names
        assert "mealie_mealplans_update" in tool_names
        assert "mealie_mealplans_delete" in tool_names

    @pytest.mark.asyncio
    async def test_shopping_tools_registered(self, mcp_server):
        """Test that shopping list tools are registered."""
        tools = await mcp_server.get_tools()
        tool_names = list(tools.keys())

        assert "mealie_shopping_lists_list" in tool_names
        assert "mealie_shopping_items_add" in tool_names
        assert "mealie_shopping_generate_from_mealplan" in tool_names

    @pytest.mark.asyncio
    async def test_utility_tools_registered(self, mcp_server):
        """Test that utility tools are registered."""
        tools = await mcp_server.get_tools()
        tool_names = list(tools.keys())

        assert "ping" in tool_names

    @pytest.mark.asyncio
    async def test_all_tools_count(self, mcp_server):
        """Test that we have all expected tools registered."""
        tools = await mcp_server.get_tools()
        # We should have at least 70+ tools registered
        # (recipes, mealplans, shopping, foods, organizers, etc.)
        assert len(tools) >= 70


class TestMCPToolInvocation:
    """Test invoking MCP tools programmatically."""

    @pytest.mark.asyncio
    async def test_invoke_ping_tool(self, invoke_mcp_tool):
        """Test invoking the ping tool."""
        result = await invoke_mcp_tool("ping")

        # Validate MCP response structure
        validation = validate_mcp_response(result)
        assert validation["valid"], validation.get("error")
        assert validation["content_count"] > 0
        assert validation["has_text"]

        # Extract text content
        text = extract_tool_result_text(result)
        assert len(text) > 0

    @pytest.mark.asyncio
    async def test_invoke_recipe_search_tool(self, invoke_mcp_tool):
        """Test invoking mealie_recipes_search tool."""
        # Configure mock HTTP response
        mock_response = {
            "items": [
                {
                    "name": "Test Recipe",
                    "slug": "test-recipe",
                    "description": "A test recipe",
                    "rating": 5,
                    "tags": [{"name": "Dinner"}],
                    "recipeCategory": [{"name": "Main"}]
                }
            ],
            "total": 1
        }

        result = await invoke_mcp_tool(
            "mealie_recipes_search",
            mock_response=mock_response,
            query="test"
        )

        # Validate response
        validation = validate_mcp_response(result)
        assert validation["valid"]

        # Extract and parse JSON response
        text = extract_tool_result_text(result)
        data = json.loads(text)

        assert "recipes" in data
        assert data["count"] == 1
        assert len(data["recipes"]) == 1
        assert data["recipes"][0]["name"] == "Test Recipe"

    @pytest.mark.asyncio
    async def test_invoke_mealplans_list_tool(self, invoke_mcp_tool):
        """Test invoking mealie_mealplans_list tool."""
        # Configure mock HTTP response
        mock_response = {
            "items": [
                {
                    "id": "meal-1",
                    "date": "2025-12-25",
                    "entryType": "dinner",
                    "title": "Christmas Dinner"
                }
            ],
            "total": 1
        }

        result = await invoke_mcp_tool(
            "mealie_mealplans_list",
            mock_response=mock_response
        )

        # Validate response
        validation = validate_mcp_response(result)
        assert validation["valid"]

        # Parse response
        text = extract_tool_result_text(result)
        data = json.loads(text)
        # The API returns "items" and "total"
        assert "items" in data
        assert data["total"] == 1


class TestMCPToolParameters:
    """Test tool parameter validation."""

    @pytest.mark.asyncio
    async def test_recipes_search_parameters(self, mcp_server):
        """Test that recipes_search has correct parameters."""
        tools = await mcp_server.get_tools()
        tool = tools["mealie_recipes_search"]

        # All parameters should be optional
        assert validate_tool_params(tool, {
            "query": False,
            "tags": False,
            "categories": False,
            "limit": False
        })

    @pytest.mark.asyncio
    async def test_recipes_create_parameters(self, mcp_server):
        """Test that recipes_create has correct parameters."""
        tools = await mcp_server.get_tools()
        tool = tools["mealie_recipes_create"]

        # name is required, others optional
        params = tool.parameters
        assert "name" in params.get("required", [])
        assert "description" not in params.get("required", [])

    @pytest.mark.asyncio
    async def test_mealplans_create_parameters(self, mcp_server):
        """Test that mealplans_create has correct parameters."""
        tools = await mcp_server.get_tools()
        tool = tools["mealie_mealplans_create"]

        # meal_date and entry_type are required
        params = tool.parameters
        required = params.get("required", [])
        assert "meal_date" in required
        assert "entry_type" in required


class TestMCPResources:
    """Test MCP resource registration."""

    @pytest.mark.asyncio
    async def test_resources_registered(self, mcp_server):
        """Test that resources are registered."""
        resources = await mcp_server.get_resources()
        assert len(resources) > 0

        # Get resource URIs (resources are strings)
        resource_uris = list(resources.keys())

        # Check for expected resources
        assert any("recipes" in uri for uri in resource_uris)
        assert any("mealplans" in uri for uri in resource_uris)
        assert any("shopping" in uri for uri in resource_uris)
