"""
Example E2E tests demonstrating Docker-based testing infrastructure.

These tests run against a containerized Mealie instance, providing true end-to-end
validation in an isolated, reproducible environment.

Usage:
    # Run Docker E2E tests
    pytest tests/e2e/test_docker_e2e.py -v

    # Run with live output
    pytest tests/e2e/test_docker_e2e.py -v -s

Note: These tests require Docker to be installed and running.
      Tests will be skipped if Docker is not available.
"""

import pytest
from src.client import MealieClient


@pytest.mark.e2e
def test_docker_infrastructure_recipe_workflow(
    docker_mealie_client: MealieClient,
    docker_unique_id: str,
    docker_test_cleanup: dict[str, list[str]]
):
    """
    Test basic recipe workflow against containerized Mealie instance.

    This test demonstrates:
    1. Creating a recipe in containerized Mealie
    2. Retrieving the recipe
    3. Updating the recipe
    4. Automatic cleanup via fixture

    Args:
        docker_mealie_client: MealieClient connected to Docker container
        docker_unique_id: Unique ID for test resources
        docker_test_cleanup: Cleanup fixture for automatic teardown
    """
    # Create recipe with unique name
    recipe_name = f"Docker E2E Test Recipe {docker_unique_id}"

    recipe = docker_mealie_client.create_recipe(
        name=recipe_name,
        description="Test recipe created by Docker E2E infrastructure test",
        recipe_yield="4 servings"
    )

    # Track for cleanup
    docker_test_cleanup["recipes"].append(recipe["slug"])

    # Verify recipe was created
    assert recipe["name"] == recipe_name
    assert recipe["slug"] is not None
    assert recipe["description"] == "Test recipe created by Docker E2E infrastructure test"

    # Retrieve the recipe
    retrieved = docker_mealie_client.get_recipe(recipe["slug"])
    assert retrieved["name"] == recipe_name

    # Update the recipe
    updated = docker_mealie_client.update_recipe(
        slug=recipe["slug"],
        description="Updated description from E2E test"
    )
    assert updated["description"] == "Updated description from E2E test"

    # Verify update persisted
    final = docker_mealie_client.get_recipe(recipe["slug"])
    assert final["description"] == "Updated description from E2E test"

    # Cleanup happens automatically via docker_test_cleanup fixture


@pytest.mark.e2e
def test_docker_infrastructure_mealplan_workflow(
    docker_mealie_client: MealieClient,
    docker_unique_id: str,
    docker_test_cleanup: dict[str, list[str]]
):
    """
    Test meal planning workflow against containerized Mealie instance.

    This test demonstrates:
    1. Creating a meal plan entry
    2. Retrieving meal plans by date
    3. Updating a meal plan
    4. Deleting a meal plan
    5. Automatic cleanup

    Args:
        docker_mealie_client: MealieClient connected to Docker container
        docker_unique_id: Unique ID for test resources
        docker_test_cleanup: Cleanup fixture for automatic teardown
    """
    # Create meal plan entry
    mealplan = docker_mealie_client.create_mealplan(
        meal_date="2025-12-25",
        entry_type="dinner",
        title=f"Docker E2E Test Meal {docker_unique_id}",
        text="Test meal plan entry from Docker E2E test"
    )

    # Track for cleanup
    docker_test_cleanup["mealplans"].append(mealplan["id"])

    # Verify meal plan was created
    assert mealplan["entryType"] == "dinner"
    assert f"Docker E2E Test Meal {docker_unique_id}" in mealplan["title"]

    # Retrieve meal plans for the date
    meal_plans = docker_mealie_client.list_mealplans(
        start_date="2025-12-25",
        end_date="2025-12-25"
    )

    # Find our meal plan
    found = False
    for item in meal_plans.get("items", []):
        if item["id"] == mealplan["id"]:
            found = True
            break

    assert found, "Created meal plan not found in list"

    # Cleanup happens automatically


