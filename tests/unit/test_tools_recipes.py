"""Unit tests for recipe tools (src/tools/recipes.py).

Tests recipe search, retrieval, creation, updates, and bulk operations.
All tests use mocked MealieClient to avoid network calls.
"""

import json
import pytest
from unittest.mock import Mock, patch
from src.tools.recipes import (
    recipes_search,
    recipes_get,
    recipes_list,
    _slugify,
    get_recipe_suggestions,
)
from tests.unit.builders import build_recipe, build_tag, build_category


class TestSlugify:
    """Tests for the _slugify utility function."""

    def test_slugify_simple_text(self):
        """Test slugifying simple text."""
        assert _slugify("Hello World") == "hello-world"

    def test_slugify_with_special_chars(self):
        """Test slugifying text with special characters."""
        assert _slugify("Recipe's Name!") == "recipes-name"

    def test_slugify_with_multiple_spaces(self):
        """Test slugifying text with multiple spaces."""
        assert _slugify("Too    Many   Spaces") == "too-many-spaces"

    def test_slugify_already_lowercase(self):
        """Test slugifying already lowercase text."""
        assert _slugify("already-lowercase") == "already-lowercase"

    def test_slugify_with_numbers(self):
        """Test slugifying text with numbers."""
        assert _slugify("Recipe 123") == "recipe-123"


class TestRecipesSearch:
    """Tests for recipes_search function."""

    def test_search_recipes_with_query(self):
        """Test searching recipes with a query string."""
        mock_client = Mock()
        mock_client.get.return_value = {
            "items": [
                build_recipe(name="Pasta Carbonara", slug="pasta-carbonara"),
                build_recipe(name="Pasta Primavera", slug="pasta-primavera")
            ],
            "total": 2
        }

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_search(query="pasta")
            result_dict = json.loads(result)

            assert result_dict["total"] == 2
            assert result_dict["count"] == 2
            assert len(result_dict["recipes"]) == 2
            assert result_dict["recipes"][0]["name"] == "Pasta Carbonara"

            # Verify API call
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert call_args[0][0] == "/api/recipes"
            assert call_args[1]["params"]["search"] == "pasta"

    def test_search_recipes_with_tags(self):
        """Test searching recipes filtered by tags."""
        mock_client = Mock()
        mock_client.get.return_value = {
            "items": [
                build_recipe(
                    name="Vegan Curry",
                    slug="vegan-curry",
                    tags=[build_tag(name="Vegan")]
                )
            ],
            "total": 1
        }

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_search(tags=["Vegan"])
            result_dict = json.loads(result)

            assert result_dict["count"] == 1

            # Verify tags parameter was passed
            call_args = mock_client.get.call_args
            assert "tags" in call_args[1]["params"]

    def test_search_recipes_with_categories(self):
        """Test searching recipes filtered by categories."""
        mock_client = Mock()
        mock_client.get.return_value = {
            "items": [
                build_recipe(
                    name="Chocolate Cake",
                    recipeCategory=[build_category(name="Dessert")]
                )
            ],
            "total": 1
        }

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_search(categories=["Dessert"])
            result_dict = json.loads(result)

            assert result_dict["count"] == 1

            # Verify categories parameter was passed
            call_args = mock_client.get.call_args
            assert "categories" in call_args[1]["params"]

    def test_search_recipes_with_limit(self):
        """Test searching recipes with custom limit."""
        mock_client = Mock()
        recipes = [build_recipe(name=f"Recipe {i}") for i in range(5)]
        mock_client.get.return_value = {"items": recipes, "total": 50}

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_search(limit=5)
            result_dict = json.loads(result)

            assert result_dict["count"] == 5

            # Verify limit was passed as perPage
            call_args = mock_client.get.call_args
            assert call_args[1]["params"]["perPage"] == 5

    def test_search_recipes_empty_results(self):
        """Test searching recipes with no results."""
        mock_client = Mock()
        mock_client.get.return_value = {"items": [], "total": 0}

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_search(query="nonexistent")
            result_dict = json.loads(result)

            assert result_dict["total"] == 0
            assert result_dict["count"] == 0
            assert result_dict["recipes"] == []

    def test_search_recipes_extracts_fields(self):
        """Test that search extracts and formats recipe fields correctly."""
        mock_client = Mock()
        mock_client.get.return_value = {
            "items": [
                build_recipe(
                    name="Test Recipe",
                    slug="test-recipe",
                    description="A test recipe",
                    tags=[build_tag(name="Quick"), build_tag(name="Easy")],
                    recipeCategory=[build_category(name="Dinner")]
                )
            ],
            "total": 1
        }

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_search()
            result_dict = json.loads(result)

            recipe = result_dict["recipes"][0]
            assert recipe["name"] == "Test Recipe"
            assert recipe["slug"] == "test-recipe"
            assert recipe["description"] == "A test recipe"
            assert "Quick" in recipe["tags"]
            assert "Easy" in recipe["tags"]
            assert "Dinner" in recipe["categories"]

    def test_search_recipes_api_error(self):
        """Test handling of API error during search."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.get.side_effect = MealieAPIError(
            "Search failed",
            status_code=500,
            response_body="Internal server error"
        )

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_search(query="test")
            result_dict = json.loads(result)

            assert "error" in result_dict
            assert result_dict["status_code"] == 500

    def test_search_recipes_no_parameters(self):
        """Test searching recipes with default parameters."""
        mock_client = Mock()
        mock_client.get.return_value = {
            "items": [build_recipe()],
            "total": 1
        }

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_search()
            result_dict = json.loads(result)

            # Should still work with defaults
            assert result_dict["count"] >= 0

            # Verify perPage default
            call_args = mock_client.get.call_args
            assert call_args[1]["params"]["perPage"] == 10


class TestRecipesGet:
    """Tests for recipes_get function."""

    def test_get_recipe_by_slug(self):
        """Test retrieving a recipe by slug."""
        recipe = build_recipe(name="Test Recipe", slug="test-recipe")
        mock_client = Mock()
        mock_client.get.return_value = recipe

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_get("test-recipe")
            result_dict = json.loads(result)

            assert result_dict["name"] == "Test Recipe"
            assert result_dict["slug"] == "test-recipe"

            # Verify correct endpoint was called
            mock_client.get.assert_called_once_with("/api/recipes/test-recipe")

    def test_get_recipe_full_details(self):
        """Test that get returns full recipe details."""
        recipe = build_recipe(
            name="Full Recipe",
            recipeIngredient=["2 cups flour", "1 tsp salt"],
            recipeInstructions=[{"text": "Mix"}, {"text": "Bake"}]
        )
        mock_client = Mock()
        mock_client.get.return_value = recipe

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_get("full-recipe")
            result_dict = json.loads(result)

            assert "recipeIngredient" in result_dict
            assert "recipeInstructions" in result_dict
            assert len(result_dict["recipeIngredient"]) == 2

    def test_get_recipe_not_found(self):
        """Test handling of recipe not found error."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.get.side_effect = MealieAPIError(
            "Recipe not found",
            status_code=404,
            response_body="Not found"
        )

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_get("nonexistent")
            result_dict = json.loads(result)

            assert "error" in result_dict
            assert result_dict["status_code"] == 404

    def test_get_recipe_with_special_chars_in_slug(self):
        """Test retrieving recipe with special characters in slug."""
        recipe = build_recipe(slug="recipe-with-123")
        mock_client = Mock()
        mock_client.get.return_value = recipe

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_get("recipe-with-123")

            # Should handle slug correctly
            mock_client.get.assert_called_once_with("/api/recipes/recipe-with-123")


