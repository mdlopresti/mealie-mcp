"""
Pytest fixtures for MCP integration tests.

Provides fixtures for testing MCP protocol interactions with mocked client.
These fixtures enable testing tools end-to-end without real API calls.
"""

import os
import pytest
from unittest.mock import MagicMock, patch
import respx
from httpx import Response
from src.server import mcp
from tests.unit.builders import (
    build_recipe,
    build_mealplan,
    build_shopping_list,
    build_shopping_item,
    build_tag,
    build_category,
    build_tool,
    build_food,
    build_unit,
)


@pytest.fixture
def mealie_env():
    """Set up environment variables for Mealie MCP tests.

    Ensures MEALIE_URL and MEALIE_API_TOKEN are set so that
    MealieClient can be instantiated without errors.
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
def mcp_server():
    """Get the FastMCP server instance.

    Returns the configured MCP server from src.server with all tools
    registered. This allows testing tool registration and metadata.

    Returns:
        FastMCP: The configured MCP server instance
    """
    return mcp


@pytest.fixture
def mcp_tool_invoker(mealie_env):
    """Create an MCP tool invoker with mocked HTTP responses.

    Returns a callable that invokes MCP tools programmatically with
    mocked HTTP responses. Uses respx to intercept httpx calls.

    Usage:
        result = await mcp_tool_invoker(
            "mealie_recipes_search",
            mock_response={"items": [...]},
            query="pasta"
        )

    Args:
        tool_name: Name of the MCP tool to invoke
        mock_response: Dict to return as JSON response (default: empty list)
        status_code: HTTP status code to return (default: 200)
        **kwargs: Tool parameters

    Returns:
        Callable that invokes tools and returns ToolResult
    """
    async def _invoke(
        tool_name: str,
        mock_response: dict = None,
        status_code: int = 200,
        **kwargs
    ):
        """Invoke an MCP tool with mocked HTTP responses."""
        # Default mock response
        if mock_response is None:
            mock_response = {"items": [], "total": 0}

        # Mock HTTP responses with respx
        with respx.mock:
            # Mock all HTTP methods to return the mock response
            respx.get(url__startswith="https://test.mealie.example.com").mock(
                return_value=Response(status_code, json=mock_response)
            )
            respx.post(url__startswith="https://test.mealie.example.com").mock(
                return_value=Response(status_code, json=mock_response)
            )
            respx.put(url__startswith="https://test.mealie.example.com").mock(
                return_value=Response(status_code, json=mock_response)
            )
            respx.delete(url__startswith="https://test.mealie.example.com").mock(
                return_value=Response(204 if status_code == 200 else status_code)
            )

            # Get the tool
            tools = await mcp.get_tools()
            if tool_name not in tools:
                raise ValueError(
                    f"Tool '{tool_name}' not found. "
                    f"Available: {list(tools.keys())[:10]}..."
                )

            tool = tools[tool_name]

            # Invoke with parameters
            result = await tool.run(kwargs)
            return result

    return _invoke


@pytest.fixture
def mock_mealie_api():
    """Create a respx mock context for Mealie API.

    Provides a context manager that mocks HTTP requests to the Mealie API.
    Use this for more complex scenarios where you need to control different
    endpoints differently.

    Usage:
        with mock_mealie_api() as api:
            api.get("/api/recipes").mock(return_value=Response(200, json={...}))
            result = await invoke_tool(...)

    Returns:
        respx.MockRouter: Mock router for HTTP requests
    """
    with respx.mock as router:
        yield router


# Sample data fixtures using builders

@pytest.fixture
def sample_recipes():
    """Generate sample recipe data for testing.

    Returns:
        list: Three sample recipes with different attributes
    """
    return [
        build_recipe(
            id="recipe-1",
            slug="pasta-carbonara",
            name="Pasta Carbonara",
            description="Classic Italian pasta dish"
        ),
        build_recipe(
            id="recipe-2",
            slug="vegan-stir-fry",
            name="Vegan Stir Fry",
            description="Quick vegetable stir fry",
            tags=[build_tag(name="Vegan")]
        ),
        build_recipe(
            id="recipe-3",
            slug="chocolate-cake",
            name="Chocolate Cake",
            description="Rich chocolate layer cake",
            recipeCategory=[build_category(name="Dessert")]
        )
    ]


@pytest.fixture
def sample_mealplans():
    """Generate sample meal plan data for testing.

    Returns:
        list: Meal plan entries for a week
    """
    return [
        build_mealplan(
            id="mp-1",
            meal_date="2025-12-25",
            entry_type="breakfast",
            title="Christmas Breakfast"
        ),
        build_mealplan(
            id="mp-2",
            meal_date="2025-12-25",
            entry_type="dinner",
            recipeId="recipe-1"
        ),
        build_mealplan(
            id="mp-3",
            meal_date="2025-12-26",
            entry_type="lunch",
            recipeId="recipe-2"
        )
    ]


@pytest.fixture
def sample_shopping_lists():
    """Generate sample shopping list data for testing.

    Returns:
        list: Shopping lists with items
    """
    return [
        build_shopping_list(
            id="list-1",
            name="Weekly Groceries",
            listItems=[
                build_shopping_item(
                    id="item-1",
                    note="2 cups flour",
                    checked=False
                ),
                build_shopping_item(
                    id="item-2",
                    note="1 lb butter",
                    checked=True
                )
            ]
        )
    ]


@pytest.fixture
def sample_organizers():
    """Generate sample organizer data (tags, categories, tools).

    Returns:
        dict: Dictionary with tags, categories, and tools
    """
    return {
        "tags": [
            build_tag(id="tag-1", name="Vegan", slug="vegan"),
            build_tag(id="tag-2", name="Quick", slug="quick")
        ],
        "categories": [
            build_category(id="cat-1", name="Dessert", slug="dessert"),
            build_category(id="cat-2", name="Main Course", slug="main-course")
        ],
        "tools": [
            build_tool(id="tool-1", name="Blender", slug="blender"),
            build_tool(id="tool-2", name="Oven", slug="oven")
        ]
    }


@pytest.fixture
def sample_foods_and_units():
    """Generate sample food and unit data for testing.

    Returns:
        dict: Dictionary with foods and units
    """
    return {
        "foods": [
            build_food(id="food-1", name="Flour"),
            build_food(id="food-2", name="Sugar"),
            build_food(id="food-3", name="Butter")
        ],
        "units": [
            build_unit(id="unit-1", name="cup", abbreviation="c"),
            build_unit(id="unit-2", name="teaspoon", abbreviation="tsp"),
            build_unit(id="unit-3", name="pound", abbreviation="lb")
        ]
    }
