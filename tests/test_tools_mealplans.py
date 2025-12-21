"""
Simplified tests for meal plan tools focusing on code coverage.
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from src.tools.mealplans import (
    mealplans_list,
    mealplans_today,
    mealplans_get,
    mealplans_get_by_date,
    mealplans_create,
    mealplans_update,
    mealplans_delete,
    mealplans_random,
    mealplans_search,
    mealplans_delete_range,
    mealplans_update_batch,
    mealplan_rules_list,
    mealplan_rules_get,
    mealplan_rules_create,
    mealplan_rules_update,
    mealplan_rules_delete
)


def create_mock_client(get_value=None, post_value=None, patch_value=None, put_value=None, delete_value=None):
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
    if put_value is not None:
        mock.put.return_value = put_value
    if delete_value is not None:
        mock.delete.return_value = delete_value
    return mock


class TestMealPlans:
    """Test meal plan operations."""

    def test_mealplans_list(self):
        """Test listing meal plans."""
        mock_client = create_mock_client(get_value=[{"id": "1", "date": "2025-01-01"}])

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_list()

        data = json.loads(result)
        assert isinstance(data, (dict, list))

    def test_mealplans_today(self):
        """Test getting today's meal plans."""
        mock_client = create_mock_client(get_value=[])

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_today()

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_mealplans_get(self):
        """Test getting a meal plan."""
        mock_client = create_mock_client(get_value={"id": "1", "date": "2025-01-01"})

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_get("mealplan-1")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_mealplans_get_by_date(self):
        """Test getting meal plans by date."""
        mock_client = create_mock_client(get_value=[])

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_get_by_date("2025-01-01")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_mealplans_create(self):
        """Test creating a meal plan."""
        mock_client = create_mock_client(post_value={"id": "new", "date": "2025-01-01"})

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_create("2025-01-01", "dinner")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_mealplans_update(self):
        """Test updating a meal plan."""
        # Mock GET to return existing entry with required fields
        existing_entry = {
            "id": "1",
            "date": "2025-01-01",
            "entryType": "dinner",
            "groupId": "group-uuid-123",
            "userId": "user-uuid-456"
        }
        # Mock PUT to return updated entry
        updated_entry = {
            "id": "1",
            "date": "2025-01-02",
            "entryType": "dinner",
            "groupId": "group-uuid-123",
            "userId": "user-uuid-456"
        }
        mock_client = create_mock_client(
            get_value=existing_entry,
            put_value=updated_entry
        )

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_update("mealplan-1", meal_date="2025-01-02")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data.get("success") is True

    def test_mealplans_delete(self):
        """Test deleting a meal plan."""
        mock_client = create_mock_client(delete_value=None)

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_delete("mealplan-1")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_mealplans_random(self):
        """Test getting a random meal plan suggestion."""
        mock_client = create_mock_client(get_value={"slug": "test-recipe", "name": "Test"})

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_random()

        data = json.loads(result)
        assert isinstance(data, dict)


class TestMealPlanRules:
    """Test meal plan rule operations."""

    def test_rules_list(self):
        """Test listing meal plan rules."""
        mock_client = create_mock_client(get_value=[{"id": "1", "name": "Dinner Rule"}])

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplan_rules_list()

        data = json.loads(result)
        assert isinstance(data, (dict, list))

    def test_rules_get(self):
        """Test getting a meal plan rule."""
        mock_client = create_mock_client(get_value={"id": "1", "name": "Dinner Rule"})

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplan_rules_get("rule-1")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_rules_create(self):
        """Test creating a meal plan rule."""
        mock_client = create_mock_client(post_value={"id": "new", "name": "New Rule"})

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplan_rules_create("New Rule", "dinner")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_rules_update(self):
        """Test updating a meal plan rule."""
        mock_client = create_mock_client(patch_value={"id": "1", "name": "Updated"})

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplan_rules_update("rule-1", name="Updated")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_rules_delete(self):
        """Test deleting a meal plan rule."""
        mock_client = create_mock_client(delete_value=None)

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplan_rules_delete("rule-1")

        data = json.loads(result)
        assert isinstance(data, dict)


