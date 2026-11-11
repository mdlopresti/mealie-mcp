"""
Mealie food label tools.

Labels are group-level and decide how foods are grouped on shopping lists.
Assign a label to a food with mealie_foods_update(label_id=...).
"""

import json
import sys
from pathlib import Path
from typing import Optional

# Handle imports for both module usage and standalone execution
try:
    from ..client import MealieClient, MealieAPIError
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from client import MealieClient, MealieAPIError


def _api_error(e: MealieAPIError) -> str:
    return json.dumps({
        "error": str(e),
        "status_code": e.status_code,
        "response_body": e.response_body,
    }, indent=2)


def _unexpected(e: Exception) -> str:
    return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def _slim_label(label: dict) -> dict:
    return {"id": label.get("id"), "name": label.get("name"), "color": label.get("color")}


def labels_list(page: int = 1, per_page: int = 100, search: Optional[str] = None) -> str:
    """List food labels."""
    try:
        with MealieClient() as client:
            response = client.list_labels(page=page, per_page=per_page, search=search)
            if isinstance(response, dict) and "items" in response:
                items, total = response["items"], response.get("total", len(response["items"]))
            elif isinstance(response, list):
                items, total = response, len(response)
            else:
                items, total = [], 0
            return json.dumps({"total": total, "labels": [_slim_label(x) for x in items]}, indent=2)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)


def labels_create(name: str, color: str = "#959595") -> str:
    """Create a food label."""
    try:
        with MealieClient() as client:
            label = client.create_label(name=name, color=color)
            return json.dumps({"success": True, "message": "Label created", "label": _slim_label(label)}, indent=2)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)


def labels_get(label_id: str) -> str:
    """Get a food label by ID."""
    try:
        with MealieClient() as client:
            return json.dumps(client.get_label(label_id), indent=2)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)


def labels_update(label_id: str, name: Optional[str] = None, color: Optional[str] = None) -> str:
    """Rename or recolor a food label."""
    if name is None and color is None:
        return json.dumps({"error": "Provide name and/or color to update"}, indent=2)
    try:
        with MealieClient() as client:
            label = client.update_label(label_id, name=name, color=color)
            return json.dumps({"success": True, "message": "Label updated", "label": _slim_label(label)}, indent=2)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)


def labels_delete(label_id: str) -> str:
    """Delete a food label."""
    try:
        with MealieClient() as client:
            client.delete_label(label_id)
            return json.dumps({"success": True, "message": f"Label {label_id} deleted"}, indent=2)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)
