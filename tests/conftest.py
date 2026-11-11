"""
Shared pytest fixtures for Mealie MCP tests.

Provides common test fixtures for mocking HTTP clients and API responses.

For unit test-specific fixtures (isolated mocks, builders), see tests/unit/conftest.py.
For mock data builders, see tests/unit/builders.py.
"""

import pytest
import respx

# FORK: fastmcp 4 removed FastMCP.get_tools()/get_resources(); the suite still uses them.
from fastmcp import FastMCP as _FastMCP

if not hasattr(_FastMCP, "get_tools"):
    async def _get_tools(self):
        return {t.name: t for t in await self.list_tools()}
    _FastMCP.get_tools = _get_tools  # type: ignore[attr-defined]

if not hasattr(_FastMCP, "get_resources") and hasattr(_FastMCP, "list_resources"):
    async def _get_resources(self):
        return {str(r.uri): r for r in await self.list_resources()}
    _FastMCP.get_resources = _get_resources  # type: ignore[attr-defined]

if not hasattr(_FastMCP, "get_resource_templates") and hasattr(_FastMCP, "list_resource_templates"):
    async def _get_resource_templates(self):
        return {t.uri_template: t for t in await self.list_resource_templates()}
    _FastMCP.get_resource_templates = _get_resource_templates  # type: ignore[attr-defined]
from httpx import Response
from src.client import MealieClient
from tests.unit.builders import (
    build_recipe,
    build_mealplan,
    build_shopping_list,
    build_shopping_item,
    build_tag,
    build_category
)


@pytest.fixture
def mock_client():
    """Create a MealieClient with test configuration.

    This is the real MealieClient class for integration tests.
    For isolated unit tests, use mock_client_isolated from tests/unit/conftest.py.
    """
    return MealieClient(
        base_url="https://test.mealie.example.com",
        api_token="test-token-12345"
    )


@pytest.fixture
def respx_mock():
    """Create a respx mock context for httpx requests.

    Use this for integration tests that need to mock HTTP responses.
    For pure unit tests without HTTP, use mock_client_isolated instead.
    """
    with respx.mock:
        yield respx


@pytest.fixture
def sample_recipe():
    """Sample recipe data for testing.

    Uses builder from tests/unit/builders.py for consistency.
    """
    return build_recipe(
        id="recipe-123",
        slug="test-recipe",
        name="Test Recipe"
    )


@pytest.fixture
def sample_mealplan():
    """Sample meal plan entry for testing.

    Uses builder from tests/unit/builders.py for consistency.
    """
    return build_mealplan(
        id="mealplan-123",
        meal_date="2025-12-25",
        entry_type="dinner",
        title="Christmas Dinner",
        text="Special holiday meal",
        recipeId="recipe-123"
    )


@pytest.fixture
def sample_shopping_list():
    """Sample shopping list for testing.

    Uses builder from tests/unit/builders.py for consistency.
    """
    return build_shopping_list(
        id="list-123",
        name="Weekly Shopping",
        listItems=[
            build_shopping_item(
                id="item-1",
                note="2 cups flour",
                checked=False,
                quantity=2.0,
                unit={"id": "unit-1", "name": "cup"},
                food={"id": "food-1", "name": "flour"}
            )
        ]
    )


@pytest.fixture
def sample_tag():
    """Sample tag for testing.

    Uses builder from tests/unit/builders.py for consistency.
    """
    return build_tag(
        id="tag-123",
        name="Vegan",
        slug="vegan"
    )


@pytest.fixture
def sample_category():
    """Sample category for testing.

    Uses builder from tests/unit/builders.py for consistency.
    """
    return build_category(
        id="cat-123",
        name="Dessert",
        slug="dessert"
    )


def create_json_response(data, status_code=200):
    """Helper to create httpx Response with JSON data."""
    import json
    return Response(
        status_code=status_code,
        json=data,
        headers={"content-type": "application/json"}
    )


def create_error_response(status_code, detail):
    """Helper to create error response."""
    import json
    return Response(
        status_code=status_code,
        json={"detail": detail},
        headers={"content-type": "application/json"}
    )
