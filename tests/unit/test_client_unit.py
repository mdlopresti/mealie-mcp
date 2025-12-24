"""
Unit tests for MealieClient methods.

Tests individual client methods in isolation using mocked HTTP responses.
No real HTTP calls are made - all responses are mocked.
"""

import pytest
import httpx
from unittest.mock import Mock
from src.client import MealieClient


@pytest.mark.unit
def test_get_recipe_success(
    mock_mealie_client: MealieClient,
    mock_httpx_client: Mock,
    sample_recipe_response: dict
):
    """Test successful recipe retrieval."""
    # Arrange
    mock_httpx_client.get.return_value.json.return_value = sample_recipe_response
    mock_httpx_client.get.return_value.status_code = 200
    mock_httpx_client.get.return_value.raise_for_status = Mock()

    # Act
    recipe = mock_mealie_client.get_recipe("test-recipe")

    # Assert
    assert recipe["name"] == "Test Recipe"
    assert recipe["slug"] == "test-recipe"
    assert recipe["description"] == "A test recipe for unit testing"
    mock_httpx_client.get.assert_called_once_with("/api/recipes/test-recipe")


@pytest.mark.unit
def test_get_recipe_not_found(
    mock_mealie_client: MealieClient,
    mock_httpx_client: Mock
):
    """Test recipe retrieval when recipe doesn't exist."""
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found",
        request=Mock(),
        response=mock_response
    )
    mock_httpx_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(httpx.HTTPStatusError):
        mock_mealie_client.get_recipe("non-existent-recipe")

    mock_httpx_client.get.assert_called_once_with("/api/recipes/non-existent-recipe")


@pytest.mark.unit
def test_search_recipes_success(
    mock_mealie_client: MealieClient,
    mock_httpx_client: Mock,
    sample_recipe_response: dict
):
    """Test successful recipe search."""
    # Arrange
    search_results = {
        "items": [sample_recipe_response],
        "total": 1,
        "page": 1,
        "per_page": 10
    }
    mock_httpx_client.get.return_value.json.return_value = search_results
    mock_httpx_client.get.return_value.status_code = 200
    mock_httpx_client.get.return_value.raise_for_status = Mock()

    # Act
    results = mock_mealie_client.search_recipes(query="test")

    # Assert
    assert len(results["items"]) == 1
    assert results["total"] == 1
    assert results["items"][0]["name"] == "Test Recipe"
    mock_httpx_client.get.assert_called_once()


@pytest.mark.unit
def test_create_recipe_success(
    mock_mealie_client: MealieClient,
    mock_httpx_client: Mock,
    sample_recipe_response: dict
):
    """Test successful recipe creation."""
    # Arrange
    mock_httpx_client.post.return_value.json.return_value = sample_recipe_response
    mock_httpx_client.post.return_value.status_code = 201
    mock_httpx_client.post.return_value.raise_for_status = Mock()

    # Act
    recipe = mock_mealie_client.create_recipe(
        name="Test Recipe",
        description="A test recipe"
    )

    # Assert
    assert recipe["name"] == "Test Recipe"
    assert recipe["slug"] == "test-recipe"
    mock_httpx_client.post.assert_called_once()
    call_args = mock_httpx_client.post.call_args
    assert call_args[0][0] == "/api/recipes"
    assert call_args[1]["json"]["name"] == "Test Recipe"


@pytest.mark.unit
def test_update_recipe_success(
    mock_mealie_client: MealieClient,
    mock_httpx_client: Mock,
    sample_recipe_response: dict
):
    """Test successful recipe update."""
    # Arrange
    updated_response = sample_recipe_response.copy()
    updated_response["name"] = "Updated Recipe Name"
    mock_httpx_client.put.return_value.json.return_value = updated_response
    mock_httpx_client.put.return_value.status_code = 200
    mock_httpx_client.put.return_value.raise_for_status = Mock()

    # Act
    recipe = mock_mealie_client.update_recipe(
        slug="test-recipe",
        name="Updated Recipe Name"
    )

    # Assert
    assert recipe["name"] == "Updated Recipe Name"
    assert recipe["slug"] == "test-recipe"
    mock_httpx_client.put.assert_called_once()


@pytest.mark.unit
def test_delete_recipe_success(
    mock_mealie_client: MealieClient,
    mock_httpx_client: Mock
):
    """Test successful recipe deletion."""
    # Arrange
    mock_httpx_client.delete.return_value.status_code = 200
    mock_httpx_client.delete.return_value.raise_for_status = Mock()

    # Act
    mock_mealie_client.delete_recipe("test-recipe")

    # Assert
    mock_httpx_client.delete.assert_called_once_with("/api/recipes/test-recipe")


@pytest.mark.unit
def test_get_mealplan_success(
    mock_mealie_client: MealieClient,
    mock_httpx_client: Mock,
    sample_mealplan_response: dict
):
    """Test successful meal plan retrieval."""
    # Arrange
    mock_httpx_client.get.return_value.json.return_value = sample_mealplan_response
    mock_httpx_client.get.return_value.status_code = 200
    mock_httpx_client.get.return_value.raise_for_status = Mock()

    # Act
    mealplan = mock_mealie_client.get_mealplan(sample_mealplan_response["id"])

    # Assert
    assert mealplan["date"] == "2025-12-25"
    assert mealplan["entryType"] == "dinner"
    assert mealplan["recipe"]["name"] == "Roast Turkey"


@pytest.mark.unit
def test_list_shopping_lists_success(
    mock_mealie_client: MealieClient,
    mock_httpx_client: Mock,
    sample_shopping_list_response: dict
):
    """Test successful shopping lists retrieval."""
    # Arrange
    mock_httpx_client.get.return_value.json.return_value = [sample_shopping_list_response]
    mock_httpx_client.get.return_value.status_code = 200
    mock_httpx_client.get.return_value.raise_for_status = Mock()

    # Act
    shopping_lists = mock_mealie_client.list_shopping_lists()

    # Assert
    assert len(shopping_lists) == 1
    assert shopping_lists[0]["name"] == "Weekly Groceries"
    assert len(shopping_lists[0]["listItems"]) == 2
    mock_httpx_client.get.assert_called_once_with("/api/groups/shopping/lists")


@pytest.mark.unit
def test_client_initialization():
    """Test MealieClient initialization."""
    # Act
    client = MealieClient(
        base_url="https://recipe.example.com",
        api_token="test-token-123"
    )

    # Assert
    assert client.base_url == "https://recipe.example.com"
    assert client.api_token == "test-token-123"
    assert client.client is not None
    assert "Authorization" in client.client.headers
    assert client.client.headers["Authorization"] == "Bearer test-token-123"


@pytest.mark.unit
def test_client_request_with_server_error(
    mock_mealie_client: MealieClient,
    mock_httpx_client: Mock
):
    """Test client behavior with server error (500)."""
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "500 Internal Server Error",
        request=Mock(),
        response=mock_response
    )
    mock_httpx_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(httpx.HTTPStatusError):
        mock_mealie_client.get_recipe("test-recipe")
