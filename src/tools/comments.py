"""Mealie Recipe Comments Management Tools"""
import json
import sys
from pathlib import Path

try:
    from ..client import MealieClient, MealieAPIError
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from client import MealieClient, MealieAPIError


def comments_get_recipe(recipe_slug: str) -> str:
    """Get all comments for a recipe."""
    try:
        with MealieClient() as client:
            comments = client.get_recipe_comments(recipe_slug)
            return json.dumps({"success": True, "comments": comments}, indent=2)
    except MealieAPIError as e:
        return json.dumps({"error": str(e), "status_code": e.status_code, "response_body": e.response_body}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def comments_create(recipe_id: str, text: str) -> str:
    """Create a comment on a recipe."""
    try:
        with MealieClient() as client:
            comment = client.create_comment(recipe_id, text)
            return json.dumps({"success": True, "message": "Comment created successfully", "comment": comment}, indent=2)
    except MealieAPIError as e:
        return json.dumps({"error": str(e), "status_code": e.status_code, "response_body": e.response_body}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def comments_get(comment_id: str) -> str:
    """Get a comment by ID."""
    try:
        with MealieClient() as client:
            comment = client.get_comment(comment_id)
            return json.dumps({"success": True, "comment": comment}, indent=2)
    except MealieAPIError as e:
        return json.dumps({"error": str(e), "status_code": e.status_code, "response_body": e.response_body}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def comments_update(comment_id: str, text: str) -> str:
    """Update a comment."""
    try:
        with MealieClient() as client:
            comment = client.update_comment(comment_id, text)
            return json.dumps({"success": True, "message": "Comment updated successfully", "comment": comment}, indent=2)
    except MealieAPIError as e:
        return json.dumps({"error": str(e), "status_code": e.status_code, "response_body": e.response_body}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def comments_delete(comment_id: str) -> str:
    """Delete a comment."""
    try:
        with MealieClient() as client:
            client.delete_comment(comment_id)
            return json.dumps({"success": True, "message": "Comment deleted successfully"}, indent=2)
    except MealieAPIError as e:
        return json.dumps({"error": str(e), "status_code": e.status_code, "response_body": e.response_body}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)
