"""Example unit tests demonstrating the unit test utilities.

This module shows how to use builders, assertions, and fixtures
from the unit test utilities to write clean, maintainable tests.
"""

import pytest
from tests.unit.builders import (
    build_recipe,
    build_mealplan,
    build_shopping_list,
    build_tag,
    build_category,
    build_parsed_ingredient
)
from tests.unit.assertions import (
    assert_recipe_structure,
    assert_mealplan_structure,
    assert_shopping_list_structure,
    assert_tag_structure,
    assert_category_structure,
    assert_has_keys,
    assert_valid_uuid,
    assert_valid_iso_date,
    assert_all_items_have_structure,
    assert_non_empty_string,
    assert_numeric_range
)


class TestRecipeBuilder:
    """Test the recipe builder utility."""

    def test_recipe_builder_defaults(self):
        """Test recipe builder creates valid recipe with defaults."""
        recipe = build_recipe()

        assert_recipe_structure(recipe)
        assert recipe["name"] == "Test Recipe"
        assert recipe["slug"] == "test-recipe"
        assert recipe["id"] == "recipe-test-recipe"

    def test_recipe_builder_with_custom_name(self):
        """Test recipe builder accepts custom name."""
        recipe = build_recipe(name="Custom Recipe", slug="custom")

        assert_recipe_structure(recipe)
        assert recipe["name"] == "Custom Recipe"
        assert recipe["slug"] == "custom"

    def test_recipe_builder_with_overrides(self):
        """Test recipe builder accepts field overrides."""
        recipe = build_recipe(
            recipeYield="8 servings",
            totalTime="2 hours",
            tags=[{"id": "tag-1", "name": "Custom"}]
        )

        assert recipe["recipeYield"] == "8 servings"
        assert recipe["totalTime"] == "2 hours"
        assert len(recipe["tags"]) == 1
        assert recipe["tags"][0]["name"] == "Custom"

    def test_recipe_has_required_arrays(self):
        """Test recipe builder includes required array fields."""
        recipe = build_recipe()

        assert isinstance(recipe["recipeIngredient"], list)
        assert isinstance(recipe["recipeInstructions"], list)
        assert isinstance(recipe["tags"], list)
        assert isinstance(recipe["recipeCategory"], list)


class TestMealplanBuilder:
    """Test the meal plan builder utility."""

    def test_mealplan_builder_defaults(self):
        """Test meal plan builder creates valid meal plan."""
        mealplan = build_mealplan()

        assert_mealplan_structure(mealplan)
        assert mealplan["date"] == "2025-12-25"
        assert mealplan["entryType"] == "dinner"

    def test_mealplan_builder_with_custom_date(self):
        """Test meal plan builder accepts custom date."""
        mealplan = build_mealplan(meal_date="2025-12-26", entry_type="breakfast")

        assert mealplan["date"] == "2025-12-26"
        assert mealplan["entryType"] == "breakfast"

    def test_mealplan_builder_with_recipe(self):
        """Test meal plan builder can associate a recipe."""
        mealplan = build_mealplan(recipeId="recipe-123", title="Custom Title")

        assert mealplan["recipeId"] == "recipe-123"
        assert mealplan["title"] == "Custom Title"


class TestShoppingListBuilder:
    """Test the shopping list builder utility."""

    def test_shopping_list_builder_defaults(self):
        """Test shopping list builder creates valid list."""
        shopping_list = build_shopping_list()

        assert_shopping_list_structure(shopping_list)
        assert shopping_list["name"] == "Test Shopping List"
        assert shopping_list["listItems"] == []

    def test_shopping_list_builder_with_items(self):
        """Test shopping list builder accepts items."""
        from tests.unit.builders import build_shopping_item

        shopping_list = build_shopping_list(
            name="Grocery Run",
            listItems=[
                build_shopping_item(note="2 cups flour"),
                build_shopping_item(note="1 tsp salt")
            ]
        )

        assert shopping_list["name"] == "Grocery Run"
        assert len(shopping_list["listItems"]) == 2
        assert shopping_list["listItems"][0]["note"] == "2 cups flour"


