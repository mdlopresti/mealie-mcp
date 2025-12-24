"""Example test file demonstrating the new test utilities.

This file shows how to use the enhanced test utilities from tests/utils/
to write cleaner, more maintainable tests.

Compare this with the original pattern in tests/test_tools_mealplans.py to see
the improvements in readability and reduced boilerplate.
"""

from unittest.mock import patch
from src.client import MealieAPIError

# Import the new utilities
from tests.utils import (
    # Mock factories
    create_mock_client,
    MockClientBuilder,
    MockResponsePresets,
    # Assertions
    assert_success_response,
    assert_error_response,
    assert_paginated_response,
    assert_batch_operation_response,
    assert_valid_uuid,
    assert_valid_date,
    assert_list_items_have_structure,
    # Data factories
    RecipeFactory,
    MealPlanFactory,
    ShoppingListFactory,
    TagFactory,
)

# Import the tools we're testing
from src.tools.mealplans import (
    mealplans_list,
    mealplans_today,
    mealplans_get,
    mealplans_create,
    mealplans_update,
    mealplans_delete,
    mealplans_search,
    mealplans_delete_range,
)


class TestMealPlansWithUtils:
    """Examples of testing meal plan tools using the new utilities."""

    def test_mealplans_list_success(self):
        """Test listing meal plans using factory and assertions.

        OLD PATTERN:
            mock_client = create_mock_client(get_value=[{"id": "1", "date": "2025-01-01"}])
            result = mealplans_list()
            data = json.loads(result)
            assert isinstance(data, (dict, list))

        NEW PATTERN:
            - Use MealPlanFactory for realistic test data
            - Use assert_success_response for validation
        """
        # Create realistic test data
        mealplans = MealPlanFactory.create_week("2025-12-25")

        # Configure mock client
        mock_client = create_mock_client(get_value=mealplans)

        # Execute test
        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_list(start_date="2025-12-25", end_date="2025-12-31")

        # Validate response - more thorough than old pattern
        data = assert_success_response(result)
        assert isinstance(data, list)
        assert len(data) == 21  # 7 days × 3 meals

    def test_mealplans_today_with_structure_validation(self):
        """Test today's meal plans with structure validation.

        Demonstrates:
        - Using factory to create a day of meals
        - Validating response structure with assertions
        """
        # Create a full day of meals
        today_meals = MealPlanFactory.create_day()

        mock_client = create_mock_client(get_value=today_meals)

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_today()

        # Validate response structure
        data = assert_success_response(result, expected_keys=["meals"])

        # Validate each meal type has correct structure
        for entry_type in ["breakfast", "lunch", "dinner"]:
            if entry_type in data["meals"]:
                meals = data["meals"][entry_type]
                assert_list_items_have_structure(
                    meals,
                    required_keys=["id", "date", "entryType"],
                    item_name="meal plan"
                )

    def test_mealplans_get_with_validation(self):
        """Test getting a specific meal plan with field validation.

        Demonstrates:
        - Using factory with customization
        - Validating UUIDs and dates
        """
        # Create specific meal plan
        mealplan = MealPlanFactory.create(
            meal_date="2025-12-25",
            entry_type="dinner"
        )

        mock_client = create_mock_client(get_value=mealplan)

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_get(mealplan["id"])

        # Validate response and fields
        data = assert_success_response(result, expected_keys=["id", "date", "entryType"])
        assert_valid_uuid(data["id"], "meal plan ID")
        assert_valid_date(data["date"], "meal date")
        assert data["entryType"] == "dinner"

    def test_mealplans_create_with_recipe(self):
        """Test creating a meal plan with a recipe attached.

        Demonstrates:
        - Using MealPlanFactory.with_recipe()
        - Builder pattern for mock client
        """
        # Create meal plan with recipe
        mealplan = MealPlanFactory.with_recipe()

        # Use builder for more complex mock
        mock_client = (MockClientBuilder()
            .with_post_response("/mealplans", mealplan)
            .build())

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_create(
                meal_date="2025-12-25",
                entry_type="dinner",
                recipe_id=mealplan["recipeId"]
            )

        # Validate creation
        data = assert_success_response(result)
        assert data["recipeId"] == mealplan["recipeId"]
        assert data["entryType"] == "dinner"

    def test_mealplans_update_success(self):
        """Test updating a meal plan.

        Demonstrates:
        - Using factory for both existing and updated data
        - MockClientBuilder for GET + PUT responses
        """
        # Create existing meal plan
        existing = MealPlanFactory.create(meal_date="2025-12-25")

        # Create updated version
        updated = {**existing, "date": "2025-12-26"}

        # Configure mock for GET (retrieve existing) and PUT (update)
        mock_client = (MockClientBuilder()
            .with_get_response("/mealplans/", existing)
            .with_put_response("/mealplans/", updated)
            .build())

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_update(existing["id"], meal_date="2025-12-26")

        # Validate update
        data = assert_success_response(result)
        assert data["date"] == "2025-12-26"

    def test_mealplans_delete_success(self):
        """Test deleting a meal plan.

        Demonstrates:
        - Simple mock creation for DELETE
        - Success response validation
        """
        mock_client = create_mock_client(delete_value=None)

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_delete("mealplan-123")

        data = assert_success_response(result, expected_keys=["success"])
        assert data["success"] is True

    def test_mealplans_search_with_results(self):
        """Test searching meal plans.

        Demonstrates:
        - Creating multiple meal plans with factories
        - Using assertions to validate search results
        """
        # Create meal plans with recipes
        pasta_recipe = RecipeFactory.create(name="Pasta Carbonara", slug="pasta")
        pork_recipe = RecipeFactory.create(name="Pork Chops", slug="pork-chops")

        mealplans = [
            MealPlanFactory.with_recipe(recipe_id=pasta_recipe["id"]),
            MealPlanFactory.with_recipe(recipe_id=pork_recipe["id"]),
        ]

        # Update meal plans with recipe details
        mealplans[0]["recipe"] = pasta_recipe
        mealplans[1]["recipe"] = pork_recipe

        mock_client = create_mock_client(get_value=mealplans)

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_search("pork")

        # Validate search results
        data = assert_success_response(result, expected_keys=["meal_plans", "count"])
        assert data["count"] >= 1
        # Should find the pork meal plan
        pork_found = any("pork" in mp.get("recipe", {}).get("name", "").lower()
                        for mp in data["meal_plans"])
        assert pork_found

    def test_mealplans_delete_range_batch_operation(self):
        """Test deleting a range of meal plans.

        Demonstrates:
        - Using assert_batch_operation_response
        - Creating a week of test data
        """
        # Create a week of meal plans to delete
        week_meals = MealPlanFactory.create_week("2025-01-01")

        mock_client = create_mock_client(
            get_value=week_meals,
            delete_value=None
        )

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_delete_range("2025-01-01", "2025-01-07")

        # Validate batch operation
        data = assert_batch_operation_response(
            result,
            expected_total=21,  # 7 days × 3 meals
            min_success=21,
            max_failures=0
        )
        assert data["deleted"] == 21
        assert data["failed"] == 0

    def test_mealplans_error_handling(self):
        """Test error handling in meal plan operations.

        Demonstrates:
        - Using MockResponsePresets.error_scenarios()
        - Using assert_error_response for validation
        """
        # Use preset for error scenarios
        mock_client = MockResponsePresets.error_scenarios()

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_get("nonexistent-id")

        # Validate error response
        data = assert_error_response(result, expected_status=404)
        assert "error" in data

    def test_mealplans_api_error_with_custom_mock(self):
        """Test API error handling with custom error configuration.

        Demonstrates:
        - Using MockClientBuilder.with_error_on_method()
        - Specific error status and message validation
        """
        # Configure mock to raise specific error
        mock_client = (MockClientBuilder()
            .with_error_on_method("post", 400, "Invalid date format")
            .build())

        with patch('src.tools.mealplans.MealieClient', return_value=mock_client):
            result = mealplans_create("invalid-date", "dinner")

        # Validate error
        data = assert_error_response(result, expected_status=400)
        assert "error" in data


