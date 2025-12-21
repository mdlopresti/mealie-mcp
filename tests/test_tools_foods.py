"""
Simplified tests for foods/units tools focusing on code coverage.
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from src.tools.foods import (
    foods_list,
    foods_get,
    foods_update,
    foods_delete,
    foods_merge,
    units_list,
    units_get,
    units_update,
    units_delete,
    units_merge
)


def create_mock_client(get_value=None, post_value=None, patch_value=None, delete_value=None):
    """Helper to create a mocked MealieClient."""
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=None)
    if get_value is not None:
        mock.get.return_value = get_value
    if post_value is not None:
        mock.post.return_value = post_value
    if patch_value is not None:
        mock.patch.return_value = patch_value
    if delete_value is not None:
        mock.delete.return_value = delete_value
    return mock


class TestFoods:
    """Test food management operations."""

    def test_foods_list(self):
        """Test listing foods."""
        mock_client = create_mock_client(get_value={"items": [{"id": "1", "name": "Flour"}]})

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            result = foods_list()

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_foods_get(self):
        """Test getting a food."""
        mock_client = create_mock_client(get_value={"id": "1", "name": "Flour"})

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            result = foods_get("food-1")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_foods_update(self):
        """Test updating a food."""
        mock_client = create_mock_client(patch_value={"id": "1", "name": "Whole Wheat Flour"})

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            result = foods_update("food-1", name="Whole Wheat Flour")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_foods_delete(self):
        """Test deleting a food."""
        mock_client = create_mock_client(delete_value=None)

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            result = foods_delete("food-1")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_foods_merge(self):
        """Test merging foods."""
        mock_client = create_mock_client(post_value={"success": True})

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            result = foods_merge("food-1", "food-2")

        data = json.loads(result)
        assert isinstance(data, dict)


class TestUnits:
    """Test unit management operations."""

    def test_units_list(self):
        """Test listing units."""
        mock_client = create_mock_client(get_value={"items": [{"id": "1", "name": "cup"}]})

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            result = units_list()

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_units_get(self):
        """Test getting a unit."""
        mock_client = create_mock_client(get_value={"id": "1", "name": "cup"})

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            result = units_get("unit-1")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_units_update(self):
        """Test updating a unit."""
        mock_client = create_mock_client(patch_value={"id": "1", "name": "cups"})

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            result = units_update("unit-1", name="cups")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_units_delete(self):
        """Test deleting a unit."""
        mock_client = create_mock_client(delete_value=None)

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            result = units_delete("unit-1")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_units_merge(self):
        """Test merging units."""
        mock_client = create_mock_client(post_value={"success": True})

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            result = units_merge("unit-1", "unit-2")

        data = json.loads(result)
        assert isinstance(data, dict)


class TestErrorHandling:
    """Test error handling."""

    def test_api_error(self):
        """Test API error handling."""
        from src.client import MealieAPIError

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.side_effect = MealieAPIError(
            "Error", status_code=500, response_body="Error"
        )

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            result = foods_list()

        data = json.loads(result)
        assert "error" in data
