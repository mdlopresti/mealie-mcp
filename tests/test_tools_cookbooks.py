"""
Simplified tests for cookbooks tools focusing on code coverage.
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from src.tools.cookbooks import (
    cookbooks_list,
    cookbooks_create,
    cookbooks_get,
    cookbooks_update,
    cookbooks_delete
)


def create_mock_client(get_value=None, post_value=None, put_value=None, delete_value=None):
    """Helper to create a mocked MealieClient."""
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=None)

    # Mock client methods
    if get_value is not None:
        mock.get.return_value = get_value
        mock.list_cookbooks = MagicMock(return_value=get_value)
        mock.get_cookbook = MagicMock(return_value=get_value)
    if post_value is not None:
        mock.post.return_value = post_value
        mock.create_cookbook = MagicMock(return_value=post_value)
    if put_value is not None:
        mock.put.return_value = put_value
        mock.update_cookbook = MagicMock(return_value=put_value)
    if delete_value is not None:
        mock.delete.return_value = delete_value
        mock.delete_cookbook = MagicMock(return_value=delete_value)

    return mock


class TestCookbooks:
    """Test cookbook management operations."""

    def test_cookbooks_list(self):
        """Test listing cookbooks."""
        mock_data = {"items": [{"id": "1", "name": "Weeknight Dinners"}]}
        mock_client = create_mock_client(get_value=mock_data)

        with patch('src.tools.cookbooks.MealieClient', return_value=mock_client):
            result = cookbooks_list()

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["success"] is True
        assert "cookbooks" in data
        mock_client.list_cookbooks.assert_called_once()

    def test_cookbooks_create(self):
        """Test creating a cookbook."""
        mock_data = {"id": "123", "name": "Weeknight Dinners", "description": "Quick meals"}
        mock_client = create_mock_client(post_value=mock_data)

        with patch('src.tools.cookbooks.MealieClient', return_value=mock_client):
            result = cookbooks_create(name="Weeknight Dinners", description="Quick meals")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["success"] is True
        assert "cookbook" in data
        assert data["message"] == "Cookbook created successfully"
        mock_client.create_cookbook.assert_called_once_with("Weeknight Dinners", "Quick meals", None, False)

    def test_cookbooks_get(self):
        """Test getting a cookbook by ID."""
        mock_data = {"id": "123", "name": "Weeknight Dinners", "description": "Quick meals"}
        mock_client = create_mock_client(get_value=mock_data)

        with patch('src.tools.cookbooks.MealieClient', return_value=mock_client):
            result = cookbooks_get(cookbook_id="123")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["success"] is True
        assert "cookbook" in data
        mock_client.get_cookbook.assert_called_once_with("123")

    def test_cookbooks_update(self):
        """Test updating a cookbook."""
        mock_data = {"id": "123", "name": "Dinner Recipes", "description": "Updated"}
        mock_client = create_mock_client(put_value=mock_data)

        with patch('src.tools.cookbooks.MealieClient', return_value=mock_client):
            result = cookbooks_update(cookbook_id="123", name="Dinner Recipes", description="Updated")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["success"] is True
        assert "cookbook" in data
        assert data["message"] == "Cookbook updated successfully"
        mock_client.update_cookbook.assert_called_once_with("123", "Dinner Recipes", "Updated", None, None)

    def test_cookbooks_delete(self):
        """Test deleting a cookbook."""
        mock_client = create_mock_client(delete_value=None)

        with patch('src.tools.cookbooks.MealieClient', return_value=mock_client):
            result = cookbooks_delete(cookbook_id="123")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["success"] is True
        assert data["message"] == "Cookbook deleted successfully"
        mock_client.delete_cookbook.assert_called_once_with("123")
