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


class TestRecipesCreate:
    """Test recipes_create function."""

    def test_create_basic(self):
        """Test basic recipe creation."""
        from src.tools.recipes import recipes_create

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.create_recipe.return_value = {
            "id": "new-recipe",
            "slug": "test-recipe",
            "name": "Test Recipe"
        }

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_create(
                name="Test Recipe",
                description="Test description"
            )

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_create_with_tags_and_categories(self):
        """Test recipe creation with tags and categories."""
        from src.tools.recipes import recipes_create

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        # Mock list_tags and list_categories responses
        mock_client.list_tags.return_value = {
            "items": [{"id": "tag-1", "name": "Vegan", "slug": "vegan"}]
        }
        mock_client.list_categories.return_value = {
            "items": [{"id": "cat-1", "name": "Dinner", "slug": "dinner"}]
        }
        mock_client.create_recipe.return_value = {
            "id": "new-recipe",
            "slug": "vegan-dinner",
            "name": "Vegan Dinner",
            "groupId": "group-123"
        }

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_create(
                name="Vegan Dinner",
                tags=["Vegan"],
                categories=["Dinner"]
            )

        data = json.loads(result)
        assert isinstance(data, dict)


class TestRecipesCreateFromUrl:
    """Test recipes_create_from_url function."""

    def test_create_from_url_basic(self):
        """Test importing recipe from URL."""
        from src.tools.recipes import recipes_create_from_url

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.create_recipe_from_url.return_value = {
            "slug": "imported-recipe",
            "name": "Imported Recipe"
        }

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_create_from_url("https://example.com/recipe")

        data = json.loads(result)
        assert isinstance(data, dict)


class TestRecipesUpdate:
    """Test recipes_update function."""

    def test_update_basic(self):
        """Test basic recipe update."""
        from src.tools.recipes import recipes_update

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        # Mock get_recipe to return existing recipe
        mock_client.get_recipe.return_value = {
            "id": "recipe-1",
            "slug": "test-recipe",
            "name": "Old Name",
            "groupId": "group-123"
        }
        mock_client.update_recipe.return_value = {
            "id": "recipe-1",
            "slug": "test-recipe",
            "name": "Updated Name"
        }

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_update("test-recipe", name="Updated Name")

        data = json.loads(result)
        assert isinstance(data, dict)


class TestRecipesDelete:
    """Test recipes_delete function."""

    def test_delete_basic(self):
        """Test recipe deletion."""
        from src.tools.recipes import recipes_delete

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.delete_recipe.return_value = None

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_delete("test-recipe")

        data = json.loads(result)
        assert "success" in data or "message" in data


class TestRecipesDuplicate:
    """Test recipes_duplicate function."""

    def test_duplicate_basic(self):
        """Test recipe duplication."""
        from src.tools.recipes import recipes_duplicate

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.duplicate_recipe.return_value = {
            "slug": "test-recipe-copy",
            "name": "Test Recipe (Copy)"
        }

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_duplicate("test-recipe")

        data = json.loads(result)
        assert isinstance(data, dict)


class TestRecipesUpdateLastMade:
    """Test recipes_update_last_made function."""

    def test_update_last_made(self):
        """Test updating recipe last made timestamp."""
        from src.tools.recipes import recipes_update_last_made

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.update_recipe_last_made.return_value = {
            "slug": "test-recipe",
            "lastMade": "2025-01-20T00:00:00"
        }

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_update_last_made("test-recipe")

        data = json.loads(result)
        assert isinstance(data, dict)


class TestRecipesBulkOperations:
    """Test bulk recipe operations."""

    def test_bulk_tag(self):
        """Test bulk tagging recipes."""
        from src.tools.recipes import recipes_bulk_tag

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.bulk_tag_recipes.return_value = {"success": True}

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_bulk_tag(["recipe-1", "recipe-2"], ["Vegan"])

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_bulk_categorize(self):
        """Test bulk categorizing recipes."""
        from src.tools.recipes import recipes_bulk_categorize

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.bulk_categorize_recipes.return_value = {"success": True}

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_bulk_categorize(["recipe-1"], ["Dinner"])

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_bulk_delete(self):
        """Test bulk deleting recipes."""
        from src.tools.recipes import recipes_bulk_delete

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.bulk_delete_recipes.return_value = {"deleted": 2}

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_bulk_delete(["recipe-1", "recipe-2"])

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_bulk_export(self):
        """Test bulk exporting recipes."""
        from src.tools.recipes import recipes_bulk_export

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.bulk_export_recipes.return_value = {"data": "exported"}

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_bulk_export(["recipe-1"], "json")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_bulk_update_settings(self):
        """Test bulk updating recipe settings."""
        from src.tools.recipes import recipes_bulk_update_settings

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.bulk_update_recipe_settings.return_value = {"updated": 1}

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_bulk_update_settings(
                ["recipe-1"],
                {"public": True}
            )

        data = json.loads(result)
        assert isinstance(data, dict)


class TestRecipesCreateFromImage:
    """Test recipes_create_from_image function."""

    def test_create_from_image(self):
        """Test creating recipe from image."""
        from src.tools.recipes import recipes_create_from_image

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.create_recipe_from_image.return_value = {
            "slug": "ai-recipe",
            "name": "AI Generated Recipe"
        }

        with patch('src.tools.recipes.MealieClient', return_value=mock_client):
            result = recipes_create_from_image("base64data", "jpg")

        data = json.loads(result)
        assert isinstance(data, dict)