class TestTagAndCategoryBuilders:
    """Test tag and category builder utilities."""

    def test_tag_builder_creates_slug(self):
        """Test tag builder creates slug from name."""
        tag = build_tag(name="Gluten Free")

        assert_tag_structure(tag)
        assert tag["name"] == "Gluten Free"
        assert tag["slug"] == "gluten-free"

    def test_category_builder_creates_slug(self):
        """Test category builder creates slug from name."""
        category = build_category(name="Main Dish")

        assert_category_structure(category)
        assert category["name"] == "Main Dish"
        assert category["slug"] == "main-dish"

    def test_tag_builder_with_override(self):
        """Test tag builder accepts slug override."""
        tag = build_tag(name="Test", slug="custom-slug")

        assert tag["slug"] == "custom-slug"


class TestCustomAssertions:
    """Test custom assertion helpers."""

    def test_assert_has_keys_success(self):
        """Test assert_has_keys passes with all keys present."""
        recipe = build_recipe()

        # Should not raise
        assert_has_keys(recipe, ["id", "slug", "name"])

    def test_assert_has_keys_failure(self):
        """Test assert_has_keys fails with missing keys."""
        recipe = build_recipe()

        with pytest.raises(AssertionError, match="Missing required keys"):
            assert_has_keys(recipe, ["id", "missing_key"])

    def test_assert_recipe_structure_success(self):
        """Test assert_recipe_structure validates recipe."""
        recipe = build_recipe()

        # Should not raise
        assert_recipe_structure(recipe)

    def test_assert_mealplan_structure_validates_entry_type(self):
        """Test assert_mealplan_structure validates entry type."""
        # Valid entry types
        for entry_type in ["breakfast", "lunch", "dinner", "side", "snack"]:
            mealplan = build_mealplan(entry_type=entry_type)
            assert_mealplan_structure(mealplan)  # Should not raise

        # Invalid entry type
        mealplan = build_mealplan(entryType="invalid")
        with pytest.raises(AssertionError, match="entryType must be one of"):
            assert_mealplan_structure(mealplan)

    def test_assert_valid_iso_date_success(self):
        """Test assert_valid_iso_date with valid dates."""
        # Should not raise
        assert_valid_iso_date("2025-12-25")
        assert_valid_iso_date("2025-12-25T10:30:00Z")
        assert_valid_iso_date("2025-12-25T10:30:00+00:00")

    def test_assert_valid_iso_date_failure(self):
        """Test assert_valid_iso_date with invalid dates."""
        with pytest.raises(AssertionError, match="not a valid ISO 8601 date"):
            assert_valid_iso_date("invalid-date")

    def test_assert_non_empty_string_success(self):
        """Test assert_non_empty_string with valid strings."""
        assert_non_empty_string("hello", "name")

    def test_assert_non_empty_string_empty_failure(self):
        """Test assert_non_empty_string with empty string."""
        with pytest.raises(AssertionError, match="must not be empty"):
            assert_non_empty_string("", "name")

    def test_assert_non_empty_string_type_failure(self):
        """Test assert_non_empty_string with non-string."""
        with pytest.raises(AssertionError, match="must be a string"):
            assert_non_empty_string(123, "name")

    def test_assert_numeric_range_success(self):
        """Test assert_numeric_range with valid values."""
        assert_numeric_range(5, min_value=0, max_value=10)
        assert_numeric_range(5, min_value=0)
        assert_numeric_range(5, max_value=10)

    def test_assert_numeric_range_min_failure(self):
        """Test assert_numeric_range below minimum."""
        with pytest.raises(AssertionError, match="less than minimum"):
            assert_numeric_range(-5, min_value=0)

    def test_assert_numeric_range_max_failure(self):
        """Test assert_numeric_range above maximum."""
        with pytest.raises(AssertionError, match="greater than maximum"):
            assert_numeric_range(15, max_value=10)


class TestAssertAllItemsHaveStructure:
    """Test the batch structure assertion helper."""

    def test_all_recipes_valid(self):
        """Test assert_all_items_have_structure with valid recipes."""
        recipes = [
            build_recipe(name="Recipe 1"),
            build_recipe(name="Recipe 2"),
            build_recipe(name="Recipe 3")
        ]

        # Should not raise
        assert_all_items_have_structure(recipes, assert_recipe_structure)

    def test_invalid_recipe_in_list(self):
        """Test assert_all_items_have_structure fails on invalid item."""
        recipes = [
            build_recipe(name="Recipe 1"),
            {"invalid": "structure"},  # Missing required keys
            build_recipe(name="Recipe 3")
        ]

        with pytest.raises(AssertionError, match="Item at index 1 failed validation"):
            assert_all_items_have_structure(recipes, assert_recipe_structure)

    def test_non_list_input(self):
        """Test assert_all_items_have_structure fails on non-list."""
        with pytest.raises(AssertionError, match="Expected list"):
            assert_all_items_have_structure("not a list", assert_recipe_structure)


