"""
Mealie Organizers Management Tools

Provides tools for managing organizers (categories, tags, tools) in Mealie.
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
# Categories Management
# -----------------------------------------------------------------------------

def categories_list() -> str:
    """List all categories.

    Returns:
        JSON string with list of categories
    """
    try:
        with MealieClient() as client:
            categories = client.list_categories()
            return json.dumps({
                "success": True,
                "categories": categories
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


def categories_create(name: str) -> str:
    """Create a new category.

    Args:
        name: Name for the new category

    Returns:
        JSON string with created category details
    """
    try:
        with MealieClient() as client:
            category = client.create_category(name)
            return json.dumps({
                "success": True,
                "message": "Category created successfully",
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


def categories_get(category_id: str) -> str:
    """Get a category by ID.

    Args:
        category_id: The category's ID

    Returns:
        JSON string with category details
    """
    try:
        with MealieClient() as client:
            category = client.get_category(category_id)
            return json.dumps({
                "success": True,
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

def tags_list() -> str:
    """List all tags.

    Returns:
        JSON string with list of tags
    """
    try:
        with MealieClient() as client:
            tags = client.list_tags()
            return json.dumps({
                "success": True,
                "tags": tags
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


def tags_create(name: str) -> str:
    """Create a new tag.

    Args:
        name: Name for the new tag

    Returns:
        JSON string with created tag details
    """
    try:
        with MealieClient() as client:
            tag = client.create_tag(name)
            return json.dumps({
                "success": True,
                "message": "Tag created successfully",
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


def tags_get(tag_id: str) -> str:
    """Get a tag by ID.

    Args:
        tag_id: The tag's ID

    Returns:
        JSON string with tag details
    """
    try:
        with MealieClient() as client:
            tag = client.get_tag(tag_id)
            return json.dumps({
                "success": True,
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

def tools_list() -> str:
    """List all kitchen tools.

    Returns:
        JSON string with list of tools
    """
    try:
        with MealieClient() as client:
            tools = client.list_tools()
            return json.dumps({
                "success": True,
                "tools": tools
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


def tools_create(name: str) -> str:
    """Create a new kitchen tool.

    Args:
        name: Name for the new tool

    Returns:
        JSON string with created tool details
    """
    try:
        with MealieClient() as client:
            tool = client.create_tool(name)
            return json.dumps({
                "success": True,
                "message": "Tool created successfully",
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


def tools_get(tool_id: str) -> str:
    """Get a kitchen tool by ID.

    Args:
        tool_id: The tool's ID

    Returns:
        JSON string with tool details
    """
    try:
        with MealieClient() as client:
            tool = client.get_tool(tool_id)
            return json.dumps({
                "success": True,
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
