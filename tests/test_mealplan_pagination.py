"""
Tests for reading meal plans from Mealie's paginated date-range endpoint.

GET /api/households/mealplans returns a pagination envelope
({page, perPage, total, items}), not a bare list. These tests use that real
shape, which the older mocks did not.
"""

import json
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src.client import MealieAPIError, mealplan_entries, mealplan_range_params
from src.resources.mealplans import get_current_mealplan
from src.tools.mealplans import (
    mealplans_delete_range,
    mealplans_get_by_date,
    mealplans_list,
    mealplans_search,
    mealplans_today,
)
from src.tools.shopping import shopping_generate_from_mealplan


TODAY = date.today().isoformat()

DINNER = {
    "id": 11, "date": TODAY, "entryType": "dinner", "title": "", "text": "",
    "recipeId": "recipe-1",
    "recipe": {"id": "recipe-1", "name": "Pasta al pomodoro", "slug": "pasta-al-pomodoro"},
}
LUNCH_NOTE = {
    "id": 12, "date": TODAY, "entryType": "lunch", "title": "Leftovers", "text": "use the soup",
    "recipeId": None, "recipe": None,
}


def envelope(*items):
    return {"page": 1, "perPage": -1, "total": len(items), "totalPages": 1, "items": list(items)}


def mock_client(get_value):
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=None)
    mock.get.return_value = get_value
    return mock


class TestHelpers:

    def test_range_params_ask_for_every_page(self):
        assert mealplan_range_params("2026-10-01", "2026-10-07") == {
            "page": 1, "perPage": -1, "start_date": "2026-10-01", "end_date": "2026-10-07",
        }
        assert mealplan_range_params(None, None) == {"page": 1, "perPage": -1}

    def test_entries_unwrap_the_envelope(self):
        assert mealplan_entries(envelope(DINNER, LUNCH_NOTE)) == [DINNER, LUNCH_NOTE]

    def test_entries_accept_a_bare_list_and_ignore_junk(self):
        assert mealplan_entries([DINNER, "x", None]) == [DINNER]
        assert mealplan_entries(envelope()) == []

    @pytest.mark.parametrize("body", [None, {"detail": "proxy says no"}, {"items": None}, "ok"])
    def test_unexpected_body_is_an_error_not_an_empty_range(self, body):
        with pytest.raises(MealieAPIError, match="Unexpected response"):
            mealplan_entries(body)

    def test_get_by_date_reports_an_unexpected_body(self):
        mock = mock_client({"detail": "proxy says no"})
        with patch("src.tools.mealplans.MealieClient", return_value=mock):
            data = json.loads(mealplans_get_by_date(TODAY))

        assert "Unexpected response" in data["error"]
        assert "count" not in data


class TestGetByDate:

    def test_fields_come_from_the_entries_not_the_envelope(self):
        mock = mock_client(envelope(DINNER, LUNCH_NOTE))
        with patch("src.tools.mealplans.MealieClient", return_value=mock):
            data = json.loads(mealplans_get_by_date(TODAY))

        assert data["count"] == 2
        assert data["meals"]["dinner"] == [{
            "id": 11, "date": TODAY, "entry_type": "dinner", "title": "", "text": "",
            "recipe_id": "recipe-1", "recipe_name": "Pasta al pomodoro",
            "recipe_slug": "pasta-al-pomodoro",
        }]
        assert data["meals"]["lunch"][0]["title"] == "Leftovers"
        assert data["meals"]["lunch"][0]["recipe_id"] is None
        assert mock.get.call_args.kwargs["params"]["perPage"] == -1

    def test_empty_day_counts_zero(self):
        """An empty envelope used to be counted as one null meal."""
        mock = mock_client(envelope())
        with patch("src.tools.mealplans.MealieClient", return_value=mock):
            data = json.loads(mealplans_get_by_date(TODAY))

        assert data == {"date": TODAY, "count": 0, "meals": {}}


class TestGroupedItemsMatchList:
    """get_by_date and today group by meal type; each item still carries the list fields."""

    def test_flattened_items_equal_list_entries(self):
        mock = mock_client(envelope(DINNER, LUNCH_NOTE))
        with patch("src.tools.mealplans.MealieClient", return_value=mock):
            listed = json.loads(mealplans_list(start_date=TODAY, end_date=TODAY))["entries"]
            by_date = json.loads(mealplans_get_by_date(TODAY))["meals"]

        mock_today = mock_client([DINNER, LUNCH_NOTE])  # /today returns a bare list
        with patch("src.tools.mealplans.MealieClient", return_value=mock_today):
            today = json.loads(mealplans_today())["meals"]

        def flatten(grouped):
            return sorted((item for items in grouped.values() for item in items), key=lambda i: i["id"])

        assert flatten(by_date) == listed
        assert flatten(today) == listed

    def test_text_only_entry_keeps_null_recipe_fields(self):
        mock = mock_client(envelope(LUNCH_NOTE))
        with patch("src.tools.mealplans.MealieClient", return_value=mock):
            lunch = json.loads(mealplans_get_by_date(TODAY))["meals"]["lunch"][0]

        assert lunch["recipe_id"] is None
        assert lunch["recipe_name"] is None
        assert lunch["recipe_slug"] is None


class TestList:

    def test_envelope_is_formatted(self):
        mock = mock_client(envelope(DINNER))
        with patch("src.tools.mealplans.MealieClient", return_value=mock):
            data = json.loads(mealplans_list(start_date=TODAY, end_date=TODAY))

        assert data["count"] == 1
        assert data["entries"][0]["entry_type"] == "dinner"
        assert data["entries"][0]["recipe_name"] == "Pasta al pomodoro"
        assert mock.get.call_args.kwargs["params"] == mealplan_range_params(TODAY, TODAY)


class TestSearchAndDeleteRange:

    def test_search_reads_the_entries(self):
        mock = mock_client(envelope(DINNER, LUNCH_NOTE))
        with patch("src.tools.mealplans.MealieClient", return_value=mock):
            data = json.loads(mealplans_search("pomodoro", start_date=TODAY, end_date=TODAY))

        assert data["success"] is True
        assert [plan["id"] for plan in data["meal_plans"]] == [11]

    def test_delete_range_deletes_each_entry(self):
        mock = mock_client(envelope(DINNER, LUNCH_NOTE))
        with patch("src.tools.mealplans.MealieClient", return_value=mock):
            json.loads(mealplans_delete_range(start_date=TODAY, end_date=TODAY))

        deleted = [call.args[0] for call in mock.delete.call_args_list]
        assert deleted == ["/api/households/mealplans/11", "/api/households/mealplans/12"]


class TestOtherReaders:

    def test_current_week_resource_lists_the_meals(self):
        mock = mock_client(envelope(DINNER, LUNCH_NOTE))
        with patch("src.resources.mealplans.MealieClient", return_value=mock):
            text = get_current_mealplan()

        assert "Pasta al pomodoro" in text
        assert "- Leftovers" in text  # a title-only entry still shows up
        assert mock.get.call_args.kwargs["params"]["perPage"] == -1

    def test_shopping_from_mealplan_finds_the_recipes(self):
        mock = mock_client(envelope(DINNER, LUNCH_NOTE))
        mock.post.return_value = {"id": "list-1", "name": "Meal plan"}
        with patch("src.tools.shopping.MealieClient", return_value=mock):
            data = json.loads(shopping_generate_from_mealplan(start_date=TODAY, end_date=TODAY))

        assert data.get("success") is True, data
        assert mock.get.call_args_list[0].kwargs["params"]["perPage"] == -1