class TestRecipesWithUtils:
    """Example tests for recipes using the new utilities."""

    def test_recipe_with_tags_and_categories(self):
        """Test recipe with tags and categories.

        Demonstrates:
        - Using RecipeFactory.with_tags() and with_categories()
        - Validating nested list structures
        """
        # Create recipe with tags and categories
        recipe = RecipeFactory.with_tags(["Vegan", "Quick"])
        recipe["recipeCategory"] = [
            TagFactory.create(name="Dinner"),
            TagFactory.create(name="Italian")
        ]

        mock_client = create_mock_client(get_value=recipe)

        # In a real test, this would call a recipe tool
        # For now, just validate the test data
        assert len(recipe["tags"]) == 2
        assert len(recipe["recipeCategory"]) == 2

        # Validate structure
        assert_list_items_have_structure(
            recipe["tags"],
            required_keys=["id", "name", "slug"],
            item_name="tag"
        )

    def test_recipe_batch_creation(self):
        """Test batch recipe operations.

        Demonstrates:
        - Using RecipeFactory.create_batch()
        - Validating batch responses
        """
        # Create batch of recipes
        recipes = RecipeFactory.create_batch(5)

        assert len(recipes) == 5
        for i, recipe in enumerate(recipes):
            assert recipe["name"] == f"Test Recipe {i+1}"
            assert_valid_uuid(recipe["id"], f"recipe {i+1} ID")


