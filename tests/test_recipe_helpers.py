"""
Unit tests for recipe helper functions.

Tests the _resolve_tags() and _resolve_categories() utility functions
that are used by both recipes_create() and recipes_update().
"""

import unittest
from unittest.mock import MagicMock, Mock
from src.tools.recipes import _resolve_tags, _resolve_categories


class TestResolveTags(unittest.TestCase):
    """Test cases for _resolve_tags() utility function."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = MagicMock()
        self.group_id = "test-group-123"

    def test_resolve_existing_tags_replace_mode(self):
        """Test resolving existing tags in REPLACE mode."""
        # Mock list_tags to return existing tags
        self.client.list_tags.return_value = {
            "items": [
                {"id": "tag-1", "name": "vegan", "slug": "vegan"},
                {"id": "tag-2", "name": "quick", "slug": "quick"},
            ]
        }

        result = _resolve_tags(self.client, ["vegan", "quick"], self.group_id)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "tag-1")
        self.assertEqual(result[0]["name"], "vegan")
        self.assertEqual(result[1]["id"], "tag-2")
        self.assertEqual(result[1]["name"], "quick")
        self.client.list_tags.assert_called_once()
        self.client.create_tag.assert_not_called()

    def test_resolve_new_tags(self):
        """Test resolving new tags (creates them)."""
        # Mock list_tags to return no matching tags
        self.client.list_tags.return_value = {
            "items": [
                {"id": "tag-1", "name": "existing", "slug": "existing"},
            ]
        }

        # Mock create_tag to return new tag objects
        self.client.create_tag.side_effect = [
            {"id": "tag-new-1", "name": "new-tag-1", "slug": "new-tag-1"},
            {"id": "tag-new-2", "name": "new-tag-2", "slug": "new-tag-2"},
        ]

        result = _resolve_tags(self.client, ["new-tag-1", "new-tag-2"], self.group_id)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "tag-new-1")
        self.assertEqual(result[0]["name"], "new-tag-1")
        self.assertEqual(result[1]["id"], "tag-new-2")
        self.assertEqual(result[1]["name"], "new-tag-2")
        self.client.list_tags.assert_called_once()
        self.assertEqual(self.client.create_tag.call_count, 2)

    def test_resolve_mixed_existing_and_new_tags(self):
        """Test resolving a mix of existing and new tags."""
        # Mock list_tags to return one existing tag
        self.client.list_tags.return_value = {
            "items": [
                {"id": "tag-1", "name": "vegan", "slug": "vegan"},
            ]
        }

        # Mock create_tag for new tag
        self.client.create_tag.return_value = {
            "id": "tag-new", "name": "quick", "slug": "quick"
        }

        result = _resolve_tags(self.client, ["vegan", "quick"], self.group_id)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "tag-1")  # Existing
        self.assertEqual(result[0]["name"], "vegan")
        self.assertEqual(result[1]["id"], "tag-new")  # New
        self.assertEqual(result[1]["name"], "quick")
        self.client.list_tags.assert_called_once()
        self.client.create_tag.assert_called_once_with("quick")

    def test_additive_mode_preserves_existing_tags(self):
        """Test ADDITIVE mode preserves existing tags on recipe."""
        # Existing tags on the recipe
        existing_tags = [
            {"id": "tag-1", "name": "breakfast", "slug": "breakfast"},
            {"id": "tag-2", "name": "quick", "slug": "quick"},
        ]

        # Mock list_tags to return system tags
        self.client.list_tags.return_value = {
            "items": [
                {"id": "tag-1", "name": "breakfast", "slug": "breakfast"},
                {"id": "tag-2", "name": "quick", "slug": "quick"},
                {"id": "tag-3", "name": "healthy", "slug": "healthy"},
            ]
        }

        # Add "healthy" to existing tags
        result = _resolve_tags(
            self.client,
            ["healthy"],
            self.group_id,
            existing_tags=existing_tags
        )

        self.assertEqual(len(result), 3)
        # First two should be the existing tags (preserved)
        self.assertEqual(result[0]["id"], "tag-1")
        self.assertEqual(result[1]["id"], "tag-2")
        # Third should be the newly added tag
        self.assertEqual(result[2]["id"], "tag-3")
        self.assertEqual(result[2]["name"], "healthy")
        self.client.create_tag.assert_not_called()

    def test_additive_mode_skips_duplicates(self):
        """Test ADDITIVE mode doesn't add duplicate tags."""
        # Existing tags on the recipe
        existing_tags = [
            {"id": "tag-1", "name": "vegan", "slug": "vegan"},
        ]

        # Mock list_tags
        self.client.list_tags.return_value = {
            "items": [
                {"id": "tag-1", "name": "vegan", "slug": "vegan"},
            ]
        }

        # Try to add "vegan" again
        result = _resolve_tags(
            self.client,
            ["vegan"],
            self.group_id,
            existing_tags=existing_tags
        )

        # Should still have only 1 tag (no duplicate)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "tag-1")
        self.client.create_tag.assert_not_called()

    def test_empty_tag_list(self):
        """Test handling empty tag list."""
        self.client.list_tags.return_value = {"items": []}

        result = _resolve_tags(self.client, [], self.group_id)

        self.assertEqual(len(result), 0)
        self.client.list_tags.assert_called_once()
        self.client.create_tag.assert_not_called()

    def test_handles_paginated_response(self):
        """Test handling paginated list_tags() response."""
        # Mock list_tags to return paginated response (dict with "items")
        self.client.list_tags.return_value = {
            "items": [
                {"id": "tag-1", "name": "vegan", "slug": "vegan"},
            ],
            "page": 1,
            "totalPages": 1,
        }

        result = _resolve_tags(self.client, ["vegan"], self.group_id)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "tag-1")

    def test_handles_direct_list_response(self):
        """Test handling direct list response (not paginated)."""
        # Mock list_tags to return direct list
        self.client.list_tags.return_value = [
            {"id": "tag-1", "name": "vegan", "slug": "vegan"},
        ]

        result = _resolve_tags(self.client, ["vegan"], self.group_id)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "tag-1")

    def test_propagates_api_errors(self):
        """Test that API errors are propagated to caller."""
        from src.client import MealieAPIError

        # Mock list_tags to raise an error
        self.client.list_tags.side_effect = MealieAPIError(
            "API Error", 500, "Internal Server Error"
        )

        with self.assertRaises(MealieAPIError):
            _resolve_tags(self.client, ["vegan"], self.group_id)


