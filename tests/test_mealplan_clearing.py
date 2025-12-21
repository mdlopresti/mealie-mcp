"""
Tests for meal plan field clearing using sentinel value.

These tests verify that the CLEAR_FIELD sentinel ("__CLEAR__") allows users
to clear optional fields (recipe_id, title, text) from meal plan entries.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.mealplans import CLEAR_FIELD, mealplans_update


class TestMealplanClearing:
    """Test suite for clearing meal plan fields with sentinel value."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock MealieClient for testing."""
        with patch("tools.mealplans.MealieClient") as mock:
            client_instance = MagicMock()
            mock.return_value.__enter__.return_value = client_instance
            yield client_instance

    def test_clear_recipe_id(self, mock_client):
        """Test clearing recipe_id with sentinel value."""
        # Setup: existing entry with recipe
        existing_entry = {
            "id": "test-123",
            "date": "2025-12-21",
            "entryType": "dinner",
            "recipeId": "recipe-abc",
            "title": "Test Meal",
            "text": "Some notes"
        }
        mock_client.get.return_value = existing_entry
        mock_client.put.return_value = {**existing_entry, "recipeId": None}

        # Execute: clear recipe_id
        result = mealplans_update(
            mealplan_id="test-123",
            recipe_id=CLEAR_FIELD
        )

        # Verify: API received null for recipeId
        mock_client.put.assert_called_once()
        call_args = mock_client.put.call_args
        payload = call_args.kwargs["json"]

        assert payload["recipeId"] is None, "recipeId should be None (cleared)"
        assert payload["title"] == "Test Meal", "title should be preserved"
        assert payload["text"] == "Some notes", "text should be preserved"

        # Verify success response
        result_data = json.loads(result)
        assert result_data["success"] is True

    def test_clear_title(self, mock_client):
        """Test clearing title with sentinel value."""
        # Setup: existing entry with title
        existing_entry = {
            "id": "test-456",
            "date": "2025-12-21",
            "entryType": "lunch",
            "recipeId": "recipe-xyz",
            "title": "Custom Title",
            "text": "Important notes"
        }
        mock_client.get.return_value = existing_entry
        mock_client.put.return_value = {**existing_entry, "title": None}

        # Execute: clear title
        result = mealplans_update(
            mealplan_id="test-456",
            title=CLEAR_FIELD
        )

        # Verify: API received null for title
        mock_client.put.assert_called_once()
        call_args = mock_client.put.call_args
        payload = call_args.kwargs["json"]

        assert payload["title"] is None, "title should be None (cleared)"
        assert payload["recipeId"] == "recipe-xyz", "recipeId should be preserved"
        assert payload["text"] == "Important notes", "text should be preserved"

        # Verify success response
        result_data = json.loads(result)
        assert result_data["success"] is True

    def test_clear_text(self, mock_client):
        """Test clearing text with sentinel value."""
        # Setup: existing entry with text
        existing_entry = {
            "id": "test-789",
            "date": "2025-12-21",
            "entryType": "breakfast",
            "recipeId": "recipe-123",
            "title": "Morning Meal",
            "text": "Old notes to remove"
        }
        mock_client.get.return_value = existing_entry
        mock_client.put.return_value = {**existing_entry, "text": None}

        # Execute: clear text
        result = mealplans_update(
            mealplan_id="test-789",
            text=CLEAR_FIELD
        )

        # Verify: API received null for text
        mock_client.put.assert_called_once()
        call_args = mock_client.put.call_args
        payload = call_args.kwargs["json"]

        assert payload["text"] is None, "text should be None (cleared)"
        assert payload["recipeId"] == "recipe-123", "recipeId should be preserved"
        assert payload["title"] == "Morning Meal", "title should be preserved"

        # Verify success response
        result_data = json.loads(result)
        assert result_data["success"] is True

    def test_clear_multiple_fields(self, mock_client):
        """Test clearing multiple fields at once."""
        # Setup: existing entry with all fields
        existing_entry = {
            "id": "test-multi",
            "date": "2025-12-21",
            "entryType": "dinner",
            "recipeId": "recipe-abc",
            "title": "Custom Title",
            "text": "Some notes"
        }
        mock_client.get.return_value = existing_entry
        mock_client.put.return_value = {
            **existing_entry,
            "recipeId": None,
            "title": None,
            "text": None
        }

        # Execute: clear all three fields
        result = mealplans_update(
            mealplan_id="test-multi",
            recipe_id=CLEAR_FIELD,
            title=CLEAR_FIELD,
            text=CLEAR_FIELD
        )

        # Verify: API received null for all fields
        mock_client.put.assert_called_once()
        call_args = mock_client.put.call_args
        payload = call_args.kwargs["json"]

        assert payload["recipeId"] is None, "recipeId should be None"
        assert payload["title"] is None, "title should be None"
        assert payload["text"] is None, "text should be None"

        # Verify success response
        result_data = json.loads(result)
        assert result_data["success"] is True

    def test_omit_field_preserves_value(self, mock_client):
        """Test that omitting a field preserves its existing value (backward compatibility)."""
        # Setup: existing entry
        existing_entry = {
            "id": "test-preserve",
            "date": "2025-12-21",
            "entryType": "lunch",
            "recipeId": "recipe-preserve",
            "title": "Preserve This",
            "text": "Keep these notes"
        }
        mock_client.get.return_value = existing_entry
        mock_client.put.return_value = existing_entry

        # Execute: update only date (omit other fields)
        result = mealplans_update(
            mealplan_id="test-preserve",
            meal_date="2025-12-22"
        )

        # Verify: all original values preserved
        mock_client.put.assert_called_once()
        call_args = mock_client.put.call_args
        payload = call_args.kwargs["json"]

        assert payload["date"] == "2025-12-22", "date should be updated"
        assert payload["recipeId"] == "recipe-preserve", "recipeId should be preserved"
        assert payload["title"] == "Preserve This", "title should be preserved"
        assert payload["text"] == "Keep these notes", "text should be preserved"

    def test_set_new_value_still_works(self, mock_client):
        """Test that setting new values still works as expected."""
        # Setup: existing entry
        existing_entry = {
            "id": "test-new-value",
            "date": "2025-12-21",
            "entryType": "dinner",
            "recipeId": None,
            "title": None,
            "text": None
        }
        mock_client.get.return_value = existing_entry
        mock_client.put.return_value = {
            **existing_entry,
            "recipeId": "new-recipe",
            "title": "New Title",
            "text": "New notes"
        }

        # Execute: set new values
        result = mealplans_update(
            mealplan_id="test-new-value",
            recipe_id="new-recipe",
            title="New Title",
            text="New notes"
        )

        # Verify: new values set
        mock_client.put.assert_called_once()
        call_args = mock_client.put.call_args
        payload = call_args.kwargs["json"]

        assert payload["recipeId"] == "new-recipe", "recipeId should be set"
        assert payload["title"] == "New Title", "title should be set"
        assert payload["text"] == "New notes", "text should be set"

    def test_clear_then_set_workflow(self, mock_client):
        """Test realistic workflow: clear recipe, set new title."""
        # Setup: existing entry with recipe but custom title
        existing_entry = {
            "id": "test-workflow",
            "date": "2025-12-21",
            "entryType": "dinner",
            "recipeId": "old-recipe",
            "title": "Old Title",
            "text": "Keep notes"
        }
        mock_client.get.return_value = existing_entry
        mock_client.put.return_value = {
            **existing_entry,
            "recipeId": None,
            "title": "New Custom Title"
        }

        # Execute: clear recipe, set new title, preserve text
        result = mealplans_update(
            mealplan_id="test-workflow",
            recipe_id=CLEAR_FIELD,
            title="New Custom Title"
        )

        # Verify: recipe cleared, title changed, text preserved
        mock_client.put.assert_called_once()
        call_args = mock_client.put.call_args
        payload = call_args.kwargs["json"]

        assert payload["recipeId"] is None, "recipeId should be cleared"
        assert payload["title"] == "New Custom Title", "title should be updated"
        assert payload["text"] == "Keep notes", "text should be preserved"

    def test_sentinel_constant_value(self):
        """Test that CLEAR_FIELD has the expected value."""
        assert CLEAR_FIELD == "__CLEAR__", "Sentinel value should be '__CLEAR__'"

    def test_entry_not_found_error(self, mock_client):
        """Test error handling when entry doesn't exist."""
        # Setup: entry not found
        mock_client.get.return_value = None

        # Execute: try to update non-existent entry
        result = mealplans_update(
            mealplan_id="non-existent",
            title=CLEAR_FIELD
        )

        # Verify: error response
        result_data = json.loads(result)
        assert "error" in result_data
        assert "not found" in result_data["error"].lower()

    def test_preserve_entry_with_no_optional_fields(self, mock_client):
        """Test updating entry that has no optional fields set."""
        # Setup: minimal entry (no recipe, title, or text)
        existing_entry = {
            "id": "test-minimal",
            "date": "2025-12-21",
            "entryType": "snack"
        }
        mock_client.get.return_value = existing_entry
        mock_client.put.return_value = existing_entry

        # Execute: change entry type (omit other fields)
        result = mealplans_update(
            mealplan_id="test-minimal",
            entry_type="breakfast"
        )

        # Verify: only entry type changed, no unexpected fields added
        mock_client.put.assert_called_once()
        call_args = mock_client.put.call_args
        payload = call_args.kwargs["json"]

        assert payload["entryType"] == "breakfast", "entryType should be updated"
        # Should not add recipeId, title, or text if they weren't in original
        assert "recipeId" not in payload or payload.get("recipeId") is None
        assert "title" not in payload or payload.get("title") is None
        assert "text" not in payload or payload.get("text") is None
