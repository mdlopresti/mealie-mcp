"""
Pytest fixtures for E2E tests.

Provides fixtures for real Mealie client, test data cleanup, and unique identifiers.
"""

import os
import logging
import pytest
from typing import Generator
from src.client import MealieClient
from .helpers import generate_unique_id, cleanup_test_data

logger = logging.getLogger(__name__)

# Check for required environment variables at module level
MEALIE_E2E_URL = os.getenv("MEALIE_E2E_URL")
MEALIE_E2E_TOKEN = os.getenv("MEALIE_E2E_TOKEN")

# Skip all E2E tests if environment variables not set
pytestmark = pytest.mark.skipif(
    not MEALIE_E2E_URL or not MEALIE_E2E_TOKEN,
    reason="E2E tests require MEALIE_E2E_URL and MEALIE_E2E_TOKEN environment variables"
)


@pytest.fixture(scope="session")
def e2e_client() -> Generator[MealieClient, None, None]:
    """
    Create a real MealieClient for E2E testing.

    Uses environment variables for configuration:
    - MEALIE_E2E_URL: Base URL of Mealie instance
    - MEALIE_E2E_TOKEN: API token for authentication

    Yields:
        MealieClient instance connected to real Mealie server
    """
    if not MEALIE_E2E_URL or not MEALIE_E2E_TOKEN:
        pytest.skip("E2E environment variables not set")

    logger.info(f"Creating E2E client for {MEALIE_E2E_URL}")
    client = MealieClient(
        base_url=MEALIE_E2E_URL,
        api_token=MEALIE_E2E_TOKEN
    )

    yield client

    # No cleanup needed at session level
    logger.info("E2E client session complete")


@pytest.fixture
def unique_id() -> str:
    """
    Generate a unique identifier for test resources.

    Returns:
        Unique string like "e2e-test-20251223-143052-123456"
    """
    return generate_unique_id("e2e-test")


@pytest.fixture
def test_recipe_cleanup(e2e_client: MealieClient) -> Generator[list[str], None, None]:
    """
    Track and cleanup test recipes.

    Usage:
        def test_something(e2e_client, test_recipe_cleanup):
            recipe = e2e_client.create_recipe(name="Test Recipe")
            test_recipe_cleanup.append(recipe["slug"])
            # ... test logic ...
            # Recipe automatically deleted in teardown

    Yields:
        List to append recipe slugs for cleanup
    """
    recipe_slugs = []
    yield recipe_slugs

    # Cleanup all tracked recipes
    if recipe_slugs:
        logger.info(f"Cleaning up {len(recipe_slugs)} test recipes")
        cleanup_test_data(e2e_client, {"recipes": recipe_slugs})


@pytest.fixture
def test_mealplan_cleanup(e2e_client: MealieClient) -> Generator[list[str], None, None]:
    """
    Track and cleanup test meal plans.

    Usage:
        def test_something(e2e_client, test_mealplan_cleanup):
            mealplan = e2e_client.create_mealplan(...)
            test_mealplan_cleanup.append(mealplan["id"])
            # ... test logic ...
            # Meal plan automatically deleted in teardown

    Yields:
        List to append meal plan IDs for cleanup
    """
    mealplan_ids = []
    yield mealplan_ids

    # Cleanup all tracked meal plans
    if mealplan_ids:
        logger.info(f"Cleaning up {len(mealplan_ids)} test meal plans")
        cleanup_test_data(e2e_client, {"mealplans": mealplan_ids})


@pytest.fixture
def test_shopping_list_cleanup(e2e_client: MealieClient) -> Generator[list[str], None, None]:
    """
    Track and cleanup test shopping lists.

    Usage:
        def test_something(e2e_client, test_shopping_list_cleanup):
            shopping_list = e2e_client.create_shopping_list(name="Test List")
            test_shopping_list_cleanup.append(shopping_list["id"])
            # ... test logic ...
            # Shopping list automatically deleted in teardown

    Yields:
        List to append shopping list IDs for cleanup
    """
    list_ids = []
    yield list_ids

    # Cleanup all tracked shopping lists
    if list_ids:
        logger.info(f"Cleaning up {len(list_ids)} test shopping lists")
        cleanup_test_data(e2e_client, {"shopping_lists": list_ids})


