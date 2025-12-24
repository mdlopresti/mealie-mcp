"""
Mealie Recipe Actions Management Tools

Provides tools for managing recipe actions in Mealie. Recipe actions allow
users to create custom automation workflows for recipes (e.g., auto-tag,
notifications, webhooks).
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
# Recipe Actions Management
# -----------------------------------------------------------------------------

def recipe_actions_list(
    page: int = 1,
    per_page: int = 50,
    order_by: Optional[str] = None,
    order_direction: Optional[str] = None
) -> str:
    """List all recipe actions with pagination.

    Args:
        page: Page number (default: 1)
        per_page: Number of actions per page (default: 50)
        order_by: Field to order by
        order_direction: "asc" or "desc"

    Returns:
        JSON string with paginated recipe actions list
    """
    try:
        with MealieClient() as client:
            result = client.list_recipe_actions(
                page=page,
                per_page=per_page,
                order_by=order_by,
                order_direction=order_direction
            )
            return json.dumps({
                "success": True,
                "actions": result
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


def recipe_actions_create(
    action_type: str,
    title: str,
    url: str
) -> str:
    """Create a new recipe action.

    Recipe actions enable custom automation workflows for recipes. The action_type
    determines how the action behaves when triggered:
    - "link": Opens the URL with recipe slug appended
    - "post": Sends a POST request to the URL with recipe data

    Args:
        action_type: Type of action - "link" or "post"
        title: Display title for the action
        url: URL for the action (webhook endpoint or link template)

    Returns:
        JSON string with created recipe action details

    Examples:
        # Create a webhook action to send recipe data to external service
        action_type="post"
        title="Send to Meal Planner"
        url="https://mealplanner.example.com/api/recipes"

        # Create a link action to open recipe in external app
        action_type="link"
        title="Open in MealPrep App"
        url="mealprep://recipe/"
    """
    try:
        with MealieClient() as client:
            action = client.create_recipe_action(action_type, title, url)
            return json.dumps({
                "success": True,
                "message": "Recipe action created successfully",
                "action": action
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


def recipe_actions_get(item_id: str) -> str:
    """Get a specific recipe action by ID.

    Args:
        item_id: The recipe action's UUID

    Returns:
        JSON string with recipe action details
    """
    try:
        with MealieClient() as client:
            action = client.get_recipe_action(item_id)
            return json.dumps({
                "success": True,
                "action": action
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


def recipe_actions_update(
    item_id: str,
    action_type: Optional[str] = None,
    title: Optional[str] = None,
    url: Optional[str] = None
) -> str:
    """Update an existing recipe action.

    Args:
        item_id: The recipe action's UUID
        action_type: New action type - "link" or "post"
        title: New display title
        url: New URL

    Returns:
        JSON string with updated recipe action details
    """
    try:
        with MealieClient() as client:
            action = client.update_recipe_action(
                item_id,
                action_type=action_type,
                title=title,
                url=url
            )
            return json.dumps({
                "success": True,
                "message": "Recipe action updated successfully",
                "action": action
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


def recipe_actions_delete(item_id: str) -> str:
    """Delete a recipe action.

    Args:
        item_id: The recipe action's UUID to delete

    Returns:
        JSON string confirming deletion
    """
    try:
        with MealieClient() as client:
            client.delete_recipe_action(item_id)
            return json.dumps({
                "success": True,
                "message": "Recipe action deleted successfully"
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


def recipe_actions_trigger(
    item_id: str,
    recipe_slug: str
) -> str:
    """Trigger a recipe action for a specific recipe.

    This executes the configured action for the given recipe. Behavior depends
    on the action type:
    - "link": Returns the constructed URL (recipe slug appended)
    - "post": Sends POST request to the URL with recipe data

    Args:
        item_id: The recipe action's UUID
        recipe_slug: The recipe's slug identifier

    Returns:
        JSON string with trigger results

    Example:
        # Trigger a webhook action to send recipe to external service
        item_id="550e8400-e29b-41d4-a716-446655440000"
        recipe_slug="sous-vide-salmon"
    """
    try:
        with MealieClient() as client:
            result = client.trigger_recipe_action(item_id, recipe_slug)
            return json.dumps({
                "success": True,
                "message": "Recipe action triggered successfully",
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
