"""Fixtures for unit tests.

Provides reusable pytest fixtures specifically for unit testing.
For integration test fixtures (respx mocking, HTTP clients), see ../conftest.py.

These fixtures use the builders from builders.py to generate consistent test data.
"""

import pytest
from unittest.mock import MagicMock
from tests.unit.builders import (
    build_recipe,
    build_mealplan,
    build_shopping_list,
    build_shopping_item,
    build_tag,
    build_category,
    build_tool,
    build_food,
    build_unit,
    build_cookbook,
    build_comment,
    build_timeline_event,
    build_parsed_ingredient
)


@pytest.fixture
def sample_recipe():
    """Sample recipe for testing."""
    return build_recipe()


@pytest.fixture
def sample_mealplan():
    """Sample meal plan for testing."""
    return build_mealplan()


@pytest.fixture
def sample_shopping_list():
    """Sample shopping list for testing."""
    return build_shopping_list()


@pytest.fixture
def sample_shopping_item():
    """Sample shopping list item for testing."""
    return build_shopping_item()


@pytest.fixture
def sample_tag():
    """Sample tag for testing."""
    return build_tag()


@pytest.fixture
def sample_category():
    """Sample category for testing."""
    return build_category()


@pytest.fixture
def sample_tool():
    """Sample kitchen tool for testing."""
    return build_tool()


@pytest.fixture
def sample_food():
    """Sample food for testing."""
    return build_food()


@pytest.fixture
def sample_unit():
    """Sample unit for testing."""
    return build_unit()


@pytest.fixture
def sample_cookbook():
    """Sample cookbook for testing."""
    return build_cookbook()


@pytest.fixture
def sample_comment():
    """Sample comment for testing."""
    return build_comment()


@pytest.fixture
def sample_timeline_event():
    """Sample timeline event for testing."""
    return build_timeline_event()


@pytest.fixture
def sample_parsed_ingredient():
    """Sample parsed ingredient for testing."""
    return build_parsed_ingredient()


@pytest.fixture
def mock_client_isolated():
    """Isolated mock client (no HTTP, no side effects).

    Use this for pure unit tests that don't need actual HTTP mocking.
    For tests that need to mock HTTP responses, use the respx fixtures
    from ../conftest.py instead.

    Returns:
        MagicMock configured as a MealieClient

    Example:
        >>> def test_something(mock_client_isolated):
        ...     mock_client_isolated.get_recipe.return_value = build_recipe()
        ...     result = my_function(mock_client_isolated)
        ...     assert result is not None
    """
    client = MagicMock()
    client.base_url = "https://test.example.com"
    client.api_token = "test-token"
    return client


@pytest.fixture
def multiple_recipes():
    """Generate multiple sample recipes for batch testing.

    Returns:
        List of 3 recipe dictionaries with different names and slugs
    """
    return [
        build_recipe(name="Recipe 1", slug="recipe-1"),
        build_recipe(name="Recipe 2", slug="recipe-2"),
        build_recipe(name="Recipe 3", slug="recipe-3")
    ]


@pytest.fixture
def multiple_mealplans():
    """Generate multiple sample meal plans for batch testing.

    Returns:
        List of meal plans for different days and entry types
    """
    return [
        build_mealplan(meal_date="2025-12-25", entry_type="breakfast"),
        build_mealplan(meal_date="2025-12-25", entry_type="lunch"),
        build_mealplan(meal_date="2025-12-25", entry_type="dinner"),
        build_mealplan(meal_date="2025-12-26", entry_type="breakfast")
    ]


@pytest.fixture
def shopping_list_with_items():
    """Shopping list with multiple items for testing.

    Returns:
        Shopping list dictionary with 3 sample items
    """
    return build_shopping_list(
        name="Test List",
        listItems=[
            build_shopping_item(note="2 cups flour", id="item-1"),
            build_shopping_item(note="1 tsp salt", id="item-2", checked=True),
            build_shopping_item(note="1 lb butter", id="item-3")
        ]
    )


@pytest.fixture
def recipe_with_full_details():
    """Recipe with all fields populated for comprehensive testing.

    Returns:
        Recipe dictionary with tags, categories, ingredients, and instructions
    """
    return build_recipe(
        name="Comprehensive Recipe",
        slug="comprehensive-recipe",
        description="A recipe with all fields populated",
        recipeYield="6 servings",
        totalTime="1 hour 30 minutes",
        prepTime="30 minutes",
        cookTime="1 hour",
        recipeIngredient=[
            "2 cups all-purpose flour",
            "1 tsp baking powder",
            "1/2 tsp salt",
            "1 cup sugar",
            "2 large eggs"
        ],
        recipeInstructions=[
            {"text": "Preheat oven to 350F"},
            {"text": "Mix dry ingredients"},
            {"text": "Beat eggs and sugar"},
            {"text": "Combine wet and dry"},
            {"text": "Bake for 45 minutes"}
        ],
        tags=[
            build_tag(name="Vegan"),
            build_tag(name="Quick")
        ],
        recipeCategory=[
            build_category(name="Dessert"),
            build_category(name="Baking")
        ]
    )