class TestRecipesList:
    """Tests for recipes_list function."""

    def test_list_recipes_default_pagination(self):
        """Test listing recipes with default pagination."""
        recipes = [build_recipe(name=f"Recipe {i}") for i in range(20)]
        mock_client = Mock()
        mock_client.get.return_value = {
            "page": 1,
            "perPage": 20,
            "total": 100,
            "totalPages": 5,
            "items": recipes
        }

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_list()
            result_dict = json.loads(result)

            assert result_dict["page"] == 1
            assert result_dict["per_page"] == 20
            assert result_dict["total"] == 100
            assert result_dict["total_pages"] == 5
            assert len(result_dict["items"]) == 20

    def test_list_recipes_custom_page(self):
        """Test listing recipes with custom page number."""
        mock_client = Mock()
        mock_client.get.return_value = {
            "page": 2,
            "perPage": 20,
            "total": 100,
            "totalPages": 5,
            "items": []
        }

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_list(page=2)

            # Verify page parameter
            call_args = mock_client.get.call_args
            assert call_args[1]["params"]["page"] == 2

    def test_list_recipes_custom_per_page(self):
        """Test listing recipes with custom per_page."""
        mock_client = Mock()
        mock_client.get.return_value = {
            "page": 1,
            "perPage": 50,
            "total": 100,
            "totalPages": 2,
            "items": []
        }

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_list(per_page=50)

            # Verify perPage parameter
            call_args = mock_client.get.call_args
            assert call_args[1]["params"]["perPage"] == 50

    def test_list_recipes_empty_collection(self):
        """Test listing recipes when collection is empty."""
        mock_client = Mock()
        mock_client.get.return_value = {
            "page": 1,
            "perPage": 20,
            "total": 0,
            "totalPages": 0,
            "items": []
        }

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_list()
            result_dict = json.loads(result)

            assert result_dict["total"] == 0
            assert result_dict["items"] == []

    def test_list_recipes_api_error(self):
        """Test handling of API error during list."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.get.side_effect = MealieAPIError(
            "List failed",
            status_code=500,
            response_body="Server error"
        )

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_list()
            result_dict = json.loads(result)

            assert "error" in result_dict
            assert result_dict["status_code"] == 500

    def test_list_recipes_pagination_metadata(self):
        """Test that pagination metadata is correctly extracted."""
        mock_client = Mock()
        mock_client.get.return_value = {
            "page": 3,
            "perPage": 10,
            "total": 47,
            "totalPages": 5,
            "items": [build_recipe()]
        }

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = recipes_list(page=3, per_page=10)
            result_dict = json.loads(result)

            # All metadata should be present
            assert result_dict["page"] == 3
            assert result_dict["per_page"] == 10
            assert result_dict["total"] == 47
            assert result_dict["total_pages"] == 5
import json
import pytest
from unittest.mock import Mock, patch
from src.tools.recipes import get_recipe_suggestions
from src.client import MealieAPIError
from tests.unit.builders import build_recipe


class TestGetRecipeSuggestions:
    """Tests for get_recipe_suggestions function."""

    def test_get_suggestions_with_default_limit(self):
        """Test getting suggestions with default limit."""
        mock_client = Mock()
        mock_client.get_recipe_suggestions.return_value = [
            build_recipe(name="Pasta Carbonara", slug="pasta-carbonara", rating=4.5),
            build_recipe(name="Chicken Parmesan", slug="chicken-parmesan", rating=4.0),
        ]

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = get_recipe_suggestions()
            result_dict = json.loads(result)

            assert result_dict["count"] == 2
            assert len(result_dict["suggestions"]) == 2
            assert result_dict["suggestions"][0]["name"] == "Pasta Carbonara"

            # Verify API call with default limit
            mock_client.get_recipe_suggestions.assert_called_once_with(limit=10)

    def test_get_suggestions_with_custom_limit(self):
        """Test getting suggestions with custom limit."""
        mock_client = Mock()
        mock_client.get_recipe_suggestions.return_value = [
            build_recipe(name="Recipe 1", slug="recipe-1"),
            build_recipe(name="Recipe 2", slug="recipe-2"),
            build_recipe(name="Recipe 3", slug="recipe-3"),
        ]

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = get_recipe_suggestions(limit=3)
            result_dict = json.loads(result)

            assert result_dict["count"] == 3
            assert len(result_dict["suggestions"]) == 3

            # Verify API call with custom limit
            mock_client.get_recipe_suggestions.assert_called_once_with(limit=3)

    def test_get_suggestions_empty_response(self):
        """Test getting suggestions when no suggestions are available."""
        mock_client = Mock()
        mock_client.get_recipe_suggestions.return_value = []

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = get_recipe_suggestions()
            result_dict = json.loads(result)

            assert result_dict["count"] == 0
            assert result_dict["suggestions"] == []

    def test_get_suggestions_with_api_error(self):
        """Test handling API error when getting suggestions."""
        mock_client = Mock()
        mock_client.get_recipe_suggestions.side_effect = MealieAPIError(
            "API error",
            status_code=500,
            response_body="Internal server error"
        )

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = get_recipe_suggestions()
            result_dict = json.loads(result)

            assert "error" in result_dict
            assert result_dict["status_code"] == 500

    def test_get_suggestions_with_connection_error(self):
        """Test handling connection error when getting suggestions."""
        mock_client = Mock()
        mock_client.get_recipe_suggestions.side_effect = Exception("Connection timeout")

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = get_recipe_suggestions()
            result_dict = json.loads(result)

            assert "error" in result_dict
            assert "Connection timeout" in result_dict["error"]

    def test_get_suggestions_non_list_response(self):
        """Test handling non-list response from API (edge case)."""
        mock_client = Mock()
        # API returns a dict instead of a list (edge case)
        mock_client.get_recipe_suggestions.return_value = {"message": "No suggestions"}

        with patch('src.tools.recipes.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = get_recipe_suggestions()
            result_dict = json.loads(result)

            # count should be 0 for non-list responses
            assert result_dict["count"] == 0
            assert result_dict["suggestions"] == {"message": "No suggestions"}
