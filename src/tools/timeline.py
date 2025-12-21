"""
Recipe Timeline Events tools for Mealie MCP server.

Provides tools for managing recipe timeline events - tracking when recipes
were made, adding notes, and building cooking history analytics.
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


def timeline_list(
    page: int = 1,
    per_page: int = 50,
    order_by: Optional[str] = None,
    order_direction: Optional[str] = None,
    query_filter: Optional[str] = None,
) -> str:
    """List all recipe timeline events with pagination.

    Args:
        page: Page number (1-indexed)
        per_page: Number of events per page
        order_by: Field to order by
        order_direction: "asc" or "desc"
        query_filter: Filter query string

    Returns:
        JSON string with paginated timeline events data
    """
    try:
        with MealieClient() as client:
            response = client.list_timeline_events(
                page=page,
                per_page=per_page,
                order_by=order_by,
                order_direction=order_direction,
                query_filter=query_filter,
            )

            # Format response
            if isinstance(response, dict) and "items" in response:
                events = []
                for event in response.get("items", []):
                    events.append({
                        "id": event.get("id"),
                        "recipe_id": event.get("recipeId"),
                        "user_id": event.get("userId"),
                        "subject": event.get("subject"),
                        "event_type": event.get("eventType"),
                        "event_message": event.get("eventMessage"),
                        "timestamp": event.get("timestamp"),
                        "has_image": event.get("image") == "has image",
                    })

                result = {
                    "page": response.get("page"),
                    "per_page": response.get("perPage"),
                    "total": response.get("total"),
                    "total_pages": response.get("totalPages"),
                    "events": events
                }
                return json.dumps(result, indent=2)

            return json.dumps(response, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def timeline_get(event_id: str) -> str:
    """Get a specific timeline event by ID.

    Args:
        event_id: Timeline event ID (UUID)

    Returns:
        JSON string with timeline event details
    """
    try:
        with MealieClient() as client:
            response = client.get_timeline_event(event_id)

            # Format response
            event = {
                "id": response.get("id"),
                "recipe_id": response.get("recipeId"),
                "user_id": response.get("userId"),
                "group_id": response.get("groupId"),
                "household_id": response.get("householdId"),
                "subject": response.get("subject"),
                "event_type": response.get("eventType"),
                "event_message": response.get("eventMessage"),
                "timestamp": response.get("timestamp"),
                "has_image": response.get("image") == "has image",
                "created_at": response.get("createdAt"),
                "update_at": response.get("updateAt"),
            }

            return json.dumps(event, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def timeline_create(
    recipe_id: str,
    subject: str,
    event_type: str = "info",
    event_message: Optional[str] = None,
    user_id: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> str:
    """Create a new timeline event for a recipe.

    Args:
        recipe_id: Recipe ID (UUID)
        subject: Event subject/title
        event_type: Event type ("system", "info", or "comment") - default: "info"
        event_message: Optional event message/description
        user_id: Optional user ID (UUID)
        timestamp: Optional ISO 8601 timestamp (defaults to current time)

    Returns:
        JSON string with created timeline event data
    """
    try:
        with MealieClient() as client:
            response = client.create_timeline_event(
                recipe_id=recipe_id,
                subject=subject,
                event_type=event_type,
                event_message=event_message,
                user_id=user_id,
                timestamp=timestamp,
            )

            # Format response
            event = {
                "id": response.get("id"),
                "recipe_id": response.get("recipeId"),
                "subject": response.get("subject"),
                "event_type": response.get("eventType"),
                "event_message": response.get("eventMessage"),
                "timestamp": response.get("timestamp"),
                "message": "Timeline event created successfully"
            }

            return json.dumps(event, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def timeline_update(
    event_id: str,
    subject: Optional[str] = None,
    event_type: Optional[str] = None,
    event_message: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> str:
    """Update an existing timeline event.

    Args:
        event_id: Timeline event ID (UUID)
        subject: New subject/title
        event_type: New event type ("system", "info", or "comment")
        event_message: New event message/description
        timestamp: New ISO 8601 timestamp

    Returns:
        JSON string with updated timeline event data
    """
    try:
        with MealieClient() as client:
            response = client.update_timeline_event(
                event_id=event_id,
                subject=subject,
                event_type=event_type,
                event_message=event_message,
                timestamp=timestamp,
            )

            # Format response
            event = {
                "id": response.get("id"),
                "recipe_id": response.get("recipeId"),
                "subject": response.get("subject"),
                "event_type": response.get("eventType"),
                "event_message": response.get("eventMessage"),
                "timestamp": response.get("timestamp"),
                "message": "Timeline event updated successfully"
            }

            return json.dumps(event, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def timeline_delete(event_id: str) -> str:
    """Delete a timeline event.

    Args:
        event_id: Timeline event ID (UUID)

    Returns:
        JSON string confirming deletion
    """
    try:
        with MealieClient() as client:
            client.delete_timeline_event(event_id)

            return json.dumps({
                "success": True,
                "message": f"Timeline event {event_id} deleted successfully"
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def timeline_update_image(
    event_id: str,
    image_url: str,
) -> str:
    """Upload or update an image for a timeline event from a URL.

    Downloads an image from the provided URL and uploads it to the specified
    timeline event. The image will be automatically resized and optimized by Mealie.

    Args:
        event_id: Timeline event ID (UUID)
        image_url: Full URL of the image to download and upload

    Returns:
        JSON string with upload confirmation or error details
    """
    try:
        import httpx

        with MealieClient() as client:
            # Download image from URL
            with httpx.Client() as http_client:
                img_response = http_client.get(image_url, follow_redirects=True)
                img_response.raise_for_status()
                image_data = img_response.content

            # Determine extension from content-type or URL
            content_type = img_response.headers.get("content-type", "")
            if "jpeg" in content_type or "jpg" in content_type:
                extension = "jpg"
            elif "png" in content_type:
                extension = "png"
            elif "webp" in content_type:
                extension = "webp"
            else:
                # Fallback to URL extension
                extension = image_url.split(".")[-1].lower()
                if extension not in ["jpg", "jpeg", "png", "webp"]:
                    extension = "jpg"  # Default

            # Upload to Mealie
            response = client.update_timeline_event_image(
                event_id=event_id,
                image_data=image_data,
                extension=extension,
            )

            return json.dumps({
                "success": True,
                "message": f"Image uploaded successfully to event {event_id}",
                "image_url": image_url,
                "extension": extension,
                "event_id": event_id
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)