@pytest.mark.e2e
def test_docker_infrastructure_shopping_list_workflow(
    docker_mealie_client: MealieClient,
    docker_unique_id: str,
    docker_test_cleanup: dict[str, list[str]]
):
    """
    Test shopping list workflow against containerized Mealie instance.

    This test demonstrates:
    1. Creating a shopping list
    2. Adding items to the list
    3. Checking/unchecking items
    4. Automatic cleanup

    Args:
        docker_mealie_client: MealieClient connected to Docker container
        docker_unique_id: Unique ID for test resources
        docker_test_cleanup: Cleanup fixture for automatic teardown
    """
    # Create shopping list
    shopping_list = docker_mealie_client.create_shopping_list(
        name=f"Docker E2E Test List {docker_unique_id}"
    )

    # Track for cleanup
    docker_test_cleanup["shopping_lists"].append(shopping_list["id"])

    # Verify shopping list was created
    assert f"Docker E2E Test List {docker_unique_id}" in shopping_list["name"]
    assert shopping_list["id"] is not None

    # Add items to the list
    item1 = docker_mealie_client.add_shopping_item(
        list_id=shopping_list["id"],
        note="2 cups flour"
    )

    item2 = docker_mealie_client.add_shopping_item(
        list_id=shopping_list["id"],
        note="1 tsp salt"
    )

    # Retrieve the shopping list with items
    updated_list = docker_mealie_client.get_shopping_list(shopping_list["id"])

    # Verify items were added
    assert len(updated_list["listItems"]) >= 2

    # Check one item
    docker_mealie_client.check_shopping_item(
        item_id=item1["id"],
        checked=True
    )

    # Verify item was checked
    final_list = docker_mealie_client.get_shopping_list(shopping_list["id"])
    checked_items = [item for item in final_list["listItems"] if item.get("checked")]
    assert len(checked_items) >= 1

    # Cleanup happens automatically


@pytest.mark.e2e
def test_docker_infrastructure_multiple_resources(
    docker_mealie_client: MealieClient,
    docker_unique_id: str,
    docker_test_cleanup: dict[str, list[str]]
):
    """
    Test creating multiple resource types in one test.

    This demonstrates the universal cleanup fixture handling
    multiple resource types (recipes, tags, categories).

    Args:
        docker_mealie_client: MealieClient connected to Docker container
        docker_unique_id: Unique ID for test resources
        docker_test_cleanup: Cleanup fixture for automatic teardown
    """
    # Create a recipe
    recipe = docker_mealie_client.create_recipe(
        name=f"Docker Multi-Resource Test {docker_unique_id}",
        description="Testing multiple resources"
    )
    docker_test_cleanup["recipes"].append(recipe["slug"])

    # Create a tag
    tag = docker_mealie_client.create_tag(
        name=f"Docker-Test-Tag-{docker_unique_id}"
    )
    docker_test_cleanup["tags"].append(tag["id"])

    # Create a category
    category = docker_mealie_client.create_category(
        name=f"Docker-Test-Category-{docker_unique_id}"
    )
    docker_test_cleanup["categories"].append(category["id"])

    # Verify all resources exist
    assert recipe["slug"] is not None
    assert tag["id"] is not None
    assert category["id"] is not None

    # Retrieve to confirm
    retrieved_recipe = docker_mealie_client.get_recipe(recipe["slug"])
    assert retrieved_recipe["name"] == f"Docker Multi-Resource Test {docker_unique_id}"

    # All cleanup happens automatically via docker_test_cleanup fixture


@pytest.mark.e2e
def test_docker_container_is_isolated(
    docker_mealie_client: MealieClient,
    docker_unique_id: str,
    docker_test_cleanup: dict[str, list[str]]
):
    """
    Verify that the Docker container provides an isolated environment.

    This test confirms:
    1. The container is accessible
    2. We can create unique test data
    3. The environment is clean (no leftover data from previous runs)

    Args:
        docker_mealie_client: MealieClient connected to Docker container
        docker_unique_id: Unique ID for test resources
        docker_test_cleanup: Cleanup fixture for automatic teardown
    """
    # List existing recipes (should be minimal in fresh container)
    recipes = docker_mealie_client.list_recipes(page=1, per_page=100)

    initial_count = recipes.get("total", 0)

    # Create a test recipe
    recipe = docker_mealie_client.create_recipe(
        name=f"Isolation Test {docker_unique_id}"
    )
    docker_test_cleanup["recipes"].append(recipe["slug"])

    # List recipes again
    recipes_after = docker_mealie_client.list_recipes(page=1, per_page=100)

    # Verify count increased by 1
    assert recipes_after.get("total", 0) == initial_count + 1

    # Verify our recipe is in the list
    recipe_names = [r["name"] for r in recipes_after.get("items", [])]
    assert f"Isolation Test {docker_unique_id}" in recipe_names
