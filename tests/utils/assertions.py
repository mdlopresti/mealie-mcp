"""Assertion helpers for validating test responses and data structures.

This module provides reusable assertion functions to simplify common test validations,
particularly for JSON responses and API data structures.

Usage:
    >>> from tests.utils.assertions import assert_success_response, assert_error_response
    >>> result = some_tool_function()
    >>> assert_success_response(result)  # Validates JSON and success structure
    >>> assert_error_response(result, expected_status=404)  # Validates error format
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid as uuid_module


def assert_success_response(
    json_string: str,
    expected_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Assert that a JSON response represents a successful operation.

    Validates:
    - String is valid JSON
    - Response has success=True (if success field exists)
    - Response does not have an error field
    - Optional: Response has expected keys

    Args:
        json_string: JSON string to validate
        expected_keys: Optional list of keys that must be present

    Returns:
        Parsed JSON dictionary

    Raises:
        AssertionError: If validation fails

    Example:
        >>> result = recipes_get("test-slug")
        >>> data = assert_success_response(result, expected_keys=["id", "name", "slug"])
        >>> assert data["name"] == "Test Recipe"
    """
    # Parse JSON
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON: {e}")

    # Check for error field (should not exist in success response)
    if "error" in data:
        raise AssertionError(f"Expected success but got error: {data.get('error')}")

    # Check success field if present
    if "success" in data and data["success"] is False:
        raise AssertionError(f"Expected success=True but got success=False")

    # Check expected keys
    if expected_keys:
        missing_keys = set(expected_keys) - set(data.keys())
        if missing_keys:
            raise AssertionError(f"Missing expected keys: {missing_keys}")

    return data


def assert_error_response(
    json_string: str,
    expected_status: Optional[int] = None,
    expected_message: Optional[str] = None
) -> Dict[str, Any]:
    """Assert that a JSON response represents an error.

    Validates:
    - String is valid JSON
    - Response has an error field
    - Optional: Response has expected status code
    - Optional: Error message contains expected text

    Args:
        json_string: JSON string to validate
        expected_status: Optional expected HTTP status code
        expected_message: Optional substring expected in error message

    Returns:
        Parsed JSON dictionary

    Raises:
        AssertionError: If validation fails

    Example:
        >>> result = recipes_get("nonexistent-slug")
        >>> data = assert_error_response(result, expected_status=404)
        >>> assert "not found" in data["error"].lower()
    """
    # Parse JSON
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON: {e}")

    # Check for error field
    if "error" not in data:
        raise AssertionError(f"Expected error field but got: {data}")

    # Check status code if provided
    if expected_status is not None:
        if "status_code" not in data:
            raise AssertionError(f"Expected status_code field but got: {data}")
        if data["status_code"] != expected_status:
            raise AssertionError(
                f"Expected status {expected_status} but got {data['status_code']}"
            )

    # Check error message if provided
    if expected_message is not None:
        error_msg = str(data["error"]).lower()
        if expected_message.lower() not in error_msg:
            raise AssertionError(
                f"Expected '{expected_message}' in error message but got: {data['error']}"
            )

    return data


def assert_paginated_response(
    json_string: str,
    expected_page: Optional[int] = None,
    expected_per_page: Optional[int] = None,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None
) -> Dict[str, Any]:
    """Assert that a JSON response represents a paginated list.

    Validates:
    - String is valid JSON
    - Response has pagination fields (page, per_page, total, items)
    - Optional: Specific page number
    - Optional: Specific per_page value
    - Optional: Minimum number of items
    - Optional: Maximum number of items

    Args:
        json_string: JSON string to validate
        expected_page: Optional expected page number
        expected_per_page: Optional expected items per page
        min_items: Optional minimum number of items in response
        max_items: Optional maximum number of items in response

    Returns:
        Parsed JSON dictionary

    Raises:
        AssertionError: If validation fails

    Example:
        >>> result = recipes_list(page=2, per_page=20)
        >>> data = assert_paginated_response(result, expected_page=2, min_items=1)
        >>> assert len(data["items"]) <= 20
    """
    data = assert_success_response(json_string)

    # Check for required pagination fields
    required_fields = ["page", "per_page", "total", "items"]
    missing_fields = set(required_fields) - set(data.keys())
    if missing_fields:
        raise AssertionError(f"Missing pagination fields: {missing_fields}")

    # Validate items is a list
    if not isinstance(data["items"], list):
        raise AssertionError(f"Expected items to be a list, got {type(data['items'])}")

    # Check specific page number
    if expected_page is not None and data["page"] != expected_page:
        raise AssertionError(f"Expected page {expected_page} but got {data['page']}")

    # Check specific per_page value
    if expected_per_page is not None and data["per_page"] != expected_per_page:
        raise AssertionError(
            f"Expected per_page {expected_per_page} but got {data['per_page']}"
        )

    # Check minimum items
    if min_items is not None and len(data["items"]) < min_items:
        raise AssertionError(
            f"Expected at least {min_items} items but got {len(data['items'])}"
        )

    # Check maximum items
    if max_items is not None and len(data["items"]) > max_items:
        raise AssertionError(
            f"Expected at most {max_items} items but got {len(data['items'])}"
        )

    return data