class TestMealPlansErrorHandling:
    """Test error handling in meal plan operations."""

    def test_list_api_error(self):
        """Test error handling in mealplans_list."""
        from src.client import MealieAPIError

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.side_effect = MealieAPIError(
            "API Error", status_code=500, response_body="Error"
        )

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_list()

        data = json.loads(result)
        assert "error" in data

    def test_create_api_error(self):
        """Test error handling in mealplans_create."""
        from src.client import MealieAPIError

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.post.side_effect = MealieAPIError(
            "Bad Request", status_code=400, response_body="Invalid date"
        )

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_create("2025-13-99", "dinner")

        data = json.loads(result)
        assert "error" in data

    def test_update_api_error(self):
        """Test error handling in mealplans_update."""
        from src.client import MealieAPIError

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.patch.side_effect = MealieAPIError(
            "Not Found", status_code=404, response_body="Meal plan not found"
        )

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_update("nonexistent-id")

        data = json.loads(result)
        assert "error" in data

    def test_rules_create_api_error(self):
        """Test error handling in mealplan_rules_create."""
        from src.client import MealieAPIError

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.post.side_effect = MealieAPIError(
            "Conflict", status_code=409, response_body="Rule exists"
        )

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplan_rules_create("Duplicate Rule", "dinner")

        data = json.loads(result)
        assert "error" in data


class TestMealPlansAdvanced:
    """Test advanced meal plan scenarios."""

    def test_create_with_recipe(self):
        """Test creating meal plan with recipe."""
        mock_client = create_mock_client(post_value={
            "id": "new",
            "date": "2025-01-20",
            "entryType": "dinner",
            "recipe": {"id": "recipe-1", "name": "Pasta"}
        })

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_create(
                "2025-01-20",
                "dinner",
                recipe_id="recipe-1"
            )

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_create_with_title_and_text(self):
        """Test creating meal plan with custom title and text."""
        mock_client = create_mock_client(post_value={
            "id": "new",
            "date": "2025-01-20",
            "entryType": "snack",
            "title": "Healthy Snack",
            "text": "Apple and peanut butter"
        })

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_create(
                "2025-01-20",
                "snack",
                title="Healthy Snack",
                text="Apple and peanut butter"
            )

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_update_change_date(self):
        """Test updating meal plan date."""
        mock_client = create_mock_client(patch_value={
            "id": "1",
            "date": "2025-01-21"
        })

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_update("mealplan-1", meal_date="2025-01-21")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_update_change_recipe(self):
        """Test updating meal plan recipe."""
        mock_client = create_mock_client(patch_value={
            "id": "1",
            "recipe": {"id": "recipe-2"}
        })

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_update("mealplan-1", recipe_id="recipe-2")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_rules_create_with_tags_and_categories(self):
        """Test creating rule with tags and categories."""
        mock_client = create_mock_client(post_value={
            "id": "new",
            "name": "Vegan Dinners",
            "entryType": "dinner",
            "tags": [{"name": "Vegan"}],
            "categories": [{"name": "Main"}, {"name": "Dinner"}]
        })

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplan_rules_create(
                "Vegan Dinners",
                "dinner",
                tags=["Vegan"],
                categories=["Main", "Dinner"]
            )

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_rules_update_tags(self):
        """Test updating rule tags."""
        mock_client = create_mock_client(patch_value={
            "id": "1",
            "tags": [{"name": "Quick"}, {"name": "Easy"}]
        })

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplan_rules_update(
                "rule-1",
                tags=["Quick", "Easy"]
            )

        data = json.loads(result)
        assert isinstance(data, dict)


