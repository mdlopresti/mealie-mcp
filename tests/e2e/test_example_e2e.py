"""
Example E2E test demonstrating the E2E test infrastructure.

This test validates that the E2E fixtures and helpers work correctly.
It creates a simple recipe, verifies it exists, and ensures cleanup happens.
"""

import pytest
from src.client import MealieClient


@pytest.mark.e2e
def test_infrastructure_example(
    e2e_client: MealieClient,
    unique_id: str,
    test_recipe_cleanup: list[str]
):
    """
    Example E2E test showing how to use the fixtures.

    This test:
    1. Creates a recipe with a unique name
    2. Verifies the recipe was created
    3. Relies on fixture for automatic cleanup
    """
    # Create recipe with unique name to avoid collisions
    recipe_name = f"E2E Test Recipe {unique_id}"

    recipe = e2e_client.create_recipe(
        name=recipe_name,
        description="Test recipe created by E2E infrastructure test",
        recipe_yield="4 servings"
    )

    # Track for cleanup
    test_recipe_cleanup.append(recipe["slug"])

    # Verify recipe was created
    assert recipe["name"] == recipe_name
    assert recipe["slug"] is not None
    assert recipe["description"] == "Test recipe created by E2E infrastructure test"

    # Verify we can retrieve it
    retrieved = e2e_client.get_recipe(recipe["slug"])
    assert retrieved["name"] == recipe_name

    # Cleanup happens automatically via test_recipe_cleanup fixture


@pytest.mark.e2e
def test_cleanup_all_fixture(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Example showing the universal cleanup fixture for multiple resource types.

    This test creates multiple resources and relies on test_cleanup_all
    to clean them up automatically.
    """
    # Create a recipe
    recipe = e2e_client.create_recipe(
        name=f"E2E Cleanup Test Recipe {unique_id}",
        description="Testing universal cleanup"
    )
    test_cleanup_all["recipes"].append(recipe["slug"])

    # Create a tag
    tag = e2e_client.create_tag(name=f"E2E Test Tag {unique_id}")
    test_cleanup_all["tags"].append(tag["id"])

    # Create a category
    category = e2e_client.create_category(name=f"E2E Test Category {unique_id}")
    test_cleanup_all["categories"].append(category["id"])

    # Verify resources exist
    assert recipe["slug"] is not None
    assert tag["id"] is not None
    assert category["id"] is not None

    # All cleanup happens automatically via test_cleanup_all fixture