def assert_json_structure(
    json_string: str,
    required_keys: List[str],
    optional_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Assert that a JSON response has expected structure.

    Validates:
    - String is valid JSON
    - All required keys are present
    - No unexpected keys (if optional_keys provided)

    Args:
        json_string: JSON string to validate
        required_keys: List of keys that must be present
        optional_keys: Optional list of allowed optional keys

    Returns:
        Parsed JSON dictionary

    Raises:
        AssertionError: If validation fails

    Example:
        >>> result = recipes_get("test-slug")
        >>> data = assert_json_structure(
        ...     result,
        ...     required_keys=["id", "slug", "name"],
        ...     optional_keys=["description", "tags", "recipeCategory"]
        ... )
    """
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON: {e}")

    # Check required keys
    missing_keys = set(required_keys) - set(data.keys())
    if missing_keys:
        raise AssertionError(f"Missing required keys: {missing_keys}")

    # Check for unexpected keys if optional_keys specified
    if optional_keys is not None:
        allowed_keys = set(required_keys) | set(optional_keys)
        unexpected_keys = set(data.keys()) - allowed_keys
        if unexpected_keys:
            raise AssertionError(f"Unexpected keys: {unexpected_keys}")

    return data


def assert_valid_uuid(value: str, field_name: str = "value") -> None:
    """Assert that a string is a valid UUID.

    Args:
        value: String to validate as UUID
        field_name: Name of field for error message

    Raises:
        AssertionError: If value is not a valid UUID

    Example:
        >>> assert_valid_uuid("550e8400-e29b-41d4-a716-446655440000")
        >>> data = assert_success_response(result)
        >>> assert_valid_uuid(data["id"], "recipe ID")
    """
    try:
        uuid_module.UUID(value)
    except (ValueError, AttributeError, TypeError):
        raise AssertionError(f"{field_name} is not a valid UUID: {value}")


def assert_valid_iso_timestamp(
    value: str,
    field_name: str = "timestamp",
    allow_none: bool = False
) -> None:
    """Assert that a string is a valid ISO 8601 timestamp.

    Accepts formats:
    - 2025-12-25T10:30:00Z
    - 2025-12-25T10:30:00+00:00
    - 2025-12-25T10:30:00.123456Z

    Args:
        value: String to validate as ISO 8601 timestamp
        field_name: Name of field for error message
        allow_none: If True, allows None values

    Raises:
        AssertionError: If value is not a valid ISO 8601 timestamp

    Example:
        >>> assert_valid_iso_timestamp("2025-12-25T10:30:00Z")
        >>> data = assert_success_response(result)
        >>> assert_valid_iso_timestamp(data["createdAt"], "creation timestamp")
    """
    if value is None:
        if allow_none:
            return
        raise AssertionError(f"{field_name} is None but allow_none=False")

    try:
        # Handle both Z and +00:00 timezone formats
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError, TypeError):
        raise AssertionError(f"{field_name} is not a valid ISO 8601 timestamp: {value}")


def assert_valid_date(value: str, field_name: str = "date") -> None:
    """Assert that a string is a valid date in YYYY-MM-DD format.

    Args:
        value: String to validate as date
        field_name: Name of field for error message

    Raises:
        AssertionError: If value is not a valid date

    Example:
        >>> assert_valid_date("2025-12-25")
        >>> data = assert_success_response(result)
        >>> assert_valid_date(data["meal_date"], "meal plan date")
    """
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except (ValueError, AttributeError, TypeError):
        raise AssertionError(f"{field_name} is not a valid YYYY-MM-DD date: {value}")


def assert_list_items_have_structure(
    items: List[Dict[str, Any]],
    required_keys: List[str],
    item_name: str = "item"
) -> None:
    """Assert that all items in a list have required keys.

    Args:
        items: List of dictionaries to validate
        required_keys: Keys that must be present in each item
        item_name: Name of items for error messages

    Raises:
        AssertionError: If any item is missing required keys

    Example:
        >>> data = assert_success_response(result)
        >>> assert_list_items_have_structure(
        ...     data["recipes"],
        ...     required_keys=["id", "slug", "name"],
        ...     item_name="recipe"
        ... )
    """
    if not isinstance(items, list):
        raise AssertionError(f"Expected list of {item_name}s, got {type(items)}")

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise AssertionError(
                f"{item_name} at index {i} is not a dict: {type(item)}"
            )

        missing_keys = set(required_keys) - set(item.keys())
        if missing_keys:
            raise AssertionError(
                f"{item_name} at index {i} missing keys: {missing_keys}"
            )


def assert_numeric_in_range(
    value: float,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    field_name: str = "value"
) -> None:
    """Assert that a numeric value is within a specified range.

    Args:
        value: Number to check
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)
        field_name: Name of field for error messages

    Raises:
        AssertionError: If value is out of range

    Example:
        >>> assert_numeric_in_range(5, min_value=0, max_value=10, field_name="priority")
        >>> data = assert_success_response(result)
        >>> assert_numeric_in_range(data["quantity"], min_value=0, field_name="quantity")
    """
    if not isinstance(value, (int, float)):
        raise AssertionError(f"{field_name} must be numeric, got {type(value)}")

    if min_value is not None and value < min_value:
        raise AssertionError(
            f"{field_name} is {value}, less than minimum {min_value}"
        )

    if max_value is not None and value > max_value:
        raise AssertionError(
            f"{field_name} is {value}, greater than maximum {max_value}"
        )


def assert_non_empty_string(value: Any, field_name: str = "value") -> None:
    """Assert that a value is a non-empty string.

    Args:
        value: Value to check
        field_name: Name of field for error messages

    Raises:
        AssertionError: If value is not a non-empty string

    Example:
        >>> assert_non_empty_string("test", "name")
        >>> data = assert_success_response(result)
        >>> assert_non_empty_string(data["slug"], "recipe slug")
    """
    if not isinstance(value, str):
        raise AssertionError(f"{field_name} must be a string, got {type(value)}")

    if len(value) == 0:
        raise AssertionError(f"{field_name} must not be empty")


def assert_has_keys(obj: Dict[str, Any], required_keys: List[str]) -> None:
    """Assert that a dictionary has all required keys.

    Args:
        obj: Dictionary to check
        required_keys: List of keys that must be present

    Raises:
        AssertionError: If any required keys are missing

    Example:
        >>> data = assert_success_response(result)
        >>> assert_has_keys(data, ["id", "name", "slug"])
    """
    if not isinstance(obj, dict):
        raise AssertionError(f"Expected dict, got {type(obj)}")

    missing_keys = set(required_keys) - set(obj.keys())
    if missing_keys:
        raise AssertionError(f"Missing required keys: {missing_keys}")


def assert_batch_operation_response(
    json_string: str,
    expected_total: Optional[int] = None,
    min_success: Optional[int] = None,
    max_failures: Optional[int] = None
) -> Dict[str, Any]:
    """Assert that a JSON response represents a batch operation result.

    Validates:
    - String is valid JSON
    - Response has batch operation fields (total, success, failures)
    - Optional: Specific total count
    - Optional: Minimum successful operations
    - Optional: Maximum failed operations

    Args:
        json_string: JSON string to validate
        expected_total: Optional expected total operations
        min_success: Optional minimum successful operations
        max_failures: Optional maximum failed operations

    Returns:
        Parsed JSON dictionary

    Raises:
        AssertionError: If validation fails

    Example:
        >>> result = recipes_bulk_tag(["recipe-1", "recipe-2"], ["Vegan"])
        >>> data = assert_batch_operation_response(result, expected_total=2)
        >>> assert data["success"] >= 1
    """
    data = assert_success_response(json_string)

    # Check for common batch operation fields
    if "success" not in data and "updated" not in data and "deleted" not in data:
        raise AssertionError(
            "Expected batch operation response with success/updated/deleted fields"
        )

    # Check expected total
    if expected_total is not None:
        total_field = "total_requested" if "total_requested" in data else "total_found"
        if total_field in data and data[total_field] != expected_total:
            raise AssertionError(
                f"Expected total {expected_total} but got {data[total_field]}"
            )

    # Check minimum successes
    if min_success is not None:
        success_field = "updated" if "updated" in data else "deleted" if "deleted" in data else "success"
        if success_field in data and data[success_field] < min_success:
            raise AssertionError(
                f"Expected at least {min_success} successes but got {data[success_field]}"
            )

    # Check maximum failures
    if max_failures is not None:
        if "failed" in data and data["failed"] > max_failures:
            raise AssertionError(
                f"Expected at most {max_failures} failures but got {data['failed']}"
            )

    return data
