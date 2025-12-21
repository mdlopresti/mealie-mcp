"""
Simplified tests for timeline tools focusing on code coverage.
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from src.tools.timeline import (
    timeline_list,
    timeline_get,
    timeline_create,
    timeline_update,
    timeline_delete,
    timeline_update_image,
)


def create_mock_client(get_value=None, post_value=None, put_value=None, delete_value=None):
    """Helper to create a mocked MealieClient."""
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=None)
    if get_value is not None:
        mock.get.return_value = get_value
        mock.list_timeline_events = MagicMock(return_value=get_value)
        mock.get_timeline_event = MagicMock(return_value=get_value)
    if post_value is not None:
        mock.post.return_value = post_value
        mock.create_timeline_event = MagicMock(return_value=post_value)
    if put_value is not None:
        mock.put.return_value = put_value
        mock.update_timeline_event = MagicMock(return_value=put_value)
        mock.update_timeline_event_image = MagicMock(return_value=put_value)
    if delete_value is not None:
        mock.delete.return_value = delete_value
        mock.delete_timeline_event = MagicMock(return_value=delete_value)
    return mock


class TestTimeline:
    """Test timeline operations."""

    def test_timeline_list(self):
        """Test listing timeline events."""
        mock_response = {
            "items": [
                {
                    "id": "event-1",
                    "recipeId": "recipe-1",
                    "userId": "user-1",
                    "subject": "Made this recipe",
                    "eventType": "info",
                    "eventMessage": "Turned out great!",
                    "timestamp": "2025-01-15T18:00:00Z",
                    "image": "has image"
                }
            ],
            "page": 1,
            "perPage": 50,
            "total": 1,
            "totalPages": 1
        }
        mock_client = create_mock_client(get_value=mock_response)

        with patch('src.tools.timeline.MealieClient', return_value=mock_client):
            result = timeline_list()

        data = json.loads(result)
        assert isinstance(data, dict)
        assert "events" in data
        assert len(data["events"]) == 1

    def test_timeline_list_with_filters(self):
        """Test listing timeline events with filters."""
        mock_response = {"items": [], "page": 1, "perPage": 20, "total": 0, "totalPages": 0}
        mock_client = create_mock_client(get_value=mock_response)

        with patch('src.tools.timeline.MealieClient', return_value=mock_client):
            result = timeline_list(page=2, per_page=20, order_by="timestamp", order_direction="desc")

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_timeline_get(self):
        """Test getting a timeline event."""
        mock_response = {
            "id": "event-1",
            "recipeId": "recipe-1",
            "userId": "user-1",
            "groupId": "group-1",
            "householdId": "household-1",
            "subject": "Made this recipe",
            "eventType": "info",
            "eventMessage": "Turned out great!",
            "timestamp": "2025-01-15T18:00:00Z",
            "image": "has image",
            "createdAt": "2025-01-15T18:00:00Z",
            "updateAt": "2025-01-15T18:00:00Z"
        }
        mock_client = create_mock_client(get_value=mock_response)

        with patch('src.tools.timeline.MealieClient', return_value=mock_client):
            result = timeline_get("event-1")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["id"] == "event-1"
        assert data["has_image"] is True

    def test_timeline_create(self):
        """Test creating a timeline event."""
        mock_response = {
            "id": "new-event",
            "recipeId": "recipe-1",
            "subject": "Made this today",
            "eventType": "info",
            "eventMessage": None,
            "timestamp": "2025-01-20T12:00:00Z"
        }
        mock_client = create_mock_client(post_value=mock_response)

        with patch('src.tools.timeline.MealieClient', return_value=mock_client):
            result = timeline_create(recipe_id="recipe-1", subject="Made this today")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["id"] == "new-event"
        assert "message" in data

    def test_timeline_create_full(self):
        """Test creating a timeline event with all fields."""
        mock_response = {
            "id": "new-event",
            "recipeId": "recipe-1",
            "subject": "Made this today",
            "eventType": "comment",
            "eventMessage": "Delicious!",
            "timestamp": "2025-01-20T12:00:00Z"
        }
        mock_client = create_mock_client(post_value=mock_response)

        with patch('src.tools.timeline.MealieClient', return_value=mock_client):
            result = timeline_create(
                recipe_id="recipe-1",
                subject="Made this today",
                event_type="comment",
                event_message="Delicious!",
                user_id="user-1",
                timestamp="2025-01-20T12:00:00Z"
            )

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["event_type"] == "comment"

    def test_timeline_update(self):
        """Test updating a timeline event."""
        mock_response = {
            "id": "event-1",
            "recipeId": "recipe-1",
            "subject": "Updated subject",
            "eventType": "info",
            "eventMessage": "Updated message",
            "timestamp": "2025-01-20T12:00:00Z"
        }
        mock_client = create_mock_client(put_value=mock_response)

        with patch('src.tools.timeline.MealieClient', return_value=mock_client):
            result = timeline_update(event_id="event-1", subject="Updated subject")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["subject"] == "Updated subject"
        assert "message" in data

    def test_timeline_update_multiple_fields(self):
        """Test updating multiple fields of a timeline event."""
        mock_response = {
            "id": "event-1",
            "recipeId": "recipe-1",
            "subject": "Updated subject",
            "eventType": "comment",
            "eventMessage": "Updated message",
            "timestamp": "2025-01-21T12:00:00Z"
        }
        mock_client = create_mock_client(put_value=mock_response)

        with patch('src.tools.timeline.MealieClient', return_value=mock_client):
            result = timeline_update(
                event_id="event-1",
                subject="Updated subject",
                event_type="comment",
                event_message="Updated message",
                timestamp="2025-01-21T12:00:00Z"
            )

        data = json.loads(result)
        assert isinstance(data, dict)

    def test_timeline_delete(self):
        """Test deleting a timeline event."""
        mock_client = create_mock_client(delete_value=None)

        with patch('src.tools.timeline.MealieClient', return_value=mock_client):
            result = timeline_delete("event-1")

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["success"] is True

    def test_timeline_update_image(self):
        """Test updating timeline event image."""
        mock_response = {
            "id": "event-1",
            "image": "has image"
        }
        mock_client = create_mock_client(put_value=mock_response)

        # Mock httpx client for image download
        mock_http_response = MagicMock()
        mock_http_response.content = b"fake image data"
        mock_http_response.headers = {"content-type": "image/jpeg"}
        mock_http_response.raise_for_status = MagicMock()

        mock_http_client = MagicMock()
        mock_http_client.__enter__ = MagicMock(return_value=mock_http_client)
        mock_http_client.__exit__ = MagicMock(return_value=None)
        mock_http_client.get = MagicMock(return_value=mock_http_response)

        with patch('src.tools.timeline.MealieClient', return_value=mock_client):
            with patch('httpx.Client', return_value=mock_http_client):
                result = timeline_update_image(
                    event_id="event-1",
                    image_url="https://example.com/image.jpg"
                )

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["success"] is True

    def test_timeline_update_image_png(self):
        """Test updating timeline event image with PNG."""
        mock_response = {"id": "event-1"}
        mock_client = create_mock_client(put_value=mock_response)

        mock_http_response = MagicMock()
        mock_http_response.content = b"fake png data"
        mock_http_response.headers = {"content-type": "image/png"}
        mock_http_response.raise_for_status = MagicMock()

        mock_http_client = MagicMock()
        mock_http_client.__enter__ = MagicMock(return_value=mock_http_client)
        mock_http_client.__exit__ = MagicMock(return_value=None)
        mock_http_client.get = MagicMock(return_value=mock_http_response)

        with patch('src.tools.timeline.MealieClient', return_value=mock_client):
            with patch('httpx.Client', return_value=mock_http_client):
                result = timeline_update_image(
                    event_id="event-1",
                    image_url="https://example.com/image.png"
                )

        data = json.loads(result)
        assert data["extension"] == "png"

    def test_timeline_update_image_unknown_type(self):
        """Test updating timeline event image with unknown type."""
        mock_response = {"id": "event-1"}
        mock_client = create_mock_client(put_value=mock_response)

        mock_http_response = MagicMock()
        mock_http_response.content = b"fake data"
        mock_http_response.headers = {"content-type": "application/octet-stream"}
        mock_http_response.raise_for_status = MagicMock()

        mock_http_client = MagicMock()
        mock_http_client.__enter__ = MagicMock(return_value=mock_http_client)
        mock_http_client.__exit__ = MagicMock(return_value=None)
        mock_http_client.get = MagicMock(return_value=mock_http_response)

        with patch('src.tools.timeline.MealieClient', return_value=mock_client):
            with patch('httpx.Client', return_value=mock_http_client):
                result = timeline_update_image(
                    event_id="event-1",
                    image_url="https://example.com/image.xyz"
                )

        data = json.loads(result)
        # Should default to jpg
        assert data["extension"] == "xyz" or data["extension"] == "jpg"


class TestTimelineErrorHandling:
    """Test error handling in timeline operations."""

    def test_timeline_list_api_error(self):
        """Test timeline list with API error."""
        from src.client import MealieAPIError

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(side_effect=MealieAPIError("API Error", 500, "Server error"))
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch('src.tools.timeline.MealieClient', return_value=mock_client):
            result = timeline_list()

        data = json.loads(result)
        assert "error" in data

    def test_timeline_create_generic_error(self):
        """Test timeline create with generic error."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(side_effect=ValueError("Invalid value"))
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch('src.tools.timeline.MealieClient', return_value=mock_client):
            result = timeline_create(recipe_id="recipe-1", subject="Test")

        data = json.loads(result)
        assert "error" in data
        assert "Unexpected error" in data["error"]