class TestResolveCategories(unittest.TestCase):
    """Test cases for _resolve_categories() utility function."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = MagicMock()
        self.group_id = "test-group-123"

    def test_resolve_existing_categories_replace_mode(self):
        """Test resolving existing categories in REPLACE mode."""
        # Mock list_categories to return existing categories
        self.client.list_categories.return_value = {
            "items": [
                {"id": "cat-1", "name": "dinner", "slug": "dinner"},
                {"id": "cat-2", "name": "soup", "slug": "soup"},
            ]
        }

        result = _resolve_categories(self.client, ["dinner", "soup"], self.group_id)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "cat-1")
        self.assertEqual(result[0]["name"], "dinner")
        self.assertEqual(result[1]["id"], "cat-2")
        self.assertEqual(result[1]["name"], "soup")
        self.client.list_categories.assert_called_once()
        self.client.create_category.assert_not_called()

    def test_resolve_new_categories(self):
        """Test resolving new categories (creates them)."""
        # Mock list_categories to return no matching categories
        self.client.list_categories.return_value = {
            "items": [
                {"id": "cat-1", "name": "existing", "slug": "existing"},
            ]
        }

        # Mock create_category to return new category objects
        self.client.create_category.side_effect = [
            {"id": "cat-new-1", "name": "new-cat-1", "slug": "new-cat-1"},
            {"id": "cat-new-2", "name": "new-cat-2", "slug": "new-cat-2"},
        ]

        result = _resolve_categories(
            self.client, ["new-cat-1", "new-cat-2"], self.group_id
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "cat-new-1")
        self.assertEqual(result[0]["name"], "new-cat-1")
        self.assertEqual(result[1]["id"], "cat-new-2")
        self.assertEqual(result[1]["name"], "new-cat-2")
        self.client.list_categories.assert_called_once()
        self.assertEqual(self.client.create_category.call_count, 2)

    def test_resolve_mixed_existing_and_new_categories(self):
        """Test resolving a mix of existing and new categories."""
        # Mock list_categories to return one existing category
        self.client.list_categories.return_value = {
            "items": [
                {"id": "cat-1", "name": "dinner", "slug": "dinner"},
            ]
        }

        # Mock create_category for new category
        self.client.create_category.return_value = {
            "id": "cat-new", "name": "soup", "slug": "soup"
        }

        result = _resolve_categories(self.client, ["dinner", "soup"], self.group_id)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "cat-1")  # Existing
        self.assertEqual(result[0]["name"], "dinner")
        self.assertEqual(result[1]["id"], "cat-new")  # New
        self.assertEqual(result[1]["name"], "soup")
        self.client.list_categories.assert_called_once()
        self.client.create_category.assert_called_once_with("soup")

    def test_additive_mode_preserves_existing_categories(self):
        """Test ADDITIVE mode preserves existing categories on recipe."""
        # Existing categories on the recipe
        existing_categories = [
            {"id": "cat-1", "name": "dinner", "slug": "dinner"},
            {"id": "cat-2", "name": "soup", "slug": "soup"},
        ]

        # Mock list_categories to return system categories
        self.client.list_categories.return_value = {
            "items": [
                {"id": "cat-1", "name": "dinner", "slug": "dinner"},
                {"id": "cat-2", "name": "soup", "slug": "soup"},
                {"id": "cat-3", "name": "healthy", "slug": "healthy"},
            ]
        }

        # Add "healthy" to existing categories
        result = _resolve_categories(
            self.client,
            ["healthy"],
            self.group_id,
            existing_categories=existing_categories
        )

        self.assertEqual(len(result), 3)
        # First two should be the existing categories (preserved)
        self.assertEqual(result[0]["id"], "cat-1")
        self.assertEqual(result[1]["id"], "cat-2")
        # Third should be the newly added category
        self.assertEqual(result[2]["id"], "cat-3")
        self.assertEqual(result[2]["name"], "healthy")
        self.client.create_category.assert_not_called()

    def test_additive_mode_skips_duplicates(self):
        """Test ADDITIVE mode doesn't add duplicate categories."""
        # Existing categories on the recipe
        existing_categories = [
            {"id": "cat-1", "name": "dinner", "slug": "dinner"},
        ]

        # Mock list_categories
        self.client.list_categories.return_value = {
            "items": [
                {"id": "cat-1", "name": "dinner", "slug": "dinner"},
            ]
        }

        # Try to add "dinner" again
        result = _resolve_categories(
            self.client,
            ["dinner"],
            self.group_id,
            existing_categories=existing_categories
        )

        # Should still have only 1 category (no duplicate)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "cat-1")
        self.client.create_category.assert_not_called()

    def test_empty_category_list(self):
        """Test handling empty category list."""
        self.client.list_categories.return_value = {"items": []}

        result = _resolve_categories(self.client, [], self.group_id)

        self.assertEqual(len(result), 0)
        self.client.list_categories.assert_called_once()
        self.client.create_category.assert_not_called()

    def test_handles_paginated_response(self):
        """Test handling paginated list_categories() response."""
        # Mock list_categories to return paginated response (dict with "items")
        self.client.list_categories.return_value = {
            "items": [
                {"id": "cat-1", "name": "dinner", "slug": "dinner"},
            ],
            "page": 1,
            "totalPages": 1,
        }

        result = _resolve_categories(self.client, ["dinner"], self.group_id)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "cat-1")

    def test_handles_direct_list_response(self):
        """Test handling direct list response (not paginated)."""
        # Mock list_categories to return direct list
        self.client.list_categories.return_value = [
            {"id": "cat-1", "name": "dinner", "slug": "dinner"},
        ]

        result = _resolve_categories(self.client, ["dinner"], self.group_id)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "cat-1")

    def test_propagates_api_errors(self):
        """Test that API errors are propagated to caller."""
        from src.client import MealieAPIError

        # Mock list_categories to raise an error
        self.client.list_categories.side_effect = MealieAPIError(
            "API Error", 500, "Internal Server Error"
        )

        with self.assertRaises(MealieAPIError):
            _resolve_categories(self.client, ["dinner"], self.group_id)


if __name__ == "__main__":
    unittest.main()
