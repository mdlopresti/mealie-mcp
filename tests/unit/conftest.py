"""
Pytest fixtures for unit tests.

Provides fixtures for mocking external dependencies, creating test clients,
and setting up isolated unit test environments.

Unit tests focus on testing individual components (client methods, tool functions)
in isolation without external dependencies (no real HTTP calls, no Docker, no MCP server).
"""

import pytest
import httpx
from typing import Generator, Dict, Any
from unittest.mock import Mock, MagicMock, patch
from src.client import MealieClient


@pytest.fixture
def mock_httpx_client() -> Generator[Mock, None, None]:
    """
    Create a mock httpx.Client for testing without real HTTP calls.

    Returns:
        Mock httpx.Client instance

    Example:
        def test_get_recipe(mock_httpx_client):
            mock_httpx_client.get.return_value.json.return_value = {"name": "Test Recipe"}
            mock_httpx_client.get.return_value.status_code = 200

            client = MealieClient("http://test", "token")
            client.client = mock_httpx_client

            recipe = client.get_recipe("test-recipe")
            assert recipe["name"] == "Test Recipe"
    """
    mock_client = MagicMock(spec=httpx.Client)
    yield mock_client


@pytest.fixture
def mock_mealie_client(mock_httpx_client: Mock) -> MealieClient:
    """
    Create a MealieClient with mocked httpx.Client.

    This allows testing client methods without making real HTTP requests.
    Configure mock_httpx_client responses to test different scenarios.

    Args:
        mock_httpx_client: Mocked httpx.Client fixture

    Returns:
        MealieClient with mocked HTTP client

    Example:
        def test_client_method(mock_mealie_client, mock_httpx_client):
            # Configure mock response
            mock_httpx_client.get.return_value.json.return_value = {"name": "Test"}
            mock_httpx_client.get.return_value.status_code = 200

            # Test client method
            result = mock_mealie_client.get_recipe("test-slug")

            # Verify
            assert result["name"] == "Test"
            mock_httpx_client.get.assert_called_once()
    """
    client = MealieClient(
        base_url="http://test.example.com",
        api_token="test-token-12345"
    )
    client.client = mock_httpx_client
    return client


@pytest.fixture
def sample_recipe_response() -> Dict[str, Any]:
    """
    Sample recipe response data for testing.

    Returns:
        Dict representing a typical Mealie recipe response
    """
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "slug": "test-recipe",
        "name": "Test Recipe",
        "description": "A test recipe for unit testing",
        "recipeYield": "4 servings",
        "totalTime": "30 minutes",
        "prepTime": "10 minutes",
        "cookTime": "20 minutes",
        "recipeIngredient": [
            "2 cups flour",
            "1 tsp salt",
            "1 cup water"
        ],
        "recipeInstructions": [
            {"text": "Mix dry ingredients"},
            {"text": "Add water and stir"},
            {"text": "Cook for 20 minutes"}
        ],
        "tags": [{"name": "dinner", "slug": "dinner"}],
        "categories": [{"name": "main-course", "slug": "main-course"}],
        "rating": 4.5,
        "orgURL": "https://example.com/recipe"
    }


@pytest.fixture
def sample_mealplan_response() -> Dict[str, Any]:
    """
    Sample meal plan response data for testing.

    Returns:
        Dict representing a typical Mealie meal plan response
    """
    return {
        "id": "650e8400-e29b-41d4-a716-446655440001",
        "date": "2025-12-25",
        "entryType": "dinner",
        "title": "Christmas Dinner",
        "text": "Special holiday meal",
        "recipeId": "550e8400-e29b-41d4-a716-446655440000",
        "recipe": {
            "name": "Roast Turkey",
            "slug": "roast-turkey"
        }
    }


@pytest.fixture
def sample_shopping_list_response() -> Dict[str, Any]:
    """
    Sample shopping list response data for testing.

    Returns:
        Dict representing a typical Mealie shopping list response
    """
    return {
        "id": "750e8400-e29b-41d4-a716-446655440002",
        "name": "Weekly Groceries",
        "listItems": [
            {
                "id": "item-1",
                "note": "2 lbs chicken breast",
                "checked": False,
                "quantity": 2.0,
                "unit": {"name": "pound"}
            },
            {
                "id": "item-2",
                "note": "1 dozen eggs",
                "checked": False,
                "quantity": 1.0,
                "unit": {"name": "dozen"}
            }
        ]
    }


@pytest.fixture
def mock_httpx_response() -> Mock:
    """
    Create a mock httpx.Response object.

    Returns:
        Mock httpx.Response

    Example:
        def test_with_response(mock_httpx_response):
            mock_httpx_response.status_code = 200
            mock_httpx_response.json.return_value = {"key": "value"}

            # Use in tests
            assert mock_httpx_response.status_code == 200
            assert mock_httpx_response.json()["key"] == "value"
    """
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_response.text = ""
    mock_response.raise_for_status = Mock()
    return mock_response


@pytest.fixture
def mock_successful_response(
    mock_httpx_response: Mock,
    sample_recipe_response: Dict[str, Any]
) -> Mock:
    """
    Pre-configured successful response with sample recipe data.

    Args:
        mock_httpx_response: Mock response fixture
        sample_recipe_response: Sample recipe data

    Returns:
        Mock response configured for success (200 OK)
    """
    mock_httpx_response.status_code = 200
    mock_httpx_response.json.return_value = sample_recipe_response
    return mock_httpx_response


@pytest.fixture
def mock_error_response(mock_httpx_response: Mock) -> Mock:
    """
    Pre-configured error response (404 Not Found).

    Args:
        mock_httpx_response: Mock response fixture

    Returns:
        Mock response configured for error (404)
    """
    mock_httpx_response.status_code = 404
    mock_httpx_response.json.return_value = {
        "detail": "Recipe not found"
    }
    mock_httpx_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found",
        request=Mock(),
        response=mock_httpx_response
    )
    return mock_httpx_response


@pytest.fixture
def mock_server_error_response(mock_httpx_response: Mock) -> Mock:
    """
    Pre-configured server error response (500 Internal Server Error).

    Args:
        mock_httpx_response: Mock response fixture

    Returns:
        Mock response configured for server error (500)
    """
    mock_httpx_response.status_code = 500
    mock_httpx_response.json.return_value = {
        "detail": "Internal server error"
    }
    mock_httpx_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "500 Internal Server Error",
        request=Mock(),
        response=mock_httpx_response
    )
    return mock_httpx_response
