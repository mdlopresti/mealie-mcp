"""
Simple tests for recipe tools to boost coverage.

Uses monkeypatch to mock MealieClient for testing tool functions.
"""

import json
import pytest
from unittest.mock import MagicMock, patch

# Import tool functions
from src.tools.recipes import (
    recipes_search,
    recipes_get,
    recipes_list,
    _slugify
)


class TestSlugifyHelper:
    """Test the _slugify helper function."""

    def test_slugify_basic(self):
        """Test basic slugification."""
        assert _slugify("Test Recipe") == "test-recipe"

    def test_slugify_special_chars(self):
        """Test removal of special characters."""
        assert _slugify("Test & Recipe!") == "test-recipe"

    def test_slugify_multiple_spaces(self):
        """Test collapsing multiple spaces."""
        assert _slugify("Test   Recipe") == "test-recipe"

    def test_slugify_leading_trailing(self):
        """Test strip of leading/trailing whitespace."""
        assert _slugify("  Test Recipe  ") == "test-recipe"


class TestRecipesSearch:
    """Test recipes_search function."""

    def test_search_basic(self, monkeypatch):
        """Test basic recipe search."""
        # Mock the MealieClient
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.return_value = {
            "items": [
                {
                    "name": "Test Recipe",
                    "slug": "test-recipe",
                    "description": "A test",
                    "rating": 5,
                    "tags": [{"name": "Dinner"}],
                    "recipeCategory": [{"name": "Main"}]
                }
            ],
            "total": 1
        }

        # Patch MealieClient class
        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_search(query="test", limit=10)

        # Verify JSON response
        data = json.loads(result)
        assert data["count"] == 1
        assert data["total"] == 1
        assert len(data["recipes"]) == 1
        assert data["recipes"][0]["name"] == "Test Recipe"
        assert data["recipes"][0]["tags"] == ["Dinner"]

    def test_search_with_tags_and_categories(self, monkeypatch):
        """Test search with tag and category filters."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.return_value = {
            "items": [],
            "total": 0
        }

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_search(
                query="vegan",
                tags=["Vegan"],
                categories=["Dinner"],
                limit=5
            )

        # Verify the client was called with correct params
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "/api/recipes"
        params = call_args[1]["params"]
        assert params["search"] == "vegan"
        assert params["tags"] == ["Vegan"]
        assert params["categories"] == ["Dinner"]
        assert params["perPage"] == 5

    def test_search_api_error(self):
        """Test handling of API errors."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        # Import MealieAPIError
        from src.client import MealieAPIError

        # Make client.get raise an error
        mock_client.get.side_effect = MealieAPIError(
            "API Error",
            status_code=500,
            response_body="Internal error"
        )

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_search(query="test")

        # Verify error response
        data = json.loads(result)
        assert "error" in data
        assert data["status_code"] == 500

    def test_search_unexpected_response_format(self):
        """Test handling of unexpected response format."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        # Return response without "items" key
        mock_client.get.return_value = {"data": "unexpected"}

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_search(query="test")

        # Should return the response as-is
        data = json.loads(result)
        assert data == {"data": "unexpected"}


class TestRecipesGet:
    """Test recipes_get function."""

    def test_get_basic(self):
        """Test basic recipe retrieval."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.return_value = {
            "name": "Test Recipe",
            "slug": "test-recipe",
            "description": "A test recipe"
        }

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_get(slug="test-recipe")

        # Verify response
        data = json.loads(result)
        assert data["name"] == "Test Recipe"
        assert data["slug"] == "test-recipe"

        # Verify client was called correctly
        mock_client.get.assert_called_once_with("/api/recipes/test-recipe")


class TestRecipesList:
    """Test recipes_list function."""

    def test_list_basic(self):
        """Test basic recipe listing."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.return_value = {
            "items": [
                {"name": "Recipe 1", "slug": "recipe-1"},
                {"name": "Recipe 2", "slug": "recipe-2"}
            ],
            "total": 2
        }

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_list(page=1, per_page=20)

        # Verify response
        data = json.loads(result)
        assert "items" in data
        assert len(data["items"]) == 2
        assert data["total"] == 2

        # Verify client was called correctly
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["page"] == 1
        assert call_args[1]["params"]["perPage"] == 20
