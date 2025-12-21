"""
Simplified tests for organizers tools focusing on code coverage.
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from src.tools.organizers import (
    categories_list,
    categories_create,
    categories_get,
    categories_update,
    categories_delete,
    tags_update,
    tags_delete,
    tools_update,
    tools_delete
)


def create_mock_client(get_value=None, post_value=None, patch_value=None, delete_value=None):
    """Helper to create a mocked MealieClient."""
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=None)

    # Mock client methods
    if get_value is not None:
        mock.get.return_value = get_value
        mock.list_categories = MagicMock(return_value=get_value)
        mock.get_category = MagicMock(return_value=get_value)
    if post_value is not None:
        mock.post.return_value = post_value
        mock.create_category = MagicMock(return_value=post_value)
    if patch_value is not None:
        mock.patch.return_value = patch_value
        mock.update_category = MagicMock(return_value=patch_value)
        mock.update_tag = MagicMock(return_value=patch_value)
        mock.update_tool = MagicMock(return_value=patch_value)
    if delete_value is not None:
        mock.delete.return_value = delete_value
        mock.delete_category = MagicMock(return_value=delete_value)
        mock.delete_tag = MagicMock(return_value=delete_value)
        mock.delete_tool = MagicMock(return_value=delete_value)

    return mock


class TestCategories:
    """Test category management operations."""

    def test_categories_list(self):
        """Test listing categories."""
        mock_data = {"items": [{"id": "1", "name": "Breakfast", "slug": "breakfast"}]}
        mock_client = create_mock_client(get_value=mock_data)

        with patch('src.tools.organizers.MealieClient', return_value=mock_client):
            result = categories_list()

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["success"] is True
        assert "categories" in data
        mock_client.list_categories.assert_called_once()

    def test_categories_create(self):
        """Test creating a category."""
        mock_data = {"id": "123", "name": "Breakfast", "slug": "breakfast"}
        mock_client = create_mock_client(post_value=mock_data)

        with patch('src.tools.organizers.MealieClient', return_value=mock_client):
            result = categories_create(name="Breakfast")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["success"] is True
        assert "category" in data
        assert data["message"] == "Category created successfully"
        mock_client.create_category.assert_called_once_with("Breakfast")

    def test_categories_get(self):
        """Test getting a category by ID."""
        mock_data = {"id": "123", "name": "Breakfast", "slug": "breakfast"}
        mock_client = create_mock_client(get_value=mock_data)

        with patch('src.tools.organizers.MealieClient', return_value=mock_client):
            result = categories_get(category_id="123")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["success"] is True
        assert "category" in data
        mock_client.get_category.assert_called_once_with("123")

    def test_categories_update(self):
        """Test updating a category."""
        mock_data = {"id": "123", "name": "Lunch", "slug": "lunch"}
        mock_client = create_mock_client(patch_value=mock_data)

        with patch('src.tools.organizers.MealieClient', return_value=mock_client):
            result = categories_update(category_id="123", name="Lunch")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["success"] is True
        assert "category" in data
        assert data["message"] == "Category updated successfully"
        mock_client.update_category.assert_called_once_with("123", "Lunch", None)

    def test_categories_delete(self):
        """Test deleting a category."""
        mock_client = create_mock_client(delete_value=None)

        with patch('src.tools.organizers.MealieClient', return_value=mock_client):
            result = categories_delete(category_id="123")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["success"] is True
        assert data["message"] == "Category deleted successfully"
        mock_client.delete_category.assert_called_once_with("123")


class TestTags:
    """Test tag management operations."""

    def test_tags_update(self):
        """Test updating a tag."""
        mock_data = {"id": "123", "name": "Vegetarian", "slug": "vegetarian"}
        mock_client = create_mock_client(patch_value=mock_data)

        with patch('src.tools.organizers.MealieClient', return_value=mock_client):
            result = tags_update(tag_id="123", name="Vegetarian")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["success"] is True
        assert "tag" in data
        mock_client.update_tag.assert_called_once_with("123", "Vegetarian", None)

    def test_tags_delete(self):
        """Test deleting a tag."""
        mock_client = create_mock_client(delete_value=None)

        with patch('src.tools.organizers.MealieClient', return_value=mock_client):
            result = tags_delete(tag_id="123")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["success"] is True
        assert data["message"] == "Tag deleted successfully"
        mock_client.delete_tag.assert_called_once_with("123")


class TestTools:
    """Test tool management operations."""

    def test_tools_update(self):
        """Test updating a tool."""
        mock_data = {"id": "123", "name": "Blender", "slug": "blender"}
        mock_client = create_mock_client(patch_value=mock_data)

        with patch('src.tools.organizers.MealieClient', return_value=mock_client):
            result = tools_update(tool_id="123", name="Blender")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["success"] is True
        assert "tool" in data
        mock_client.update_tool.assert_called_once_with("123", "Blender", None)

    def test_tools_delete(self):
        """Test deleting a tool."""
        mock_client = create_mock_client(delete_value=None)

        with patch('src.tools.organizers.MealieClient', return_value=mock_client):
            result = tools_delete(tool_id="123")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["success"] is True
        assert data["message"] == "Tool deleted successfully"
        mock_client.delete_tool.assert_called_once_with("123")
