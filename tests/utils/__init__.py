"""Test utilities package for Mealie MCP Server.

This package provides reusable utilities for writing tests across unit, integration,
and end-to-end test suites.

Modules:
    mock_factories: Enhanced mock client factory for creating configured mock clients
    assertions: Common assertion helpers for validating responses and data structures
    factories: Test data generators for creating realistic mock data

Quick Start:
    >>> from tests.utils.mock_factories import create_mock_client, MockClientBuilder
    >>> from tests.utils.assertions import assert_success_response, assert_error_response
    >>> from tests.utils.factories import RecipeFactory, MealPlanFactory
    >>>
    >>> # Create a mock client with configured responses
    >>> mock_client = create_mock_client(get_value={"id": "123", "name": "Test"})
    >>>
    >>> # Or use the builder for more complex scenarios
    >>> mock_client = (MockClientBuilder()
    ...     .with_recipe_responses()
    ...     .with_error_on_delete()
    ...     .build())
    >>>
    >>> # Generate test data
    >>> recipe = RecipeFactory.create(name="Test Recipe")
    >>> mealplan = MealPlanFactory.create_breakfast()
    >>>
    >>> # Use assertion helpers
    >>> assert_success_response(result)
    >>> assert_error_response(result, expected_status=404)

See tests/utils/README.md for detailed documentation and examples.
"""

from tests.utils.mock_factories import (
    create_mock_client,
    MockClientBuilder,
    MockResponsePresets,
)

from tests.utils.assertions import (
    assert_success_response,
    assert_error_response,
    assert_paginated_response,
    assert_json_structure,
    assert_valid_uuid,
    assert_valid_iso_timestamp,
    assert_valid_date,
    assert_list_items_have_structure,
    assert_batch_operation_response,
    assert_numeric_in_range,
    assert_non_empty_string,
    assert_has_keys,
)

from tests.utils.factories import (
    RecipeFactory,
    MealPlanFactory,
    ShoppingListFactory,
    TagFactory,
    CategoryFactory,
    ToolFactory,
    FoodFactory,
    UnitFactory,
    CookbookFactory,
    CommentFactory,
    TimelineEventFactory,
    ParsedIngredientFactory,
)

__all__ = [
    # Mock factories
    "create_mock_client",
    "MockClientBuilder",
    "MockResponsePresets",
    # Assertions
    "assert_success_response",
    "assert_error_response",
    "assert_paginated_response",
    "assert_json_structure",
    "assert_valid_uuid",
    "assert_valid_iso_timestamp",
    "assert_valid_date",
    "assert_list_items_have_structure",
    "assert_batch_operation_response",
    "assert_numeric_in_range",
    "assert_non_empty_string",
    "assert_has_keys",
    # Data factories
    "RecipeFactory",
    "MealPlanFactory",
    "ShoppingListFactory",
    "TagFactory",
    "CategoryFactory",
    "ToolFactory",
    "FoodFactory",
    "UnitFactory",
    "CookbookFactory",
    "CommentFactory",
    "TimelineEventFactory",
    "ParsedIngredientFactory",
]
