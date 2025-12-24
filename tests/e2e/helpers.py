"""
Helper utilities for E2E tests.

Provides retry logic, unique ID generation, and cleanup helpers.
"""

import time
import logging
from datetime import datetime
from typing import Callable, Any, TypeVar
import httpx

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_on_network_error(
    func: Callable[..., T],
    max_retries: int = 3,
    initial_delay: float = 0.5,
    backoff_factor: float = 2.0
) -> T:
    """
    Retry a function on network errors with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 0.5)
        backoff_factor: Multiplier for delay on each retry (default: 2.0)

    Returns:
        Result from successful function call

    Raises:
        Last exception if all retries fail
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func()
        except (httpx.HTTPError, httpx.TimeoutException, httpx.NetworkError) as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)
                delay *= backoff_factor
            else:
                logger.error(f"All {max_retries + 1} attempts failed.")

    # This should never happen, but satisfy type checker
    if last_exception:
        raise last_exception
    raise RuntimeError("Retry logic error: no exception but all attempts failed")


def generate_unique_id(prefix: str = "e2e-test") -> str:
    """
    Generate a unique identifier for test resources.

    Uses timestamp with microseconds to ensure uniqueness across parallel tests.

    Args:
        prefix: Prefix for the identifier (default: "e2e-test")

    Returns:
        Unique identifier string like "e2e-test-20251223-143052-123456"
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    return f"{prefix}-{timestamp}"


def cleanup_test_data(client, resource_ids: dict[str, list[str]]) -> None:
    """
    Bulk cleanup helper for test resources.

    Deletes test resources and ignores 404 errors (already deleted).

    Args:
        client: MealieClient instance
        resource_ids: Dict mapping resource type to list of IDs
            e.g., {"recipes": ["slug1", "slug2"], "shopping_lists": ["id1"]}

    Example:
        cleanup_test_data(client, {
            "recipes": ["test-recipe-1", "test-recipe-2"],
            "shopping_lists": ["list-123"],
            "mealplans": ["mealplan-456"]
        })
    """
    for resource_type, ids in resource_ids.items():
        for resource_id in ids:
            try:
                if resource_type == "recipes":
                    client.delete_recipe(resource_id)
                    logger.debug(f"Deleted recipe: {resource_id}")
                elif resource_type == "shopping_lists":
                    client.delete_shopping_list(resource_id)
                    logger.debug(f"Deleted shopping list: {resource_id}")
                elif resource_type == "mealplans":
                    client.delete_mealplan(resource_id)
                    logger.debug(f"Deleted meal plan: {resource_id}")
                elif resource_type == "tags":
                    client.delete_tag(resource_id)
                    logger.debug(f"Deleted tag: {resource_id}")
                elif resource_type == "categories":
                    client.delete_category(resource_id)
                    logger.debug(f"Deleted category: {resource_id}")
                elif resource_type == "foods":
                    client.delete_food(resource_id)
                    logger.debug(f"Deleted food: {resource_id}")
                elif resource_type == "units":
                    client.delete_unit(resource_id)
                    logger.debug(f"Deleted unit: {resource_id}")
                elif resource_type == "cookbooks":
                    client.delete_cookbook(resource_id)
                    logger.debug(f"Deleted cookbook: {resource_id}")
                elif resource_type == "tools":
                    client.delete_tool(resource_id)
                    logger.debug(f"Deleted tool: {resource_id}")
                else:
                    logger.warning(f"Unknown resource type: {resource_type}")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.debug(
                        f"{resource_type} {resource_id} already deleted (404)"
                    )
                else:
                    logger.error(
                        f"Failed to delete {resource_type} {resource_id}: {e}"
                    )
            except Exception as e:
                logger.error(
                    f"Unexpected error deleting {resource_type} {resource_id}: {e}"
                )
