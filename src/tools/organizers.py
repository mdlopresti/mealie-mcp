"""
Mealie Organizers Management Tools

Provides tools for managing organizers (categories, tags, tools) in Mealie.
"""

import json
from typing import Optional

from ..client import MealieClient, MealieAPIError


# -----------------------------------------------------------------------------
# Categories Management
# -----------------------------------------------------------------------------

def categories_update(
    category_id: str,
    name: Optional[str] = None,
    slug: Optional[str] = None
) -> str:
    """Update a category.

    Args:
        category_id: The category's ID
        name: New name for the category
        slug: New slug for the category

    Returns:
        JSON string with updated category details
    """
    try:
        with MealieClient() as client:
            category = client.update_category(category_id, name, slug)
            return json.dumps({
                "success": True,
                "message": "Category updated successfully",
                "category": category
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


def categories_delete(category_id: str) -> str:
    """Delete a category.

    Args:
        category_id: The category's ID to delete

    Returns:
        JSON string confirming deletion
    """
    try:
        with MealieClient() as client:
            client.delete_category(category_id)
            return json.dumps({
                "success": True,
                "message": "Category deleted successfully"
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
# Tags Management
# -----------------------------------------------------------------------------

def tags_update(
    tag_id: str,
    name: Optional[str] = None,
    slug: Optional[str] = None
) -> str:
    """Update a tag.

    Args:
        tag_id: The tag's ID
        name: New name for the tag
        slug: New slug for the tag

    Returns:
        JSON string with updated tag details
    """
    try:
        with MealieClient() as client:
            tag = client.update_tag(tag_id, name, slug)
            return json.dumps({
                "success": True,
                "message": "Tag updated successfully",
                "tag": tag
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


def tags_delete(tag_id: str) -> str:
    """Delete a tag.

    Args:
        tag_id: The tag's ID to delete

    Returns:
        JSON string confirming deletion
    """
    try:
        with MealieClient() as client:
            client.delete_tag(tag_id)
            return json.dumps({
                "success": True,
                "message": "Tag deleted successfully"
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
# Tools Management
# -----------------------------------------------------------------------------

def tools_update(
    tool_id: str,
    name: Optional[str] = None,
    slug: Optional[str] = None
) -> str:
    """Update a tool.

    Args:
        tool_id: The tool's ID
        name: New name for the tool
        slug: New slug for the tool

    Returns:
        JSON string with updated tool details
    """
    try:
        with MealieClient() as client:
            tool = client.update_tool(tool_id, name, slug)
            return json.dumps({
                "success": True,
                "message": "Tool updated successfully",
                "tool": tool
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


def tools_delete(tool_id: str) -> str:
    """Delete a tool.

    Args:
        tool_id: The tool's ID to delete

    Returns:
        JSON string confirming deletion
    """
    try:
        with MealieClient() as client:
            client.delete_tool(tool_id)
            return json.dumps({
                "success": True,
                "message": "Tool deleted successfully"
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
