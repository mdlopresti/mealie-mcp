"""
Unit tests for recipe rating tools.

Tests the rating tool functions with mocked HTTP responses.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.tools.recipes import (
    set_recipe_rating,
    get_user_ratings,
    get_recipe_rating,
)


class TestSetRecipeRating:
    """Test set_recipe_rating tool function."""

    @patch('src.tools.recipes.MealieClient')
    def test_set_rating_success(self, mock_client_class):
        """Test successfully setting a recipe rating."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        mock_client.set_recipe_rating.return_value = {
            "rating": 5.0,
            "isFavorite": None
        }

        # Call function
        result_json = set_recipe_rating(slug="test-recipe", rating=5.0)
        result = json.loads(result_json)

        # Assertions
        assert result["success"] is True
        assert "Rating set to 5.0" in result["message"]
        assert result["data"]["rating"] == 5.0
        mock_client.set_recipe_rating.assert_called_once_with("test-recipe", 5.0, None)

    @patch('src.tools.recipes.MealieClient')
    def test_set_rating_with_favorite(self, mock_client_class):
        """Test setting rating with favorite flag."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        mock_client.set_recipe_rating.return_value = {
            "rating": 4.5,
            "isFavorite": True
        }

        # Call function
        result_json = set_recipe_rating(slug="test-recipe", rating=4.5, is_favorite=True)
        result = json.loads(result_json)

        # Assertions
        assert result["success"] is True
        assert result["data"]["rating"] == 4.5
        assert result["data"]["isFavorite"] is True
        mock_client.set_recipe_rating.assert_called_once_with("test-recipe", 4.5, True)

    @patch('src.tools.recipes.MealieClient')
    def test_set_rating_decimal(self, mock_client_class):
        """Test setting a decimal rating."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        mock_client.set_recipe_rating.return_value = {
            "rating": 3.5,
            "isFavorite": None
        }

        # Call function
        result_json = set_recipe_rating(slug="test-recipe", rating=3.5)
        result = json.loads(result_json)

        # Assertions
        assert result["success"] is True
        assert result["data"]["rating"] == 3.5

    @patch('src.tools.recipes.MealieClient')
    def test_set_rating_clear(self, mock_client_class):
        """Test clearing a rating by setting to 0."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        mock_client.set_recipe_rating.return_value = {
            "rating": 0,
            "isFavorite": None
        }

        # Call function
        result_json = set_recipe_rating(slug="test-recipe", rating=0)
        result = json.loads(result_json)

        # Assertions
        assert result["success"] is True
        assert result["data"]["rating"] == 0

    def test_set_rating_invalid_too_high(self):
        """Test validation error when rating is too high."""
        result_json = set_recipe_rating(slug="test-recipe", rating=6.0)
        result = json.loads(result_json)

        assert "error" in result
        assert "between 0 and 5" in result["error"]

    def test_set_rating_invalid_negative(self):
        """Test validation error when rating is negative."""
        result_json = set_recipe_rating(slug="test-recipe", rating=-1.0)
        result = json.loads(result_json)

        assert "error" in result
        assert "between 0 and 5" in result["error"]


class TestGetUserRatings:
    """Test get_user_ratings tool function."""

    @patch('src.tools.recipes.MealieClient')
    def test_get_ratings_success(self, mock_client_class):
        """Test successfully getting user ratings."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        mock_client.get_user_ratings.return_value = {
            "ratings": [
                {
                    "recipeId": "123",
                    "recipeName": "Chicken Parmesan",
                    "rating": 5.0,
                    "isFavorite": True
                },
                {
                    "recipeId": "456",
                    "recipeName": "Pasta Carbonara",
                    "rating": 4.0,
                    "isFavorite": False
                }
            ]
        }

        # Call function
        result_json = get_user_ratings()
        result = json.loads(result_json)

        # Assertions
        assert result["success"] is True
        assert "ratings" in result
        assert len(result["ratings"]["ratings"]) == 2
        assert result["ratings"]["ratings"][0]["rating"] == 5.0
        assert result["ratings"]["ratings"][1]["rating"] == 4.0
        mock_client.get_user_ratings.assert_called_once()

    @patch('src.tools.recipes.MealieClient')
    def test_get_ratings_empty(self, mock_client_class):
        """Test getting ratings when user has no ratings."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        mock_client.get_user_ratings.return_value = {
            "ratings": []
        }

        # Call function
        result_json = get_user_ratings()
        result = json.loads(result_json)

        # Assertions
        assert result["success"] is True
        assert result["ratings"]["ratings"] == []


class TestGetRecipeRating:
    """Test get_recipe_rating tool function."""

    @patch('src.tools.recipes.MealieClient')
    def test_get_rating_success(self, mock_client_class):
        """Test successfully getting a recipe rating."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        mock_client.get_recipe_rating.return_value = {
            "recipeId": "550e8400-e29b-41d4-a716-446655440000",
            "rating": 4.5,
            "isFavorite": True
        }

        # Call function
        result_json = get_recipe_rating(recipe_id="550e8400-e29b-41d4-a716-446655440000")
        result = json.loads(result_json)

        # Assertions
        assert result["success"] is True
        assert result["rating"]["rating"] == 4.5
        assert result["rating"]["isFavorite"] is True
        mock_client.get_recipe_rating.assert_called_once_with("550e8400-e29b-41d4-a716-446655440000")

    @patch('src.tools.recipes.MealieClient')
    def test_get_rating_no_rating(self, mock_client_class):
        """Test getting rating for an unrated recipe."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        mock_client.get_recipe_rating.return_value = {
            "recipeId": "550e8400-e29b-41d4-a716-446655440000",
            "rating": None,
            "isFavorite": False
        }

        # Call function
        result_json = get_recipe_rating(recipe_id="550e8400-e29b-41d4-a716-446655440000")
        result = json.loads(result_json)

        # Assertions
        assert result["success"] is True
        assert result["rating"]["rating"] is None
        assert result["rating"]["isFavorite"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
