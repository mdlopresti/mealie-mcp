"""
Shared pytest fixtures for Mealie MCP tests.

Provides common test fixtures for mocking HTTP clients and API responses.
"""

import pytest
import respx
from httpx import Response
from src.client import MealieClient


@pytest.fixture
def mock_client():
    """Create a MealieClient with test configuration."""
    return MealieClient(
        base_url="https://test.mealie.example.com",
        api_token="test-token-12345"
    )


@pytest.fixture
def respx_mock():
    """Create a respx mock context for httpx requests."""
    with respx.mock:
        yield respx


@pytest.fixture
def sample_recipe():
    """Sample recipe data for testing."""
    return {
        "id": "recipe-123",
        "slug": "test-recipe",
        "name": "Test Recipe",
        "description": "A test recipe",
        "recipeYield": "4 servings",
        "totalTime": "30 minutes",
        "prepTime": "10 minutes",
        "cookTime": "20 minutes",
        "recipeIngredient": ["2 cups flour", "1 tsp salt"],
        "recipeInstructions": [
            {"text": "Mix ingredients"},
            {"text": "Bake at 350F"}
        ],
        "tags": [{"id": "tag-1", "name": "Dinner", "slug": "dinner"}],
        "recipeCategory": [{"id": "cat-1", "name": "Main", "slug": "main"}],
        "groupId": "group-123"
    }


@pytest.fixture
def sample_mealplan():
    """Sample meal plan entry for testing."""
    return {
        "id": "mealplan-123",
        "date": "2025-12-25",
        "entryType": "dinner",
        "title": "Christmas Dinner",
        "text": "Special holiday meal",
        "recipeId": "recipe-123"
    }


@pytest.fixture
def sample_shopping_list():
    """Sample shopping list for testing."""
    return {
        "id": "list-123",
        "name": "Weekly Shopping",
        "listItems": [
            {
                "id": "item-1",
                "note": "2 cups flour",
                "checked": False,
                "quantity": 2.0,
                "unit": {"id": "unit-1", "name": "cup"},
                "food": {"id": "food-1", "name": "flour"}
            }
        ]
    }


@pytest.fixture
def sample_tag():
    """Sample tag for testing."""
    return {
        "id": "tag-123",
        "name": "Vegan",
        "slug": "vegan",
        "groupId": "group-123"
    }


@pytest.fixture
def sample_category():
    """Sample category for testing."""
    return {
        "id": "cat-123",
        "name": "Dessert",
        "slug": "dessert",
        "groupId": "group-123"
    }


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
