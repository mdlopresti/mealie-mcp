"""Unit tests for organizer tools (src/tools/organizers.py) - Fixed version.

Tests management of tags, categories, and kitchen tools.
All tests use mocked MealieClient to avoid network calls.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.tools.organizers import (
    tags_list,
    tags_create,
    categories_list,
    categories_create,
    tools_list,
    tools_create
)
from tests.unit.builders import build_tag, build_category, build_tool


class TestTagsList:
    """Tests for tags_list function."""

    def test_list_all_tags(self):
        """Test listing all tags."""
        mock_client = Mock()
        mock_client.list_tags.return_value = [
            build_tag(name="Vegan"),
            build_tag(name="Quick"),
            build_tag(name="Healthy")
        ]

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = tags_list()
            result_dict = json.loads(result)

            # Should have success and tags keys
            assert result_dict["success"] is True
            assert len(result_dict["tags"]) == 3

    def test_list_tags_empty(self):
        """Test listing tags when none exist."""
        mock_client = Mock()
        mock_client.list_tags.return_value = []

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = tags_list()
            result_dict = json.loads(result)

            assert result_dict["success"] is True
            assert result_dict["tags"] == []

    def test_list_tags_api_error(self):
        """Test handling of API error during tags list."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.list_tags.side_effect = MealieAPIError(
            "Failed to fetch",
            status_code=500,
            response_body="Server error"
        )

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = tags_list()
            result_dict = json.loads(result)

            assert "error" in result_dict


class TestTagsCreate:
    """Tests for tags_create function."""

    def test_create_tag(self):
        """Test creating a new tag."""
        mock_client = Mock()
        mock_client.create_tag.return_value = build_tag(name="Gluten Free")

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = tags_create(name="Gluten Free")
            result_dict = json.loads(result)

            assert result_dict["success"] is True
            assert result_dict["tag"]["name"] == "Gluten Free"

    def test_create_tag_generates_slug(self):
        """Test that tag creation generates slug from name."""
        mock_client = Mock()
        mock_client.create_tag.return_value = build_tag(
            name="Gluten Free",
            slug="gluten-free"
        )

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = tags_create(name="Gluten Free")
            result_dict = json.loads(result)

            assert result_dict["tag"]["slug"] == "gluten-free"

    def test_create_tag_duplicate_error(self):
        """Test handling of duplicate tag error."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.create_tag.side_effect = MealieAPIError(
            "Tag already exists",
            status_code=409,
            response_body="Duplicate tag"
        )

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = tags_create(name="Existing Tag")
            result_dict = json.loads(result)

            assert "error" in result_dict


class TestCategoriesList:
    """Tests for categories_list function."""

    def test_list_all_categories(self):
        """Test listing all categories."""
        mock_client = Mock()
        mock_client.list_categories.return_value = [
            build_category(name="Breakfast"),
            build_category(name="Lunch"),
            build_category(name="Dinner")
        ]

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = categories_list()
            result_dict = json.loads(result)

            assert result_dict["success"] is True
            assert len(result_dict["categories"]) == 3

    def test_list_categories_empty(self):
        """Test listing categories when none exist."""
        mock_client = Mock()
        mock_client.list_categories.return_value = []

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = categories_list()
            result_dict = json.loads(result)

            assert result_dict["success"] is True
            assert result_dict["categories"] == []

    def test_list_categories_api_error(self):
        """Test handling of API error during categories list."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.list_categories.side_effect = MealieAPIError(
            "Failed to fetch",
            status_code=500,
            response_body="Server error"
        )

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = categories_list()
            result_dict = json.loads(result)

            assert "error" in result_dict


class TestCategoriesCreate:
    """Tests for categories_create function."""

    def test_create_category(self):
        """Test creating a new category."""
        mock_client = Mock()
        mock_client.create_category.return_value = build_category(name="Appetizers")

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = categories_create(name="Appetizers")
            result_dict = json.loads(result)

            assert result_dict["success"] is True
            assert result_dict["category"]["name"] == "Appetizers"

    def test_create_category_generates_slug(self):
        """Test that category creation generates slug from name."""
        mock_client = Mock()
        mock_client.create_category.return_value = build_category(
            name="Side Dishes",
            slug="side-dishes"
        )

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = categories_create(name="Side Dishes")
            result_dict = json.loads(result)

            assert result_dict["category"]["slug"] == "side-dishes"

    def test_create_category_duplicate_error(self):
        """Test handling of duplicate category error."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.create_category.side_effect = MealieAPIError(
            "Category already exists",
            status_code=409,
            response_body="Duplicate category"
        )

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = categories_create(name="Existing Category")
            result_dict = json.loads(result)

            assert "error" in result_dict


class TestToolsList:
    """Tests for tools_list function."""

    def test_list_all_tools(self):
        """Test listing all kitchen tools."""
        mock_client = Mock()
        mock_client.list_tools.return_value = [
            build_tool(name="Blender"),
            build_tool(name="Stand Mixer"),
            build_tool(name="Food Processor")
        ]

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = tools_list()
            result_dict = json.loads(result)

            assert result_dict["success"] is True
            assert len(result_dict["tools"]) == 3

    def test_list_tools_empty(self):
        """Test listing tools when none exist."""
        mock_client = Mock()
        mock_client.list_tools.return_value = []

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = tools_list()
            result_dict = json.loads(result)

            assert result_dict["success"] is True
            assert result_dict["tools"] == []

    def test_list_tools_api_error(self):
        """Test handling of API error during tools list."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.list_tools.side_effect = MealieAPIError(
            "Failed to fetch",
            status_code=500,
            response_body="Server error"
        )

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = tools_list()
            result_dict = json.loads(result)

            assert "error" in result_dict


class TestToolsCreate:
    """Tests for tools_create function."""

    def test_create_tool(self):
        """Test creating a new kitchen tool."""
        mock_client = Mock()
        mock_client.create_tool.return_value = build_tool(name="Slow Cooker")

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = tools_create(name="Slow Cooker")
            result_dict = json.loads(result)

            assert result_dict["success"] is True
            assert result_dict["tool"]["name"] == "Slow Cooker"

    def test_create_tool_generates_slug(self):
        """Test that tool creation generates slug from name."""
        mock_client = Mock()
        mock_client.create_tool.return_value = build_tool(
            name="Instant Pot",
            slug="instant-pot"
        )

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = tools_create(name="Instant Pot")
            result_dict = json.loads(result)

            assert result_dict["tool"]["slug"] == "instant-pot"

    def test_create_tool_duplicate_error(self):
        """Test handling of duplicate tool error."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.create_tool.side_effect = MealieAPIError(
            "Tool already exists",
            status_code=409,
            response_body="Duplicate tool"
        )

        with patch('src.tools.organizers.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = tools_create(name="Existing Tool")
            result_dict = json.loads(result)

            assert "error" in result_dict
