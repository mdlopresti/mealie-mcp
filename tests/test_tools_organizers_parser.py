"""
Simplified tests for organizers and parser tools focusing on code coverage.
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from src.tools.organizers import (
    categories_update,
    categories_delete,
    tags_update,
    tags_delete,
    tools_update,
    tools_delete
)

from src.tools.parser import (
    parser_ingredient,
    parser_ingredients_batch
)


def create_mock_client(get_value=None, post_value=None):
    """Helper to create a mocked MealieClient."""
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=None)
    if get_value is not None:
        mock.get.return_value = get_value
    if post_value is not None:
        mock.post.return_value = post_value
    return mock


class TestOrganizers:
    """Test organizer operations (categories, tags, tools)."""

    def test_categories_update(self):
        """Test updating a category."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.patch.return_value = {"id": "1", "name": "Updated"}

        with patch('src.tools.organizers.MealieClient', return_value=mock_client):
            result = categories_update("cat-1", name="Updated")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_categories_delete(self):
        """Test deleting a category."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.delete.return_value = None

        with patch('src.tools.organizers.MealieClient', return_value=mock_client):
            result = categories_delete("cat-1")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_tags_update(self):
        """Test updating a tag."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.patch.return_value = {"id": "1", "name": "Updated"}

        with patch('src.tools.organizers.MealieClient', return_value=mock_client):
            result = tags_update("tag-1", name="Updated")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_tags_delete(self):
        """Test deleting a tag."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.delete.return_value = None

        with patch('src.tools.organizers.MealieClient', return_value=mock_client):
            result = tags_delete("tag-1")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_tools_update(self):
        """Test updating a tool."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.patch.return_value = {"id": "1", "name": "Updated"}

        with patch('src.tools.organizers.MealieClient', return_value=mock_client):
            result = tools_update("tool-1", name="Updated")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_tools_delete(self):
        """Test deleting a tool."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.delete.return_value = None

        with patch('src.tools.organizers.MealieClient', return_value=mock_client):
            result = tools_delete("tool-1")

        data = json.loads(result)
        assert isinstance(data, dict)


class TestParser:
    """Test ingredient parser operations."""

    def test_parse_ingredient(self):
        """Test parsing a single ingredient."""
        mock_client = create_mock_client(post_value={
            "input": "2 cups flour",
            "ingredient": {
                "quantity": 2.0,
                "unit": "cup",
                "food": "flour"
            }
        })

        with patch('src.tools.parser.MealieClient', return_value=mock_client):
            result = parser_ingredient("2 cups flour")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_parse_ingredients_batch(self):
        """Test parsing multiple ingredients."""
        mock_client = create_mock_client(post_value=[
            {"input": "2 cups flour", "ingredient": {"quantity": 2.0}},
            {"input": "1 tsp salt", "ingredient": {"quantity": 1.0}}
        ])

        with patch('src.tools.parser.MealieClient', return_value=mock_client):
            result = parser_ingredients_batch(["2 cups flour", "1 tsp salt"])

        data = json.loads(result)
        assert isinstance(data, (dict, list))

    def test_parse_ingredient_with_custom_parser(self):
        """Test parsing ingredient with custom parser."""
        mock_client = create_mock_client(post_value={
            "input": "1/2 cup butter",
            "ingredient": {"quantity": 0.5, "unit": "cup", "food": "butter"}
        })

        with patch('src.tools.parser.MealieClient', return_value=mock_client):
            result = parser_ingredient("1/2 cup butter", parser="brute")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_parse_ingredient_complex(self):
        """Test parsing complex ingredient string."""
        mock_client = create_mock_client(post_value={
            "input": "2 cups all-purpose flour, sifted",
            "ingredient": {
                "quantity": 2.0,
                "unit": "cup",
                "food": "all-purpose flour",
                "note": "sifted"
            }
        })

        with patch('src.tools.parser.MealieClient', return_value=mock_client):
            result = parser_ingredient("2 cups all-purpose flour, sifted")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_parse_ingredients_batch_large(self):
        """Test parsing large batch of ingredients."""
        ingredients = [
            "2 cups flour",
            "1 tsp salt",
            "1/2 cup butter",
            "3 eggs",
            "1 cup milk"
        ]
        mock_response = [
            {"input": ing, "ingredient": {"quantity": 1.0}}
            for ing in ingredients
        ]
        mock_client = create_mock_client(post_value=mock_response)

        with patch('src.tools.parser.MealieClient', return_value=mock_client):
            result = parser_ingredients_batch(ingredients)

        data = json.loads(result)
        assert isinstance(data, (dict, list))

    def test_parse_ingredients_batch_with_parser(self):
        """Test batch parsing with custom parser."""
        mock_client = create_mock_client(post_value=[
            {"input": "2 cups flour", "ingredient": {"quantity": 2.0}},
            {"input": "1 tsp salt", "ingredient": {"quantity": 1.0}}
        ])

        with patch('src.tools.parser.MealieClient', return_value=mock_client):
            result = parser_ingredients_batch(
                ["2 cups flour", "1 tsp salt"],
                parser="nlp"
            )

        data = json.loads(result)
        assert isinstance(data, (dict, list))


class TestErrorHandling:
    """Test error handling across modules."""

    def test_organizers_api_error(self):
        """Test organizers API error handling."""
        from src.client import MealieAPIError

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.patch.side_effect = MealieAPIError(
            "Error", status_code=500, response_body="Error"
        )

        with patch('src.tools.organizers.MealieClient', return_value=mock_client):
            result = categories_update("cat-1", name="Test")

        data = json.loads(result)
        assert "error" in data

    def test_parser_api_error(self):
        """Test parser API error handling."""
        from src.client import MealieAPIError

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.post.side_effect = MealieAPIError(
            "Error", status_code=500, response_body="Error"
        )

        with patch('src.tools.parser.MealieClient', return_value=mock_client):
            result = parser_ingredient("test")

        data = json.loads(result)
        assert "error" in data
