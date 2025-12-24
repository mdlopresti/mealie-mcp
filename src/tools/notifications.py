"""
Event Notifications tools for Mealie MCP server.

Provides tools for managing event notifications - configure alerts for meal prep,
shopping reminders, recipe updates, and other household events.
"""

import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Handle imports for both module usage and standalone execution
try:
    from ..client import MealieClient, MealieAPIError
except ImportError:
    # Add parent directory to path for standalone execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from client import MealieClient, MealieAPIError


def notifications_list() -> str:
    """List all event notifications.

    Returns:
        JSON string with list of notification configurations
    """
    try:
        with MealieClient() as client:
            response = client.list_notifications()

            # Format response
            notifications = []
            for notif in response:
                notifications.append({
                    "id": notif.get("id"),
                    "name": notif.get("name"),
                    "enabled": notif.get("enabled"),
                    "group_id": notif.get("groupId"),
                    "household_id": notif.get("householdId"),
                    "options": notif.get("options", {}),
                })

            return json.dumps({
                "total": len(notifications),
                "notifications": notifications
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def notifications_create(
    name: str,
    apprise_url: Optional[str] = None,
    enabled: bool = True,
    options: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a new event notification.

    Args:
        name: Notification name
        apprise_url: Optional Apprise notification URL (e.g., "discord://webhook_id/webhook_token")
        enabled: Whether the notification is enabled (default: True)
        options: Optional dict of event types to enable (e.g., {"mealplanEntryCreated": true})
            Available event types:
            - testMessage: Test notifications
            - webhookTask: Webhook task events
            - recipeCreated, recipeUpdated, recipeDeleted: Recipe events
            - mealplanEntryCreated: Meal plan events
            - shoppingListCreated, shoppingListUpdated, shoppingListDeleted: Shopping list events
            - cookbookCreated, cookbookUpdated, cookbookDeleted: Cookbook events
            - tagCreated, tagUpdated, tagDeleted: Tag events
            - categoryCreated, categoryUpdated, categoryDeleted: Category events
            - labelCreated, labelUpdated, labelDeleted: Label events
            - userSignup: User signup events
            - dataMigrations, dataExport, dataImport: Data operation events

    Returns:
        JSON string with created notification data
    """
    try:
        with MealieClient() as client:
            response = client.create_notification(
                name=name,
                apprise_url=apprise_url,
                enabled=enabled,
                options=options,
            )

            # Format response
            notification = {
                "id": response.get("id"),
                "name": response.get("name"),
                "enabled": response.get("enabled"),
                "group_id": response.get("groupId"),
                "household_id": response.get("householdId"),
                "options": response.get("options", {}),
                "message": "Notification created successfully"
            }

            return json.dumps(notification, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def notifications_get(item_id: str) -> str:
    """Get a specific notification by ID.

    Args:
        item_id: Notification ID (UUID)

    Returns:
        JSON string with notification details
    """
    try:
        with MealieClient() as client:
            response = client.get_notification(item_id)

            # Format response
            notification = {
                "id": response.get("id"),
                "name": response.get("name"),
                "enabled": response.get("enabled"),
                "group_id": response.get("groupId"),
                "household_id": response.get("householdId"),
                "options": response.get("options", {}),
            }

            return json.dumps(notification, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def notifications_update(
    item_id: str,
    name: Optional[str] = None,
    apprise_url: Optional[str] = None,
    enabled: Optional[bool] = None,
    options: Optional[Dict[str, Any]] = None,
) -> str:
    """Update an existing notification.

    Args:
        item_id: Notification ID (UUID)
        name: New notification name
        apprise_url: New Apprise notification URL (updates the URL if provided)
        enabled: Whether the notification is enabled
        options: New notification options (event types to subscribe to)
            See notifications_create for available event types

    Returns:
        JSON string with updated notification data
    """
    try:
        with MealieClient() as client:
            response = client.update_notification(
                item_id=item_id,
                name=name,
                apprise_url=apprise_url,
                enabled=enabled,
                options=options,
            )

            # Format response
            notification = {
                "id": response.get("id"),
                "name": response.get("name"),
                "enabled": response.get("enabled"),
                "group_id": response.get("groupId"),
                "household_id": response.get("householdId"),
                "options": response.get("options", {}),
                "message": "Notification updated successfully"
            }

            return json.dumps(notification, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def notifications_delete(item_id: str) -> str:
    """Delete a notification.

    Args:
        item_id: Notification ID (UUID)

    Returns:
        JSON string confirming deletion
    """
    try:
        with MealieClient() as client:
            client.delete_notification(item_id)

            return json.dumps({
                "success": True,
                "message": f"Notification {item_id} deleted successfully"
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def notifications_test(item_id: str) -> str:
    """Test a notification by sending a test message.

    This will send a test notification through the configured Apprise URL
    to verify the notification is working correctly.

    Args:
        item_id: Notification ID (UUID)

    Returns:
        JSON string with test result
    """
    try:
        with MealieClient() as client:
            response = client.test_notification(item_id)

            return json.dumps({
                "success": True,
                "message": "Test notification sent successfully",
                "notification_id": item_id,
                "response": response
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)
