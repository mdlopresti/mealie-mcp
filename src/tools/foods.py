"""
Mealie Foods & Units Management Tools

Provides tools for managing foods and units in Mealie, including:
- List, get, update, delete operations
- Merge duplicate foods/units
"""

import json
import sys
from pathlib import Path
from typing import Optional

# Handle imports for both module usage and standalone execution
try:
    from ..client import MealieClient, MealieAPIError
except ImportError:
    # Add parent directory to path for standalone execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from client import MealieClient, MealieAPIError


# -----------------------------------------------------------------------------
# Foods Management
# -----------------------------------------------------------------------------

def foods_list(page: int = 1, per_page: int = 50) -> str:
    """List all foods with pagination.

    Args:
        page: Page number (1-indexed)
        per_page: Number of foods per page

    Returns:
        JSON string with paginated food list
    """
    try:
        with MealieClient() as client:
            result = client.list_foods(page, per_page)
            return json.dumps(result, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def foods_create(
    name: str,
    description: Optional[str] = None,
    label_id: Optional[str] = None
) -> str:
    """Create a new food.

    Args:
        name: Name for the new food
        description: Optional description
        label_id: Optional label ID (UUID) to assign

    Returns:
        JSON string with created food details
    """
    try:
        with MealieClient() as client:
            result = client.create_food(name, description, label_id)
            return json.dumps({
                "success": True,
                "message": "Food created successfully",
                "food": result
            }, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def foods_get(food_id: str) -> str:
    """Get a specific food by ID.

    Args:
        food_id: The food's ID

    Returns:
        JSON string with food details
    """
    try:
        with MealieClient() as client:
            food = client.get_food(food_id)
            return json.dumps(food, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def foods_update(
    food_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    label_id: Optional[str] = None
) -> str:
    """Update an existing food.

    Args:
        food_id: The food's ID
        name: New name for the food
        description: New description
        label_id: Label ID (UUID) to assign to the food

    Returns:
        JSON string with updated food details
    """
    try:
        with MealieClient() as client:
            food = client.update_food(food_id, name, description, label_id)
            return json.dumps({
                "success": True,
                "message": "Food updated successfully",
                "food": food
            }, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def foods_delete(food_id: str) -> str:
    """Delete a food.

    Args:
        food_id: The food's ID to delete

    Returns:
        JSON string confirming deletion
    """
    try:
        with MealieClient() as client:
            client.delete_food(food_id)
            return json.dumps({
                "success": True,
                "message": "Food deleted successfully"
            }, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def foods_merge(from_food_id: str, to_food_id: str) -> str:
    """Merge one food into another (combines usage across recipes).

    Args:
        from_food_id: Source food ID (will be deleted)
        to_food_id: Target food ID (will absorb all references)

    Returns:
        JSON string with merge results
    """
    try:
        with MealieClient() as client:
            result = client.merge_foods(from_food_id, to_food_id)
            return json.dumps({
                "success": True,
                "message": "Foods merged successfully",
                "result": result
            }, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


# -----------------------------------------------------------------------------
# Units Management
# -----------------------------------------------------------------------------

def units_list(page: int = 1, per_page: int = 50) -> str:
    """List all units with pagination.

    Args:
        page: Page number (1-indexed)
        per_page: Number of units per page

    Returns:
        JSON string with paginated unit list
    """
    try:
        with MealieClient() as client:
            result = client.list_units(page, per_page)
            return json.dumps(result, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def units_create(
    name: str,
    description: Optional[str] = None,
    abbreviation: Optional[str] = None
) -> str:
    """Create a new unit.

    Args:
        name: Name for the new unit
        description: Optional description
        abbreviation: Optional abbreviation (e.g., "tsp", "oz")

    Returns:
        JSON string with created unit details
    """
    try:
        with MealieClient() as client:
            result = client.create_unit(name, description, abbreviation)
            return json.dumps({
                "success": True,
                "message": "Unit created successfully",
                "unit": result
            }, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def units_get(unit_id: str) -> str:
    """Get a specific unit by ID.

    Args:
        unit_id: The unit's ID

    Returns:
        JSON string with unit details
    """
    try:
        with MealieClient() as client:
            unit = client.get_unit(unit_id)
            return json.dumps(unit, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def units_update(
    unit_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    abbreviation: Optional[str] = None
) -> str:
    """Update an existing unit.

    Args:
        unit_id: The unit's ID
        name: New name for the unit
        description: New description
        abbreviation: New abbreviation

    Returns:
        JSON string with updated unit details
    """
    try:
        with MealieClient() as client:
            unit = client.update_unit(unit_id, name, description, abbreviation)
            return json.dumps({
                "success": True,
                "message": "Unit updated successfully",
                "unit": unit
            }, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def units_delete(unit_id: str) -> str:
    """Delete a unit.

    Args:
        unit_id: The unit's ID to delete

    Returns:
        JSON string confirming deletion
    """
    try:
        with MealieClient() as client:
            client.delete_unit(unit_id)
            return json.dumps({
                "success": True,
                "message": "Unit deleted successfully"
            }, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def units_merge(from_unit_id: str, to_unit_id: str) -> str:
    """Merge one unit into another (combines usage across recipes).

    Args:
        from_unit_id: Source unit ID (will be deleted)
        to_unit_id: Target unit ID (will absorb all references)

    Returns:
        JSON string with merge results
    """
    try:
        with MealieClient() as client:
            result = client.merge_units(from_unit_id, to_unit_id)
            return json.dumps({
                "success": True,
                "message": "Units merged successfully",
                "result": result
            }, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)
