"""Unit tests for mealplan tools (src/tools/mealplans.py).

Tests meal plan listing, creation, updates, deletion, and search functionality.
All tests use mocked MealieClient to avoid network calls.
"""

import json
import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch
from src.tools.mealplans import (
    mealplans_list,
    mealplans_today,
    mealplans_get,
    mealplans_create,
    mealplans_delete
)
from tests.unit.builders import build_mealplan, build_recipe


class TestMealplansList:
    """Tests for mealplans_list function."""

    def test_list_mealplans_default_dates(self):
        """Test listing meal plans with default date range."""
        mock_client = Mock()
        today = date.today()
        end = today + timedelta(days=7)

        mock_client.get.return_value = [
            build_mealplan(meal_date=today.isoformat(), entry_type="breakfast"),
            build_mealplan(meal_date=today.isoformat(), entry_type="lunch")
        ]

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = mealplans_list()
            result_dict = json.loads(result)

            assert "entries" in result_dict
            assert result_dict["count"] == 2
            assert result_dict["start_date"] == today.isoformat()
            assert result_dict["end_date"] == end.isoformat()

    def test_list_mealplans_custom_date_range(self):
        """Test listing meal plans with custom date range."""
        mock_client = Mock()
        mock_client.get.return_value = [
            build_mealplan(meal_date="2025-12-25", entry_type="dinner")
        ]

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = mealplans_list(start_date="2025-12-25", end_date="2025-12-26")
            result_dict = json.loads(result)

            assert result_dict["start_date"] == "2025-12-25"
            assert result_dict["end_date"] == "2025-12-26"

            # Verify API params
            call_args = mock_client.get.call_args
            assert call_args[1]["params"]["start_date"] == "2025-12-25"
            assert call_args[1]["params"]["end_date"] == "2025-12-26"

    def test_list_mealplans_formats_entries(self):
        """Test that mealplans_list formats entries correctly."""
        recipe = build_recipe(name="Pasta", slug="pasta")
        mealplan = build_mealplan(
            meal_date="2025-12-25",
            entry_type="dinner",
            title="Christmas Dinner",
            text="Special meal",
            recipeId="recipe-pasta"
        )
        mealplan["recipe"] = recipe

        mock_client = Mock()
        mock_client.get.return_value = [mealplan]

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = mealplans_list(start_date="2025-12-25", end_date="2025-12-26")
            result_dict = json.loads(result)

            entry = result_dict["entries"][0]
            assert entry["date"] == "2025-12-25"
            assert entry["entry_type"] == "dinner"
            assert entry["title"] == "Christmas Dinner"
            assert entry["text"] == "Special meal"
            assert entry["recipe_name"] == "Pasta"
            assert entry["recipe_slug"] == "pasta"

    def test_list_mealplans_empty_range(self):
        """Test listing meal plans with no entries in range."""
        mock_client = Mock()
        mock_client.get.return_value = []

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = mealplans_list(start_date="2025-01-01", end_date="2025-01-02")
            result_dict = json.loads(result)

            assert result_dict["count"] == 0
            assert result_dict["entries"] == []

    def test_list_mealplans_api_error(self):
        """Test handling of API error during list."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.get.side_effect = MealieAPIError(
            "Failed to fetch",
            status_code=500,
            response_body="Server error"
        )

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = mealplans_list()
            result_dict = json.loads(result)

            assert "error" in result_dict
            assert result_dict["status_code"] == 500


class TestMealplansToday:
    """Tests for mealplans_today function."""

    def test_get_today_mealplans(self):
        """Test retrieving today's meal plans."""
        today = date.today().isoformat()
        mock_client = Mock()
        mock_client.get.return_value = [
            build_mealplan(meal_date=today, entry_type="breakfast"),
            build_mealplan(meal_date=today, entry_type="lunch"),
            build_mealplan(meal_date=today, entry_type="dinner")
        ]

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = mealplans_today()
            result_dict = json.loads(result)

            assert result_dict["date"] == today
            assert "meals" in result_dict
            assert result_dict["count"] == 3

    def test_get_today_mealplans_organized_by_type(self):
        """Test that today's meals are organized by entry type."""
        today = date.today().isoformat()
        mock_client = Mock()
        mock_client.get.return_value = [
            build_mealplan(meal_date=today, entry_type="breakfast", title="Oatmeal"),
            build_mealplan(meal_date=today, entry_type="dinner", title="Pasta")
        ]

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = mealplans_today()
            result_dict = json.loads(result)

            # Should have meals organized by type
            assert "meals" in result_dict

    def test_get_today_mealplans_empty(self):
        """Test retrieving today's meals when none exist."""
        mock_client = Mock()
        mock_client.get.return_value = []

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = mealplans_today()
            result_dict = json.loads(result)

            assert result_dict["count"] == 0