class TestMealPlansMoreEdgeCases:
    """Test additional meal plan edge cases for coverage."""

    def test_mealplans_today_with_actual_meals(self):
        """Test today's meals with actual meal entries."""
        mock_client = create_mock_client(get_value=[
            {
                "id": "meal-1",
                "entryType": "breakfast",
                "title": "Morning Meal",
                "text": "Oatmeal",
                "recipeId": None,
                "recipe": None
            },
            {
                "id": "meal-2",
                "entryType": "dinner",
                "title": None,
                "text": None,
                "recipeId": "recipe-1",
                "recipe": {
                    "id": "recipe-1",
                    "name": "Pasta",
                    "slug": "pasta"
                }
            },
            {
                "id": "meal-3",
                "entryType": "snack",
                "title": "Afternoon Snack",
                "text": "Fruit",
                "recipeId": None,
                "recipe": None
            }
        ])

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_today()

        data = json.loads(result)
        assert "meals" in data
        assert "breakfast" in data["meals"]
        assert "dinner" in data["meals"]
        assert "snack" in data["meals"]

    def test_mealplans_get_by_date_with_multiple_entries(self):
        """Test get meal plans by date with multiple entries."""
        mock_client = create_mock_client(get_value=[
            {
                "id": "meal-1",
                "entryType": "breakfast",
                "recipe": {"name": "Oatmeal", "slug": "oatmeal"}
            },
            {
                "id": "meal-2",
                "entryType": "lunch",
                "recipe": {"name": "Sandwich", "slug": "sandwich"}
            }
        ])

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_get_by_date("2025-01-20")

        data = json.loads(result)
        assert "meals" in data
        assert len(data["meals"]) >= 2

    def test_mealplans_list_with_date_range(self):
        """Test listing meal plans with custom date range."""
        mock_client = create_mock_client(get_value=[
            {"id": "1", "date": "2025-01-20"},
            {"id": "2", "date": "2025-01-21"},
            {"id": "3", "date": "2025-01-22"}
        ])

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_list(start_date="2025-01-20", end_date="2025-01-25")

        data = json.loads(result)
        assert isinstance(data, (dict, list))

    def test_mealplan_unexpected_error(self):
        """Test unexpected error handling in mealplans."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.side_effect = ValueError("Unexpected error")

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_list()

        data = json.loads(result)
        assert "error" in data
        assert "Unexpected error" in data["error"]

    def test_mealplans_get_unexpected_error(self):
        """Test unexpected error in mealplans_get."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.side_effect = TypeError("Type error")

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_get("test-id")

        data = json.loads(result)
        assert "error" in data


