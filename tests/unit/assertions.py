"""Custom assertion helpers for unit tests.

Provides reusable assertion functions to simplify common test validations.
All assertions raise AssertionError with descriptive messages on failure.

Usage:
    >>> from tests.unit.assertions import assert_recipe_structure
    >>> recipe = {"id": "123", "slug": "test", "name": "Test Recipe"}
    >>> assert_recipe_structure(recipe)  # Passes
"""

from typing import Dict, Any, List


def assert_valid_uuid(value: str) -> None:
    """Assert value is a valid UUID.

    Args:
        value: String to validate as UUID

    Raises:
        AssertionError: If value is not a valid UUID

    Example:
        >>> assert_valid_uuid("550e8400-e29b-41d4-a716-446655440000")
        >>> assert_valid_uuid("not-a-uuid")  # Raises AssertionError
    """
    import uuid
    try:
        uuid.UUID(value)
    except ValueError:
        raise AssertionError(f"{value} is not a valid UUID")


def assert_valid_iso_date(value: str) -> None:
    """Assert value is a valid ISO 8601 date.

    Args:
        value: String to validate as ISO 8601 date

    Raises:
        AssertionError: If value is not a valid ISO 8601 date

    Example:
        >>> assert_valid_iso_date("2025-12-25")
        >>> assert_valid_iso_date("2025-12-25T10:30:00Z")
        >>> assert_valid_iso_date("invalid-date")  # Raises AssertionError
    """
    from datetime import datetime
    try:
        # Handle both with and without timezone
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise AssertionError(f"{value} is not a valid ISO 8601 date")


def assert_has_keys(obj: Dict[str, Any], required_keys: List[str]) -> None:
    """Assert dictionary has all required keys.

    Args:
        obj: Dictionary to check
        required_keys: List of keys that must be present

    Raises:
        AssertionError: If any required keys are missing

    Example:
        >>> obj = {"id": "123", "name": "Test"}
        >>> assert_has_keys(obj, ["id", "name"])
        >>> assert_has_keys(obj, ["id", "missing"])  # Raises AssertionError
    """
    missing = set(required_keys) - set(obj.keys())
    if missing:
        raise AssertionError(f"Missing required keys: {missing}")


def assert_recipe_structure(recipe: Dict[str, Any]) -> None:
    """Assert recipe has valid structure.

    Validates that recipe has required fields and correct types for arrays.

    Args:
        recipe: Recipe dictionary to validate

    Raises:
        AssertionError: If structure is invalid

    Example:
        >>> recipe = build_recipe()
        >>> assert_recipe_structure(recipe)
    """
    assert_has_keys(recipe, ["id", "slug", "name"])

    if "tags" in recipe:
        assert isinstance(recipe["tags"], list), "tags must be a list"

    if "recipeCategory" in recipe:
        assert isinstance(recipe["recipeCategory"], list), "recipeCategory must be a list"

    if "recipeIngredient" in recipe:
        assert isinstance(recipe["recipeIngredient"], list), "recipeIngredient must be a list"

    if "recipeInstructions" in recipe:
        assert isinstance(recipe["recipeInstructions"], list), "recipeInstructions must be a list"


def assert_mealplan_structure(mealplan: Dict[str, Any]) -> None:
    """Assert meal plan has valid structure.

    Validates that meal plan has required fields and valid entry type.

    Args:
        mealplan: Meal plan dictionary to validate

    Raises:
        AssertionError: If structure is invalid

    Example:
        >>> mealplan = build_mealplan()
        >>> assert_mealplan_structure(mealplan)
    """
    assert_has_keys(mealplan, ["id", "date", "entryType"])

    valid_entry_types = ["breakfast", "lunch", "dinner", "side", "snack"]
    assert mealplan["entryType"] in valid_entry_types, \
        f"entryType must be one of {valid_entry_types}, got {mealplan['entryType']}"


def assert_shopping_list_structure(shopping_list: Dict[str, Any]) -> None:
    """Assert shopping list has valid structure.

    Args:
        shopping_list: Shopping list dictionary to validate

    Raises:
        AssertionError: If structure is invalid

    Example:
        >>> shopping_list = build_shopping_list()
        >>> assert_shopping_list_structure(shopping_list)
    """
    assert_has_keys(shopping_list, ["id", "name"])

    if "listItems" in shopping_list:
        assert isinstance(shopping_list["listItems"], list), "listItems must be a list"


def assert_tag_structure(tag: Dict[str, Any]) -> None:
    """Assert tag has valid structure.

    Args:
        tag: Tag dictionary to validate

    Raises:
        AssertionError: If structure is invalid

    Example:
        >>> tag = build_tag()
        >>> assert_tag_structure(tag)
    """
    assert_has_keys(tag, ["id", "name", "slug"])


def assert_category_structure(category: Dict[str, Any]) -> None:
    """Assert category has valid structure.

    Args:
        category: Category dictionary to validate

    Raises:
        AssertionError: If structure is invalid

    Example:
        >>> category = build_category()
        >>> assert_category_structure(category)
    """
    assert_has_keys(category, ["id", "name", "slug"])


