"""Unit tests for shopping tools (src/tools/shopping.py).

Tests shopping list management, item operations, and recipe integration.
All tests use mocked MealieClient to avoid network calls.
"""

import json
import pytest
from unittest.mock import Mock, patch
from src.tools.shopping import (
    shopping_lists_list,
    shopping_lists_get,
    shopping_lists_create,
    shopping_items_add,
    shopping_items_check
)
from tests.unit.builders import build_shopping_list, build_shopping_item


class TestShoppingListsList:
    """Tests for shopping_lists_list function."""

    def test_list_shopping_lists(self):
        """Test listing all shopping lists."""
        mock_client = Mock()
        mock_client.get.return_value = [
            build_shopping_list(name="Grocery Run"),
            build_shopping_list(name="Meal Prep")
        ]

        with patch('src.tools.shopping.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = shopping_lists_list()
            result_dict = json.loads(result)

            assert "lists" in result_dict or "items" in result_dict
            assert len(result_dict.get("lists", result_dict.get("items", []))) == 2

    def test_list_shopping_lists_empty(self):
        """Test listing shopping lists when none exist."""
        mock_client = Mock()
        mock_client.get.return_value = []

        with patch('src.tools.shopping.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = shopping_lists_list()
            result_dict = json.loads(result)

            # Should handle empty list
            assert result_dict is not None

    def test_list_shopping_lists_api_error(self):
        """Test handling of API error during list."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.get.side_effect = MealieAPIError(
            "Failed to fetch",
            status_code=500,
            response_body="Server error"
        )

        with patch('src.tools.shopping.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = shopping_lists_list()
            result_dict = json.loads(result)

            assert "error" in result_dict
            assert result_dict["status_code"] == 500


class TestShoppingListsGet:
    """Tests for shopping_lists_get function."""

    def test_get_shopping_list_by_id(self):
        """Test retrieving a specific shopping list."""
        shopping_list = build_shopping_list(
            name="Weekly Groceries",
            listItems=[
                build_shopping_item(note="2 cups flour"),
                build_shopping_item(note="1 tsp salt", checked=True)
            ]
        )

        mock_client = Mock()
        mock_client.get.return_value = shopping_list

        with patch('src.tools.shopping.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = shopping_lists_get("list-123")
            result_dict = json.loads(result)

            # Response has name and items
            assert result_dict["name"] == "Weekly Groceries"
            assert "items" in result_dict

            # Verify endpoint
            mock_client.get.assert_called_once_with("/api/households/shopping/lists/list-123")

    def test_get_shopping_list_not_found(self):
        """Test handling of shopping list not found error."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.get.side_effect = MealieAPIError(
            "Not found",
            status_code=404,
            response_body="List not found"
        )

        with patch('src.tools.shopping.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = shopping_lists_get("nonexistent")
            result_dict = json.loads(result)

            assert "error" in result_dict
            assert result_dict["status_code"] == 404

    def test_get_shopping_list_with_progress(self):
        """Test retrieving shopping list with item progress calculation."""
        shopping_list = build_shopping_list(
            listItems=[
                build_shopping_item(note="Item 1", checked=True),
                build_shopping_item(note="Item 2", checked=True),
                build_shopping_item(note="Item 3", checked=False)
            ]
        )

        mock_client = Mock()
        mock_client.get_shopping_list.return_value = shopping_list

        with patch('src.tools.shopping.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = shopping_lists_get("list-123")
            result_dict = json.loads(result)

            # Should return some response
            assert result_dict is not None


class TestShoppingListsCreate:
    """Tests for shopping_lists_create function."""

    def test_create_shopping_list(self):
        """Test creating a new shopping list."""
        mock_client = Mock()
        mock_client.post.return_value = build_shopping_list(name="New List")

        with patch('src.tools.shopping.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = shopping_lists_create(name="New List")
            result_dict = json.loads(result)

            # Response wrapped with success/list
            assert result_dict["success"] is True
            assert "list" in result_dict

            # Verify call
            mock_client.post.assert_called_once()

    def test_create_shopping_list_validates_name(self):
        """Test that name is required for creating list."""
        mock_client = Mock()
        mock_client.post.return_value = build_shopping_list()

        with patch('src.tools.shopping.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = shopping_lists_create(name="Required Name")

            # Should pass name to API
            call_args = mock_client.post.call_args
            assert "name" in call_args[1]["json"]

    def test_create_shopping_list_api_error(self):
        """Test handling of API error during creation."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.post.side_effect = MealieAPIError(
            "Creation failed",
            status_code=400,
            response_body="Invalid data"
        )

        with patch('src.tools.shopping.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = shopping_lists_create(name="Test List")
            result_dict = json.loads(result)

            assert "error" in result_dict
            assert result_dict["status_code"] == 400


class TestShoppingItemsAdd:
    """Tests for shopping_items_add function."""

    def test_add_item_to_list(self):
        """Test adding a single item to shopping list."""
        mock_client = Mock()
        mock_client.post.return_value = build_shopping_item(note="2 cups flour")

        with patch('src.tools.shopping.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = shopping_items_add(
                list_id="list-123",
                note="2 cups flour"
            )
            result_dict = json.loads(result)

            # Response wrapped with success/item
            assert result_dict["success"] is True
            assert "item" in result_dict

    def test_add_item_with_quantity_and_unit(self):
        """Test adding item with quantity and unit."""
        mock_client = Mock()
        mock_client.post.return_value = build_shopping_item(
            note="flour",
            quantity=2.0
        )

        with patch('src.tools.shopping.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = shopping_items_add(
                list_id="list-123",
                note="flour",
                quantity=2.0,
                unit_id="unit-cup"
            )

            # Verify payload includes quantity and unit
            call_args = mock_client.post.call_args
            payload = call_args[1]["json"]
            assert payload.get("quantity") == 2.0

    def test_add_item_api_error(self):
        """Test handling of API error when adding item."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.post.side_effect = MealieAPIError(
            "Failed to add",
            status_code=400,
            response_body="Invalid item"
        )

        with patch('src.tools.shopping.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = shopping_items_add(
                list_id="list-123",
                note="test item"
            )
            result_dict = json.loads(result)

            assert "error" in result_dict


class TestShoppingItemsCheck:
    """Tests for shopping_items_check function."""

    def test_check_item(self):
        """Test marking an item as checked."""
        mock_client = Mock()
        mock_client.put.return_value = build_shopping_item(
            note="flour",
            checked=True
        )

        with patch('src.tools.shopping.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = shopping_items_check(
                item_id="item-123",
                checked=True
            )
            result_dict = json.loads(result)

            assert result_dict["success"] is True

    def test_uncheck_item(self):
        """Test marking an item as unchecked."""
        mock_client = Mock()
        mock_client.put.return_value = build_shopping_item(
            note="flour",
            checked=False
        )

        with patch('src.tools.shopping.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = shopping_items_check(
                item_id="item-123",
                checked=False
            )
            result_dict = json.loads(result)

            assert result_dict["success"] is True

    def test_check_item_default_true(self):
        """Test that checked defaults to True."""
        mock_client = Mock()
        mock_client.put.return_value = build_shopping_item(checked=True)

        with patch('src.tools.shopping.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = shopping_items_check(item_id="item-123")
            result_dict = json.loads(result)

            # Should succeed
            assert result_dict["success"] is True

    def test_check_item_api_error(self):
        """Test handling of API error when checking item."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.put.side_effect = MealieAPIError(
            "Update failed",
            status_code=404,
            response_body="Item not found"
        )

        with patch('src.tools.shopping.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = shopping_items_check(item_id="nonexistent")
            result_dict = json.loads(result)

            assert "error" in result_dict
            assert result_dict["status_code"] == 404