@pytest.fixture
def test_tag_cleanup(e2e_client: MealieClient) -> Generator[list[str], None, None]:
    """
    Track and cleanup test tags.

    Yields:
        List to append tag IDs for cleanup
    """
    tag_ids = []
    yield tag_ids

    if tag_ids:
        logger.info(f"Cleaning up {len(tag_ids)} test tags")
        cleanup_test_data(e2e_client, {"tags": tag_ids})


@pytest.fixture
def test_category_cleanup(e2e_client: MealieClient) -> Generator[list[str], None, None]:
    """
    Track and cleanup test categories.

    Yields:
        List to append category IDs for cleanup
    """
    category_ids = []
    yield category_ids

    if category_ids:
        logger.info(f"Cleaning up {len(category_ids)} test categories")
        cleanup_test_data(e2e_client, {"categories": category_ids})


@pytest.fixture
def test_food_cleanup(e2e_client: MealieClient) -> Generator[list[str], None, None]:
    """
    Track and cleanup test foods.

    Yields:
        List to append food IDs for cleanup
    """
    food_ids = []
    yield food_ids

    if food_ids:
        logger.info(f"Cleaning up {len(food_ids)} test foods")
        cleanup_test_data(e2e_client, {"foods": food_ids})


@pytest.fixture
def test_unit_cleanup(e2e_client: MealieClient) -> Generator[list[str], None, None]:
    """
    Track and cleanup test units.

    Yields:
        List to append unit IDs for cleanup
    """
    unit_ids = []
    yield unit_ids

    if unit_ids:
        logger.info(f"Cleaning up {len(unit_ids)} test units")
        cleanup_test_data(e2e_client, {"units": unit_ids})


@pytest.fixture
def test_cookbook_cleanup(e2e_client: MealieClient) -> Generator[list[str], None, None]:
    """
    Track and cleanup test cookbooks.

    Yields:
        List to append cookbook IDs for cleanup
    """
    cookbook_ids = []
    yield cookbook_ids

    if cookbook_ids:
        logger.info(f"Cleaning up {len(cookbook_ids)} test cookbooks")
        cleanup_test_data(e2e_client, {"cookbooks": cookbook_ids})


@pytest.fixture
def test_tool_cleanup(e2e_client: MealieClient) -> Generator[list[str], None, None]:
    """
    Track and cleanup test tools.

    Yields:
        List to append tool IDs for cleanup
    """
    tool_ids = []
    yield tool_ids

    if tool_ids:
        logger.info(f"Cleaning up {len(tool_ids)} test tools")
        cleanup_test_data(e2e_client, {"tools": tool_ids})


@pytest.fixture
def test_cleanup_all(
    e2e_client: MealieClient,
) -> Generator[dict[str, list[str]], None, None]:
    """
    Universal cleanup fixture for multiple resource types.

    Usage:
        def test_something(e2e_client, test_cleanup_all):
            recipe = e2e_client.create_recipe(name="Test")
            test_cleanup_all["recipes"].append(recipe["slug"])

            tag = e2e_client.create_tag(name="Test Tag")
            test_cleanup_all["tags"].append(tag["id"])
            # ... test logic ...
            # All resources automatically deleted in teardown

    Yields:
        Dict mapping resource types to ID lists for cleanup
    """
    resources = {
        "recipes": [],
        "mealplans": [],
        "shopping_lists": [],
        "tags": [],
        "categories": [],
        "foods": [],
        "units": [],
        "cookbooks": [],
        "tools": []
    }

    yield resources

    # Cleanup all tracked resources
    total_resources = sum(len(ids) for ids in resources.values())
    if total_resources > 0:
        logger.info(f"Cleaning up {total_resources} test resources")
        cleanup_test_data(e2e_client, resources)