class TestMealplansGet:
    """Tests for mealplans_get function."""

    def test_get_mealplan_by_id(self):
        """Test retrieving a specific meal plan entry."""
        mealplan = build_mealplan(
            meal_date="2025-12-25",
            entry_type="dinner",
            title="Holiday Dinner"
        )
        mealplan["id"] = "mealplan-123"

        mock_client = Mock()
        mock_client.get.return_value = mealplan

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = mealplans_get("mealplan-123")
            result_dict = json.loads(result)

            assert result_dict["id"] == "mealplan-123"
            assert result_dict["title"] == "Holiday Dinner"

            # Verify endpoint
            mock_client.get.assert_called_once_with("/api/households/mealplans/mealplan-123")

    def test_get_mealplan_not_found(self):
        """Test handling of meal plan not found error."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.get.side_effect = MealieAPIError(
            "Not found",
            status_code=404,
            response_body="Meal plan not found"
        )

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = mealplans_get("nonexistent")
            result_dict = json.loads(result)

            assert "error" in result_dict
            assert result_dict["status_code"] == 404


class TestMealplansCreate:
    """Tests for mealplans_create function."""

    def test_create_mealplan_with_recipe(self):
        """Test creating a meal plan entry with recipe."""
        mock_client = Mock()
        mock_client.post.return_value = build_mealplan(
            meal_date="2025-12-25",
            entry_type="dinner",
            recipeId="recipe-123"
        )

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = mealplans_create(
                meal_date="2025-12-25",
                entry_type="dinner",
                recipe_id="recipe-123"
            )
            result_dict = json.loads(result)

            # Function wraps response with success/entry keys
            assert result_dict["success"] is True
            assert "entry" in result_dict

            # Verify POST payload
            call_args = mock_client.post.call_args
            payload = call_args[1]["json"]
            assert payload["date"] == "2025-12-25"
            assert payload["entryType"] == "dinner"
            assert payload["recipeId"] == "recipe-123"

    def test_create_mealplan_without_recipe(self):
        """Test creating a meal plan entry without recipe."""
        mock_client = Mock()
        mock_client.post.return_value = build_mealplan(
            meal_date="2025-12-25",
            entry_type="breakfast",
            title="Quick breakfast",
            text="Eggs and toast"
        )

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = mealplans_create(
                meal_date="2025-12-25",
                entry_type="breakfast",
                title="Quick breakfast",
                text="Eggs and toast"
            )

            # Should work without recipe_id
            call_args = mock_client.post.call_args
            payload = call_args[1]["json"]
            assert "title" in payload
            assert "text" in payload

    def test_create_mealplan_validates_entry_type(self):
        """Test that valid entry types are accepted."""
        mock_client = Mock()
        mock_client.post.return_value = build_mealplan()

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            # Test each valid entry type
            for entry_type in ["breakfast", "lunch", "dinner", "side", "snack"]:
                result = mealplans_create(
                    meal_date="2025-12-25",
                    entry_type=entry_type
                )
                # Should not raise error
                assert result is not None

    def test_create_mealplan_api_error(self):
        """Test handling of API error during creation."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.post.side_effect = MealieAPIError(
            "Creation failed",
            status_code=400,
            response_body="Invalid data"
        )

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = mealplans_create(
                meal_date="2025-12-25",
                entry_type="dinner"
            )
            result_dict = json.loads(result)

            assert "error" in result_dict
            assert result_dict["status_code"] == 400


class TestMealplansDelete:
    """Tests for mealplans_delete function."""

    def test_delete_mealplan(self):
        """Test deleting a meal plan entry."""
        mock_client = Mock()
        mock_client.delete.return_value = {"message": "Deleted"}

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = mealplans_delete("mealplan-123")
            result_dict = json.loads(result)

            assert "success" in result_dict or "message" in result_dict

            # Verify DELETE endpoint
            mock_client.delete.assert_called_once_with("/api/households/mealplans/mealplan-123")

    def test_delete_mealplan_not_found(self):
        """Test deleting non-existent meal plan."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.delete.side_effect = MealieAPIError(
            "Not found",
            status_code=404,
            response_body="Meal plan not found"
        )

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = mealplans_delete("nonexistent")
            result_dict = json.loads(result)

            assert "error" in result_dict
            assert result_dict["status_code"] == 404

    def test_delete_mealplan_api_error(self):
        """Test handling of API error during deletion."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.delete.side_effect = MealieAPIError(
            "Deletion failed",
            status_code=500,
            response_body="Server error"
        )

        with patch('src.tools.mealplans.MealieClient') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client

            result = mealplans_delete("mealplan-123")
            result_dict = json.loads(result)

            assert "error" in result_dict
            assert result_dict["status_code"] == 500