class TestFixtureUsage:
    """Test using fixtures from conftest."""

    def test_sample_recipe_fixture(self, sample_recipe):
        """Test sample_recipe fixture."""
        assert_recipe_structure(sample_recipe)
        assert sample_recipe["name"] == "Test Recipe"

    def test_sample_mealplan_fixture(self, sample_mealplan):
        """Test sample_mealplan fixture."""
        assert_mealplan_structure(sample_mealplan)
        assert sample_mealplan["entryType"] == "dinner"

    def test_sample_tag_fixture(self, sample_tag):
        """Test sample_tag fixture."""
        assert_tag_structure(sample_tag)
        assert sample_tag["name"] == "Vegan"

    def test_multiple_recipes_fixture(self, multiple_recipes):
        """Test multiple_recipes fixture."""
        assert len(multiple_recipes) == 3
        assert_all_items_have_structure(multiple_recipes, assert_recipe_structure)

    def test_shopping_list_with_items_fixture(self, shopping_list_with_items):
        """Test shopping_list_with_items fixture."""
        assert_shopping_list_structure(shopping_list_with_items)
        assert len(shopping_list_with_items["listItems"]) == 3

    def test_recipe_with_full_details_fixture(self, recipe_with_full_details):
        """Test recipe_with_full_details fixture."""
        assert_recipe_structure(recipe_with_full_details)
        assert len(recipe_with_full_details["recipeIngredient"]) == 5
        assert len(recipe_with_full_details["recipeInstructions"]) == 5
        assert len(recipe_with_full_details["tags"]) == 2
        assert len(recipe_with_full_details["recipeCategory"]) == 2


class TestMockClientIsolated:
    """Test using isolated mock client fixture."""

    def test_mock_client_isolated_fixture(self, mock_client_isolated):
        """Test mock_client_isolated fixture provides configured mock."""
        assert mock_client_isolated.base_url == "https://test.example.com"
        assert mock_client_isolated.api_token == "test-token"

    def test_mock_client_isolated_can_be_configured(self, mock_client_isolated):
        """Test mock_client_isolated can have return values configured."""
        # Configure mock
        mock_client_isolated.get_recipe.return_value = build_recipe(name="Mocked Recipe")

        # Use mock
        result = mock_client_isolated.get_recipe("test-slug")

        assert result["name"] == "Mocked Recipe"
        mock_client_isolated.get_recipe.assert_called_once_with("test-slug")


class TestParsedIngredientBuilder:
    """Test parsed ingredient builder utility."""

    def test_parsed_ingredient_builder_defaults(self):
        """Test parsed ingredient builder creates valid parsed result."""
        from tests.unit.assertions import assert_parsed_ingredient_structure

        parsed = build_parsed_ingredient()

        assert_parsed_ingredient_structure(parsed)
        assert parsed["input"] == "2 cups flour"
        assert parsed["ingredient"]["quantity"] == 2.0
        assert parsed["ingredient"]["unit"]["name"] == "cup"
        assert parsed["ingredient"]["food"]["name"] == "flour"

    def test_parsed_ingredient_builder_custom(self):
        """Test parsed ingredient builder with custom values."""
        parsed = build_parsed_ingredient(
            input_text="1 tbsp olive oil",
            quantity=1.0,
            unit="tablespoon",
            food="olive oil"
        )

        assert parsed["input"] == "1 tbsp olive oil"
        assert parsed["ingredient"]["quantity"] == 1.0
        assert parsed["ingredient"]["unit"]["name"] == "tablespoon"
        assert parsed["ingredient"]["food"]["name"] == "olive oil"

    def test_parsed_ingredient_has_confidence(self):
        """Test parsed ingredient includes confidence scores."""
        parsed = build_parsed_ingredient()

        assert "confidence" in parsed
        assert "quantity" in parsed["confidence"]
        assert "unit" in parsed["confidence"]
        assert "food" in parsed["confidence"]
        assert "average" in parsed["confidence"]
