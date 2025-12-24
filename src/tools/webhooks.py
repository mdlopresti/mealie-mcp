"""
Webhooks tools for Mealie MCP server.

Provides tools for managing webhooks - scheduled HTTP callbacks for meal plan notifications
and other automated integrations with external services.
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


def webhooks_list() -> str:
    """List all webhooks.

    Returns:
        JSON string with list of webhooks including their configuration
    """
    try:
        with MealieClient() as client:
            response = client.list_webhooks()

            # Response could be a list or dict with items
            if isinstance(response, dict) and "items" in response:
                items = response["items"]
            elif isinstance(response, list):
                items = response
            else:
                items = [response] if response else []

            webhooks = []
            for webhook in items:
                webhooks.append({
                    "id": webhook.get("id"),
                    "name": webhook.get("name", ""),
                    "url": webhook.get("url"),
                    "enabled": webhook.get("enabled"),
                    "webhook_type": webhook.get("webhookType"),
                    "scheduled_time": webhook.get("scheduledTime"),
                    "group_id": webhook.get("groupId"),
                    "household_id": webhook.get("householdId"),
                })

            return json.dumps({
                "total": len(webhooks),
                "webhooks": webhooks
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def webhooks_create(
    url: str,
    scheduled_time: str,
    enabled: bool = True,
    name: Optional[str] = None,
    webhook_type: str = "mealplan"
) -> str:
    """Create a new webhook.

    Webhooks send scheduled HTTP POST requests to external services. The mealplan webhook
    sends today's meal plan data to the specified URL at the scheduled time each day.

    Args:
        url: Webhook URL to send notifications to (e.g., "https://example.com/webhook")
        scheduled_time: Time to trigger webhook in HH:MM:SS format (e.g., "09:00:00")
        enabled: Whether the webhook is enabled (default: True)
        name: Optional name for the webhook (defaults to empty string)
        webhook_type: Type of webhook - currently only "mealplan" is supported (default: "mealplan")

    Returns:
        JSON string with created webhook data including ID

    Example:
        webhooks_create(
            url="https://example.com/webhook",
            scheduled_time="09:00:00",
            enabled=True,
            name="Morning Meal Plan Notification"
        )
    """
    try:
        with MealieClient() as client:
            response = client.create_webhook(
                url=url,
                scheduled_time=scheduled_time,
                enabled=enabled,
                name=name,
                webhook_type=webhook_type
            )

            # Format response
            webhook = {
                "id": response.get("id"),
                "name": response.get("name", ""),
                "url": response.get("url"),
                "enabled": response.get("enabled"),
                "webhook_type": response.get("webhookType"),
                "scheduled_time": response.get("scheduledTime"),
                "group_id": response.get("groupId"),
                "household_id": response.get("householdId"),
            }

            return json.dumps({
                "success": True,
                "message": "Webhook created successfully",
                "webhook": webhook
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def webhooks_get(item_id: str) -> str:
    """Get a specific webhook by ID.

    Args:
        item_id: Webhook ID (UUID)

    Returns:
        JSON string with webhook details
    """
    try:
        with MealieClient() as client:
            response = client.get_webhook(item_id)

            # Format response
            webhook = {
                "id": response.get("id"),
                "name": response.get("name", ""),
                "url": response.get("url"),
                "enabled": response.get("enabled"),
                "webhook_type": response.get("webhookType"),
                "scheduled_time": response.get("scheduledTime"),
                "group_id": response.get("groupId"),
                "household_id": response.get("householdId"),
            }

            return json.dumps({
                "success": True,
                "webhook": webhook
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def webhooks_update(
    item_id: str,
    url: Optional[str] = None,
    scheduled_time: Optional[str] = None,
    enabled: Optional[bool] = None,
    name: Optional[str] = None,
    webhook_type: Optional[str] = None
) -> str:
    """Update an existing webhook.

    Args:
        item_id: Webhook ID (UUID)
        url: New webhook URL
        scheduled_time: New scheduled time in HH:MM:SS format
        enabled: Whether the webhook is enabled
        name: New name for the webhook
        webhook_type: New webhook type (currently only "mealplan" is supported)

    Returns:
        JSON string with updated webhook data
    """
    try:
        with MealieClient() as client:
            response = client.update_webhook(
                item_id=item_id,
                url=url,
                scheduled_time=scheduled_time,
                enabled=enabled,
                name=name,
                webhook_type=webhook_type
            )

            # Format response
            webhook = {
                "id": response.get("id"),
                "name": response.get("name", ""),
                "url": response.get("url"),
                "enabled": response.get("enabled"),
                "webhook_type": response.get("webhookType"),
                "scheduled_time": response.get("scheduledTime"),
                "group_id": response.get("groupId"),
                "household_id": response.get("householdId"),
            }

            return json.dumps({
                "success": True,
                "message": "Webhook updated successfully",
                "webhook": webhook
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def webhooks_delete(item_id: str) -> str:
    """Delete a webhook.

    Args:
        item_id: Webhook ID (UUID)

    Returns:
        JSON string confirming deletion
    """
    try:
        with MealieClient() as client:
            client.delete_webhook(item_id)

            return json.dumps({
                "success": True,
                "message": f"Webhook {item_id} deleted successfully"
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def webhooks_test(item_id: str) -> str:
    """Test a webhook by sending a test notification.

    This will immediately send a test HTTP POST request to the configured webhook URL
    to verify the webhook is working correctly. The test payload will contain today's
    meal plan data (for mealplan webhooks).

    Args:
        item_id: Webhook ID (UUID)

    Returns:
        JSON string with test result
    """
    try:
        with MealieClient() as client:
            response = client.test_webhook(item_id)

            return json.dumps({
                "success": True,
                "message": "Test webhook request sent successfully",
                "webhook_id": item_id,
                "result": response
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)