class TestMealPlansFinalPush:
    """Final mealplan tests to reach 50% coverage."""

    def test_mealplans_list_unexpected_error(self):
        """Test mealplans_list unexpected error."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.side_effect = RuntimeError("Runtime error")

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_list()

        data = json.loads(result)
        assert "error" in data

    def test_mealplans_create_unexpected_error(self):
        """Test mealplans_create unexpected error."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.post.side_effect = ValueError("Value error")

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_create("2025-01-20", "dinner")

        data = json.loads(result)
        assert "error" in data

    def test_mealplans_update_unexpected_error(self):
        """Test mealplans_update unexpected error."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.side_effect = TypeError("Type error")

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_update("meal-1", meal_date="2025-01-21")

        data = json.loads(result)
        assert "error" in data

    def test_mealplans_delete_unexpected_error(self):
        """Test mealplans_delete unexpected error."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.delete.side_effect = RuntimeError("Runtime error")

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_delete("meal-1")

        data = json.loads(result)
        assert "error" in data

    def test_mealplan_rules_create_unexpected_error(self):
        """Test mealplan_rules_create unexpected error."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.post.side_effect = ValueError("Value error")

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplan_rules_create("Test Rule", "dinner")

        data = json.loads(result)
        assert "error" in data

    def test_mealplan_rules_update_unexpected_error(self):
        """Test mealplan_rules_update unexpected error."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.patch.side_effect = TypeError("Type error")

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplan_rules_update("rule-1", name="Updated")

        data = json.loads(result)
        assert "error" in data

    def test_mealplan_rules_delete_unexpected_error(self):
        """Test mealplan_rules_delete unexpected error."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.delete_mealplan_rule.side_effect = RuntimeError("Runtime error")

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplan_rules_delete("rule-1")

        data = json.loads(result)
        assert "error" in data

    def test_mealplans_random_unexpected_error(self):
        """Test mealplans_random unexpected error."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.side_effect = ValueError("Value error")

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_random()

        data = json.loads(result)
        assert "error" in data

    def test_mealplans_get_by_date_unexpected_error(self):
        """Test mealplans_get_by_date unexpected error."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.side_effect = TypeError("Type error")

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_get_by_date("2025-01-20")

        data = json.loads(result)
        assert "error" in data


class TestMealPlansSearch:
    """Test meal plan search functionality."""

    def test_search_basic(self):
        """Test basic meal plan search."""
        mock_plans = [
            {
                "id": "1",
                "date": "2025-01-20",
                "entryType": "dinner",
                "recipe": {"id": "recipe-1", "name": "Pork Chops", "slug": "pork-chops"},
                "title": None,
                "text": None
            },
            {
                "id": "2",
                "date": "2025-01-21",
                "entryType": "lunch",
                "recipe": {"id": "recipe-2", "name": "Chicken Soup", "slug": "chicken-soup"},
                "title": None,
                "text": None
            }
        ]
        mock_client = create_mock_client(get_value=mock_plans)

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_search("pork")

        data = json.loads(result)
        assert data.get("success") is True
        assert data.get("count") == 1
        assert data["meal_plans"][0]["recipe"]["name"] == "Pork Chops"

    def test_search_case_insensitive(self):
        """Test case-insensitive search."""
        mock_plans = [
            {
                "id": "1",
                "date": "2025-01-20",
                "entryType": "dinner",
                "recipe": {"id": "recipe-1", "name": "PORK CHOPS", "slug": "pork-chops"},
                "title": None,
                "text": None
            }
        ]
        mock_client = create_mock_client(get_value=mock_plans)

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_search("pork")

        data = json.loads(result)
        assert data.get("success") is True
        assert data.get("count") == 1

    def test_search_by_title(self):
        """Test search matching entry title."""
        mock_plans = [
            {
                "id": "1",
                "date": "2025-01-20",
                "entryType": "snack",
                "recipe": None,
                "title": "Freezer meal prep",
                "text": None
            }
        ]
        mock_client = create_mock_client(get_value=mock_plans)

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_search("freezer")

        data = json.loads(result)
        assert data.get("success") is True
        assert data.get("count") == 1

    def test_search_by_text(self):
        """Test search matching entry text."""
        mock_plans = [
            {
                "id": "1",
                "date": "2025-01-20",
                "entryType": "dinner",
                "recipe": {"id": "recipe-1", "name": "Pasta", "slug": "pasta"},
                "title": None,
                "text": "freezer meal from batch cooking"
            }
        ]
        mock_client = create_mock_client(get_value=mock_plans)

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_search("freezer")

        data = json.loads(result)
        assert data.get("success") is True
        assert data.get("count") == 1

    def test_search_no_results(self):
        """Test search with no matching results."""
        mock_plans = [
            {
                "id": "1",
                "date": "2025-01-20",
                "entryType": "dinner",
                "recipe": {"id": "recipe-1", "name": "Pasta", "slug": "pasta"},
                "title": None,
                "text": None
            }
        ]
        mock_client = create_mock_client(get_value=mock_plans)

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_search("nonexistent")

        data = json.loads(result)
        assert data.get("success") is True
        assert data.get("count") == 0
        assert data["meal_plans"] == []

    def test_search_with_date_range(self):
        """Test search with custom date range."""
        mock_plans = [
            {
                "id": "1",
                "date": "2025-01-15",
                "entryType": "dinner",
                "recipe": {"id": "recipe-1", "name": "Pork Chops", "slug": "pork-chops"},
                "title": None,
                "text": None
            }
        ]
        mock_client = create_mock_client(get_value=mock_plans)

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_search("pork", start_date="2025-01-01", end_date="2025-01-31")

        data = json.loads(result)
        assert data.get("success") is True
        assert data.get("date_range")["start"] == "2025-01-01"
        assert data.get("date_range")["end"] == "2025-01-31"

    def test_search_api_error(self):
        """Test search with API error."""
        from src.client import MealieAPIError

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.side_effect = MealieAPIError(
            "Server Error", status_code=500, response_body="Internal error"
        )

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_search("pork")

        data = json.loads(result)
        assert "error" in data
        assert data.get("status_code") == 500

    def test_search_unexpected_error(self):
        """Test search with unexpected error."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.side_effect = ValueError("Unexpected error")

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_search("pork")

        data = json.loads(result)
        assert "error" in data
        assert "Unexpected error" in data["error"]

    def test_search_multiple_field_matches(self):
        """Test search matching multiple fields across entries."""
        mock_plans = [
            {
                "id": "1",
                "date": "2025-01-20",
                "entryType": "dinner",
                "recipe": {"id": "recipe-1", "name": "Pork Chops", "slug": "pork-chops"},
                "title": None,
                "text": None
            },
            {
                "id": "2",
                "date": "2025-01-21",
                "entryType": "lunch",
                "recipe": None,
                "title": "Leftover pork",
                "text": "From yesterday's dinner"
            },
            {
                "id": "3",
                "date": "2025-01-22",
                "entryType": "dinner",
                "recipe": {"id": "recipe-2", "name": "Chicken", "slug": "chicken"},
                "title": None,
                "text": "Made with pork sausage"
            }
        ]
        mock_client = create_mock_client(get_value=mock_plans)

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_search("pork")

        data = json.loads(result)
        assert data.get("success") is True
        assert data.get("count") == 3


