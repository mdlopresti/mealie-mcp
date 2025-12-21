"""
Mealie Cookbooks Management Tools

Provides tools for managing cookbooks in Mealie. Cookbooks allow users to
organize recipes into themed collections.
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
# Cookbooks Management
# -----------------------------------------------------------------------------

def cookbooks_list() -> str:
    """List all cookbooks.

    Returns:
        JSON string with list of cookbooks
    """
    try:
        with MealieClient() as client:
            cookbooks = client.list_cookbooks()
            return json.dumps({
                "success": True,
                "cookbooks": cookbooks
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


def cookbooks_create(
    name: str,
    description: Optional[str] = None,
    slug: Optional[str] = None,
    public: bool = False
) -> str:
    """Create a new cookbook.

    Args:
        name: Name for the new cookbook
        description: Optional description
        slug: Optional URL slug
        public: Whether the cookbook is public (default: False)

    Returns:
        JSON string with created cookbook details
    """
    try:
        with MealieClient() as client:
            cookbook = client.create_cookbook(name, description, slug, public)
            return json.dumps({
                "success": True,
                "message": "Cookbook created successfully",
                "cookbook": cookbook
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


def cookbooks_get(cookbook_id: str) -> str:
    """Get a cookbook by ID.

    Args:
        cookbook_id: The cookbook's ID

    Returns:
        JSON string with cookbook details
    """
    try:
        with MealieClient() as client:
            cookbook = client.get_cookbook(cookbook_id)
            return json.dumps({
                "success": True,
                "cookbook": cookbook
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


def cookbooks_update(
    cookbook_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    slug: Optional[str] = None,
    public: Optional[bool] = None
) -> str:
    """Update a cookbook.

    Args:
        cookbook_id: The cookbook's ID
        name: New name for the cookbook
        description: New description
        slug: New URL slug
        public: Whether the cookbook is public

    Returns:
        JSON string with updated cookbook details
    """
    try:
        with MealieClient() as client:
            cookbook = client.update_cookbook(cookbook_id, name, description, slug, public)
            return json.dumps({
                "success": True,
                "message": "Cookbook updated successfully",
                "cookbook": cookbook
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


def cookbooks_delete(cookbook_id: str) -> str:
    """Delete a cookbook.

    Args:
        cookbook_id: The cookbook's ID to delete

    Returns:
        JSON string confirming deletion
    """
    try:
        with MealieClient() as client:
            client.delete_cookbook(cookbook_id)
            return json.dumps({
                "success": True,
                "message": "Cookbook deleted successfully"
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