class TestShoppingWithUtils:
    """Example tests for shopping lists using the new utilities."""

    def test_shopping_list_with_items(self):
        """Test shopping list with items.

        Demonstrates:
        - Using ShoppingListFactory.with_items()
        - Validating nested structures
        """
        # Create shopping list with 10 items
        shopping_list = ShoppingListFactory.with_items(10)

        assert len(shopping_list["listItems"]) == 10

        # Validate item structure
        assert_list_items_have_structure(
            shopping_list["listItems"],
            required_keys=["id", "note", "checked"],
            item_name="shopping item"
        )

    def test_shopping_list_with_checked_items(self):
        """Test shopping list with mixed checked/unchecked items.

        Demonstrates:
        - Using ShoppingListFactory.with_checked_items()
        - Custom validation logic
        """
        # Create list with 10 items, 3 checked
        shopping_list = ShoppingListFactory.with_checked_items(total=10, checked=3)

        # Count checked items
        checked_count = sum(1 for item in shopping_list["listItems"] if item["checked"])
        assert checked_count == 3

        # Count unchecked
        unchecked_count = sum(1 for item in shopping_list["listItems"] if not item["checked"])
        assert unchecked_count == 7


# Summary of improvements shown in this file:
#
# 1. REALISTIC TEST DATA
#    - Old: {"id": "1", "date": "2025-01-01"}
#    - New: MealPlanFactory.create_week() with proper UUIDs, dates, and structure
#
# 2. BETTER VALIDATION
#    - Old: assert isinstance(data, dict)
#    - New: assert_success_response(result, expected_keys=[...])
#
# 3. LESS BOILERPLATE
#    - Old: Manual MagicMock setup for each test
#    - New: create_mock_client() or MockClientBuilder()
#
# 4. REUSABLE PATTERNS
#    - Old: Copy-paste mock setup across tests
#    - New: MockResponsePresets.recipe_crud()
#
# 5. TYPE SAFETY & DOCUMENTATION
#    - All utilities have type hints and comprehensive docstrings
#    - Clear function signatures make tests self-documenting