def assert_tool_structure(tool: Dict[str, Any]) -> None:
    """Assert kitchen tool has valid structure.

    Args:
        tool: Tool dictionary to validate

    Raises:
        AssertionError: If structure is invalid

    Example:
        >>> tool = build_tool()
        >>> assert_tool_structure(tool)
    """
    assert_has_keys(tool, ["id", "name", "slug"])


def assert_food_structure(food: Dict[str, Any]) -> None:
    """Assert food has valid structure.

    Args:
        food: Food dictionary to validate

    Raises:
        AssertionError: If structure is invalid

    Example:
        >>> food = build_food()
        >>> assert_food_structure(food)
    """
    assert_has_keys(food, ["id", "name"])


def assert_unit_structure(unit: Dict[str, Any]) -> None:
    """Assert unit has valid structure.

    Args:
        unit: Unit dictionary to validate

    Raises:
        AssertionError: If structure is invalid

    Example:
        >>> unit = build_unit()
        >>> assert_unit_structure(unit)
    """
    assert_has_keys(unit, ["id", "name"])


def assert_cookbook_structure(cookbook: Dict[str, Any]) -> None:
    """Assert cookbook has valid structure.

    Args:
        cookbook: Cookbook dictionary to validate

    Raises:
        AssertionError: If structure is invalid

    Example:
        >>> cookbook = build_cookbook()
        >>> assert_cookbook_structure(cookbook)
    """
    assert_has_keys(cookbook, ["id", "name", "slug"])

    if "recipes" in cookbook:
        assert isinstance(cookbook["recipes"], list), "recipes must be a list"


def assert_comment_structure(comment: Dict[str, Any]) -> None:
    """Assert comment has valid structure.

    Args:
        comment: Comment dictionary to validate

    Raises:
        AssertionError: If structure is invalid

    Example:
        >>> comment = build_comment()
        >>> assert_comment_structure(comment)
    """
    assert_has_keys(comment, ["id", "recipeId", "text"])


def assert_timeline_event_structure(event: Dict[str, Any]) -> None:
    """Assert timeline event has valid structure.

    Args:
        event: Timeline event dictionary to validate

    Raises:
        AssertionError: If structure is invalid

    Example:
        >>> event = build_timeline_event()
        >>> assert_timeline_event_structure(event)
    """
    assert_has_keys(event, ["id", "recipeId", "subject", "eventType"])

    valid_event_types = ["system", "info", "comment"]
    assert event["eventType"] in valid_event_types, \
        f"eventType must be one of {valid_event_types}, got {event['eventType']}"


def assert_parsed_ingredient_structure(parsed: Dict[str, Any]) -> None:
    """Assert parsed ingredient has valid structure.

    Args:
        parsed: Parsed ingredient dictionary to validate

    Raises:
        AssertionError: If structure is invalid

    Example:
        >>> parsed = build_parsed_ingredient()
        >>> assert_parsed_ingredient_structure(parsed)
    """
    assert_has_keys(parsed, ["input", "ingredient", "confidence"])

    # Check ingredient substructure
    ingredient = parsed["ingredient"]
    if "quantity" in ingredient:
        assert isinstance(ingredient["quantity"], (int, float)), "quantity must be numeric"

    # Check confidence substructure
    confidence = parsed["confidence"]
    assert isinstance(confidence, dict), "confidence must be a dict"


def assert_all_items_have_structure(
    items: List[Dict[str, Any]],
    structure_checker
) -> None:
    """Assert all items in list have valid structure.

    Args:
        items: List of items to validate
        structure_checker: Function to validate each item

    Raises:
        AssertionError: If any item has invalid structure

    Example:
        >>> recipes = [build_recipe(), build_recipe(name="Another")]
        >>> assert_all_items_have_structure(recipes, assert_recipe_structure)
    """
    assert isinstance(items, list), f"Expected list, got {type(items)}"

    for i, item in enumerate(items):
        try:
            structure_checker(item)
        except AssertionError as e:
            raise AssertionError(f"Item at index {i} failed validation: {e}")


def assert_numeric_range(
    value: float,
    min_value: float = None,
    max_value: float = None
) -> None:
    """Assert numeric value is within range.

    Args:
        value: Number to check
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)

    Raises:
        AssertionError: If value is out of range

    Example:
        >>> assert_numeric_range(5, min_value=0, max_value=10)
        >>> assert_numeric_range(15, max_value=10)  # Raises AssertionError
    """
    if min_value is not None and value < min_value:
        raise AssertionError(f"{value} is less than minimum {min_value}")

    if max_value is not None and value > max_value:
        raise AssertionError(f"{value} is greater than maximum {max_value}")


def assert_non_empty_string(value: Any, field_name: str = "value") -> None:
    """Assert value is a non-empty string.

    Args:
        value: Value to check
        field_name: Name of field for error message

    Raises:
        AssertionError: If value is not a non-empty string

    Example:
        >>> assert_non_empty_string("hello", "name")
        >>> assert_non_empty_string("", "name")  # Raises AssertionError
        >>> assert_non_empty_string(123, "name")  # Raises AssertionError
    """
    assert isinstance(value, str), f"{field_name} must be a string, got {type(value)}"
    assert len(value) > 0, f"{field_name} must not be empty"