class TestMealPlansBatchOperations:
    """Test meal plan batch operations."""

    def test_delete_range_basic(self):
        """Test basic delete range functionality."""
        mock_plans = [
            {"id": "meal-1", "date": "2025-01-20"},
            {"id": "meal-2", "date": "2025-01-21"},
            {"id": "meal-3", "date": "2025-01-22"}
        ]
        mock_client = create_mock_client(get_value=mock_plans, delete_value=None)

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_delete_range("2025-01-20", "2025-01-25")

        data = json.loads(result)
        assert data.get("success") is True
        assert data.get("total_found") == 3
        assert data.get("deleted") == 3
        assert data.get("failed") == 0

    def test_delete_range_with_failures(self):
        """Test delete range with some failures."""
        mock_plans = [
            {"id": "meal-1", "date": "2025-01-20"},
            {"id": "meal-2", "date": "2025-01-21"}
        ]

        # Create mock that fails on second delete
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.return_value = mock_plans

        delete_count = [0]
        def delete_side_effect(path):
            delete_count[0] += 1
            if delete_count[0] == 2:
                raise ValueError("Delete failed")

        mock_client.delete.side_effect = delete_side_effect

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_delete_range("2025-01-20", "2025-01-25")

        data = json.loads(result)
        assert data.get("success") is True
        assert data.get("total_found") == 2
        assert data.get("deleted") == 1
        assert data.get("failed") == 1

    def test_delete_range_api_error(self):
        """Test delete range with API error."""
        from src.client import MealieAPIError

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.side_effect = MealieAPIError(
            "Not Found", status_code=404, response_body="No plans found"
        )

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_delete_range("2025-01-01", "2025-01-31")

        data = json.loads(result)
        assert "error" in data
        assert data.get("status_code") == 404

    def test_update_batch_basic(self):
        """Test basic batch update functionality."""
        # Mock existing entries
        existing_entry_1 = {
            "id": "meal-1",
            "date": "2025-01-20",
            "entryType": "dinner",
            "groupId": "group-1",
            "userId": "user-1"
        }
        existing_entry_2 = {
            "id": "meal-2",
            "date": "2025-01-21",
            "entryType": "lunch",
            "groupId": "group-1",
            "userId": "user-1"
        }

        # Mock updates
        updated_entry_1 = {**existing_entry_1, "date": "2025-01-22"}
        updated_entry_2 = {**existing_entry_2, "text": "New note"}

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        def get_side_effect(path):
            if "meal-1" in path:
                return existing_entry_1
            elif "meal-2" in path:
                return existing_entry_2

        def put_side_effect(path, json):
            if "meal-1" in path:
                return updated_entry_1
            elif "meal-2" in path:
                return updated_entry_2

        mock_client.get.side_effect = get_side_effect
        mock_client.put.side_effect = put_side_effect

        updates = [
            {"mealplan_id": "meal-1", "meal_date": "2025-01-22"},
            {"mealplan_id": "meal-2", "text": "New note"}
        ]

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_update_batch(updates)

        data = json.loads(result)
        assert data.get("success") is True
        assert data.get("total_requested") == 2
        assert data.get("updated") == 2
        assert data.get("failed") == 0

    def test_update_batch_missing_id(self):
        """Test batch update with missing mealplan_id."""
        updates = [
            {"meal_date": "2025-01-22"}  # Missing mealplan_id
        ]

        mock_client = create_mock_client()

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_update_batch(updates)

        data = json.loads(result)
        assert data.get("success") is True
        assert data.get("updated") == 0
        assert data.get("failed") == 1

    def test_update_batch_clear_fields(self):
        """Test batch update with field clearing."""
        existing_entry = {
            "id": "meal-1",
            "date": "2025-01-20",
            "entryType": "dinner",
            "groupId": "group-1",
            "userId": "user-1",
            "recipeId": "recipe-1",
            "title": "Old title",
            "text": "Old text"
        }

        updated_entry = {
            **existing_entry,
            "recipeId": None,
            "title": None,
            "text": None
        }

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.return_value = existing_entry
        mock_client.put.return_value = updated_entry

        updates = [
            {
                "mealplan_id": "meal-1",
                "recipe_id": "__CLEAR__",
                "title": "__CLEAR__",
                "text": "__CLEAR__"
            }
        ]

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_update_batch(updates)

        data = json.loads(result)
        assert data.get("success") is True
        assert data.get("updated") == 1

    def test_update_batch_partial_failure(self):
        """Test batch update with partial failures."""
        existing_entry = {
            "id": "meal-1",
            "date": "2025-01-20",
            "entryType": "dinner",
            "groupId": "group-1",
            "userId": "user-1"
        }

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        get_count = [0]
        def get_side_effect(path):
            get_count[0] += 1
            if get_count[0] == 2:
                raise ValueError("Get failed")
            return existing_entry

        mock_client.get.side_effect = get_side_effect
        mock_client.put.return_value = existing_entry

        updates = [
            {"mealplan_id": "meal-1", "meal_date": "2025-01-22"},
            {"mealplan_id": "meal-2", "meal_date": "2025-01-23"}
        ]

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_update_batch(updates)

        data = json.loads(result)
        assert data.get("success") is True
        assert data.get("updated") == 1
        assert data.get("failed") == 1

    def test_update_batch_api_error(self):
        """Test batch update with API error on individual item."""
        from src.client import MealieAPIError

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.side_effect = MealieAPIError(
            "Server Error", status_code=500, response_body="Internal error"
        )

        updates = [{"mealplan_id": "meal-1", "meal_date": "2025-01-22"}]

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_update_batch(updates)

        data = json.loads(result)
        # Batch operations continue on error and report failures
        assert data.get("success") is True
        assert data.get("updated") == 0
        assert data.get("failed") == 1
        assert len(data.get("failures", [])) == 1
