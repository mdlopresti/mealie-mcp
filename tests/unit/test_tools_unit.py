"""
Unit tests for MCP tool functions.

Tests tool wrapper functions in isolation using mocked MealieClient.
No real HTTP calls or MCP protocol interaction.
"""

import pytest
import json
from unittest.mock import Mock, patch
from src.tools import recipes


@pytest.mark.unit
def test_search_tool_success(sample_recipe_response: dict):
    """Test mealie_recipes_search tool function."""
    # Arrange
    with patch('src.tools.recipes.get_client') as mock_get_client:
        mock_client = Mock()
        mock_client.search_recipes.return_value = {
            "items": [sample_recipe_response],
            "total": 1
        }
        mock_get_client.return_value = mock_client

        # Act
        result = recipes.search(query="test", tags=None, categories=None, limit=10)

        # Assert
        result_data = json.loads(result)
        assert result_data["total"] == 1
        assert len(result_data["items"]) == 1
        assert result_data["items"][0]["name"] == "Test Recipe"
        mock_client.search_recipes.assert_called_once_with(
            query="test",
            tags=None,
            categories=None,
            limit=10
        )


@pytest.mark.unit
def test_get_recipe_tool_success(sample_recipe_response: dict):
    """Test mealie_recipes_get tool function."""
    # Arrange
    with patch('src.tools.recipes.get_client') as mock_get_client:
        mock_client = Mock()
        mock_client.get_recipe.return_value = sample_recipe_response
        mock_get_client.return_value = mock_client

        # Act
        result = recipes.get(slug="test-recipe")

        # Assert
        result_data = json.loads(result)
        assert result_data["name"] == "Test Recipe"
        assert result_data["slug"] == "test-recipe"
        mock_client.get_recipe.assert_called_once_with("test-recipe")


@pytest.mark.unit
def test_create_recipe_tool_success(sample_recipe_response: dict):
    """Test mealie_recipes_create tool function."""
    # Arrange
    with patch('src.tools.recipes.get_client') as mock_get_client:
        mock_client = Mock()
        mock_client.create_recipe.return_value = sample_recipe_response
        mock_get_client.return_value = mock_client

        # Act
        result = recipes.create(
            name="Test Recipe",
            description="A test recipe",
            recipe_yield="4 servings",
            total_time="30 minutes",
            ingredients=["2 cups flour", "1 tsp salt"],
            instructions=["Mix ingredients", "Cook"]
        )

        # Assert
        result_data = json.loads(result)
        assert result_data["name"] == "Test Recipe"
        mock_client.create_recipe.assert_called_once()


@pytest.mark.unit
def test_update_recipe_tool_success(sample_recipe_response: dict):
    """Test mealie_recipes_update tool function."""
    # Arrange
    with patch('src.tools.recipes.get_client') as mock_get_client:
        mock_client = Mock()
        updated_response = sample_recipe_response.copy()
        updated_response["name"] = "Updated Name"
        mock_client.update_recipe.return_value = updated_response
        mock_get_client.return_value = mock_client

        # Act
        result = recipes.update(
            slug="test-recipe",
            name="Updated Name"
        )

        # Assert
        result_data = json.loads(result)
        assert result_data["name"] == "Updated Name"
        mock_client.update_recipe.assert_called_once_with(
            slug="test-recipe",
            name="Updated Name"
        )


@pytest.mark.unit
def test_delete_recipe_tool_success():
    """Test mealie_recipes_delete tool function."""
    # Arrange
    with patch('src.tools.recipes.get_client') as mock_get_client:
        mock_client = Mock()
        mock_client.delete_recipe.return_value = None
        mock_get_client.return_value = mock_client

        # Act
        result = recipes.delete(slug="test-recipe")

        # Assert
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert "deleted successfully" in result_data["message"]
        mock_client.delete_recipe.assert_called_once_with("test-recipe")


@pytest.mark.unit
def test_tool_error_handling():
    """Test tool function error handling."""
    # Arrange
    with patch('src.tools.recipes.get_client') as mock_get_client:
        mock_client = Mock()
        mock_client.get_recipe.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client

        # Act
        result = recipes.get(slug="test-recipe")

        # Assert
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "error" in result_data
        assert "API Error" in result_data["error"]


@pytest.mark.unit
def test_tool_json_serialization(sample_recipe_response: dict):
    """Test that tool results are properly JSON serialized."""
    # Arrange
    with patch('src.tools.recipes.get_client') as mock_get_client:
        mock_client = Mock()
        mock_client.get_recipe.return_value = sample_recipe_response
        mock_get_client.return_value = mock_client

        # Act
        result = recipes.get(slug="test-recipe")

        # Assert - should be valid JSON string
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert parsed["name"] == "Test Recipe"
