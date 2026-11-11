"""
Mealie backup tools (admin only).

The API token must belong to a Mealie admin user. Restore is deliberately not
exposed: it replaces the whole database and should be done from Mealie's UI.
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


def backups_list() -> str:
    """List backup files stored on the Mealie server."""
    try:
        with MealieClient() as client:
            response = client.list_backups() or {}
            imports = response.get("imports", []) if isinstance(response, dict) else response
            return json.dumps({"total": len(imports), "backups": imports}, indent=2)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)


def backups_create() -> str:
    """Create a new backup on the Mealie server."""
    try:
        with MealieClient() as client:
            result = client.create_backup()
            return json.dumps({"success": True, "message": "Backup created", "result": result}, indent=2)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)


def backups_get_download_url(file_name: str) -> str:
    """Get a short-lived download URL for a backup file."""
    try:
        with MealieClient() as client:
            token = (client.get_backup_token(file_name) or {}).get("fileToken")
            if not token:
                return json.dumps({"error": "Mealie did not return a download token"}, indent=2)
            base = (client.base_url or "").rstrip("/")
            return json.dumps({
                "file_name": file_name,
                "download_url": f"{base}/api/utils/download?token={token}",
            }, indent=2)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)


def backups_delete(file_name: str) -> str:
    """Delete a backup file from the Mealie server."""
    try:
        with MealieClient() as client:
            client.delete_backup(file_name)
            return json.dumps({"success": True, "message": f"Backup {file_name} deleted"}, indent=2)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)
