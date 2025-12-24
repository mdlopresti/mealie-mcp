"""Tests for webhooks tools."""
import json
from unittest.mock import MagicMock, patch
from src.tools.webhooks import (
    webhooks_list,
    webhooks_create,
    webhooks_get,
    webhooks_update,
    webhooks_delete,
    webhooks_test
)


def create_mock_client(
    list_value=None,
    get_value=None,
    post_value=None,
    put_value=None,
    delete_value=None,
    test_value=None
):
    """Create a mock MealieClient with configurable return values."""
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=None)

    if list_value is not None:
        mock.list_webhooks = MagicMock(return_value=list_value)
    if get_value is not None:
        mock.get_webhook = MagicMock(return_value=get_value)
    if post_value is not None:
        mock.create_webhook = MagicMock(return_value=post_value)
    if put_value is not None:
        mock.update_webhook = MagicMock(return_value=put_value)
    if delete_value is not None:
        mock.delete_webhook = MagicMock(return_value=delete_value)
    if test_value is not None:
        mock.test_webhook = MagicMock(return_value=test_value)

    return mock


class TestWebhooksList:
    """Tests for webhooks_list function."""

    def test_list_with_dict_response(self):
        """Test listing webhooks when API returns dict with items."""
        mock_data = {
            "items": [
                {
                    "id": "1",
                    "name": "Morning Notification",
                    "url": "https://example.com/webhook",
                    "enabled": True,
                    "webhookType": "mealplan",
                    "scheduledTime": "09:00:00",
                    "groupId": "group-1",
                    "householdId": "household-1"
                }
            ]
        }
        with patch('src.tools.webhooks.MealieClient', return_value=create_mock_client(list_value=mock_data)):
            result = webhooks_list()

        data = json.loads(result)
        assert data["total"] == 1
        assert len(data["webhooks"]) == 1
        assert data["webhooks"][0]["name"] == "Morning Notification"

    def test_list_with_list_response(self):
        """Test listing webhooks when API returns a list."""
        mock_data = [
            {
                "id": "1",
                "url": "https://example.com/webhook",
                "enabled": True,
                "webhookType": "mealplan",
                "scheduledTime": "09:00:00"
            }
        ]
        with patch('src.tools.webhooks.MealieClient', return_value=create_mock_client(list_value=mock_data)):
            result = webhooks_list()

        data = json.loads(result)
        assert data["total"] == 1
        assert len(data["webhooks"]) == 1

    def test_list_empty_result(self):
        """Test listing when no webhooks exist."""
        mock_data = {"items": []}
        with patch('src.tools.webhooks.MealieClient', return_value=create_mock_client(list_value=mock_data)):
            result = webhooks_list()

        data = json.loads(result)
        assert data["total"] == 0
        assert len(data["webhooks"]) == 0


class TestWebhooksCreate:
    """Tests for webhooks_create function."""

    def test_create_minimal_params(self):
        """Test creating webhook with minimal parameters."""
        mock_webhook = {
            "id": "123",
            "url": "https://example.com/webhook",
            "scheduledTime": "09:00:00",
            "enabled": True,
            "webhookType": "mealplan"
        }
        with patch('src.tools.webhooks.MealieClient', return_value=create_mock_client(post_value=mock_webhook)):
            result = webhooks_create("https://example.com/webhook", "09:00:00")

        data = json.loads(result)
        assert data["success"] is True
        assert data["message"] == "Webhook created successfully"
        assert data["webhook"]["url"] == "https://example.com/webhook"

    def test_create_with_all_params(self):
        """Test creating webhook with all parameters."""
        mock_webhook = {
            "id": "456",
            "name": "Evening Notification",
            "url": "https://api.example.com/webhook",
            "scheduledTime": "18:00:00",
            "enabled": False,
            "webhookType": "mealplan"
        }
        with patch('src.tools.webhooks.MealieClient', return_value=create_mock_client(post_value=mock_webhook)):
            result = webhooks_create(
                url="https://api.example.com/webhook",
                scheduled_time="18:00:00",
                enabled=False,
                name="Evening Notification",
                webhook_type="mealplan"
            )

        data = json.loads(result)
        assert data["success"] is True
        assert data["webhook"]["name"] == "Evening Notification"
        assert data["webhook"]["enabled"] is False


class TestWebhooksGet:
    """Tests for webhooks_get function."""

    def test_get_existing_webhook(self):
        """Test getting an existing webhook."""
        mock_webhook = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Test Webhook",
            "url": "https://example.com/webhook",
            "enabled": True,
            "webhookType": "mealplan",
            "scheduledTime": "09:00:00"
        }
        with patch('src.tools.webhooks.MealieClient', return_value=create_mock_client(get_value=mock_webhook)):
            result = webhooks_get("550e8400-e29b-41d4-a716-446655440000")

        data = json.loads(result)
        assert data["success"] is True
        assert data["webhook"]["id"] == "550e8400-e29b-41d4-a716-446655440000"


class TestWebhooksUpdate:
    """Tests for webhooks_update function."""

    def test_update_url_only(self):
        """Test updating only the URL."""
        mock_webhook = {
            "id": "123",
            "url": "https://new.example.com/webhook",
            "scheduledTime": "09:00:00",
            "enabled": True
        }
        with patch('src.tools.webhooks.MealieClient', return_value=create_mock_client(put_value=mock_webhook)):
            result = webhooks_update("123", url="https://new.example.com/webhook")

        data = json.loads(result)
        assert data["success"] is True
        assert "new.example.com" in data["webhook"]["url"]

    def test_update_scheduled_time_only(self):
        """Test updating only the scheduled time."""
        mock_webhook = {
            "id": "123",
            "url": "https://example.com/webhook",
            "scheduledTime": "18:00:00",
            "enabled": True
        }
        with patch('src.tools.webhooks.MealieClient', return_value=create_mock_client(put_value=mock_webhook)):
            result = webhooks_update("123", scheduled_time="18:00:00")

        data = json.loads(result)
        assert data["success"] is True
        assert data["webhook"]["scheduled_time"] == "18:00:00"

    def test_update_enabled_flag(self):
        """Test updating the enabled flag."""
        mock_webhook = {
            "id": "123",
            "url": "https://example.com/webhook",
            "scheduledTime": "09:00:00",
            "enabled": False
        }
        with patch('src.tools.webhooks.MealieClient', return_value=create_mock_client(put_value=mock_webhook)):
            result = webhooks_update("123", enabled=False)

        data = json.loads(result)
        assert data["success"] is True
        assert data["webhook"]["enabled"] is False

    def test_update_all_fields(self):
        """Test updating all fields at once."""
        mock_webhook = {
            "id": "123",
            "name": "Updated Webhook",
            "url": "https://updated.example.com/webhook",
            "scheduledTime": "12:00:00",
            "enabled": False,
            "webhookType": "mealplan"
        }
        with patch('src.tools.webhooks.MealieClient', return_value=create_mock_client(put_value=mock_webhook)):
            result = webhooks_update(
                "123",
                url="https://updated.example.com/webhook",
                scheduled_time="12:00:00",
                enabled=False,
                name="Updated Webhook",
                webhook_type="mealplan"
            )

        data = json.loads(result)
        assert data["success"] is True
        assert data["webhook"]["name"] == "Updated Webhook"
        assert data["webhook"]["scheduled_time"] == "12:00:00"


class TestWebhooksDelete:
    """Tests for webhooks_delete function."""

    def test_delete_existing_webhook(self):
        """Test deleting an existing webhook."""
        with patch('src.tools.webhooks.MealieClient', return_value=create_mock_client(delete_value=None)):
            result = webhooks_delete("123")

        data = json.loads(result)
        assert data["success"] is True
        assert data["message"] == "Webhook 123 deleted successfully"

    def test_delete_with_uuid(self):
        """Test deleting with UUID identifier."""
        with patch('src.tools.webhooks.MealieClient', return_value=create_mock_client(delete_value=None)):
            result = webhooks_delete("550e8400-e29b-41d4-a716-446655440000")

        data = json.loads(result)
        assert data["success"] is True


class TestWebhooksTest:
    """Tests for webhooks_test function."""

    def test_test_webhook_success(self):
        """Test sending a test webhook request."""
        mock_result = {
            "success": True,
            "message": "Test webhook sent successfully"
        }
        with patch('src.tools.webhooks.MealieClient', return_value=create_mock_client(test_value=mock_result)):
            result = webhooks_test("123")

        data = json.loads(result)
        assert data["success"] is True
        assert "successfully" in data["message"].lower()

    def test_test_webhook_with_uuid(self):
        """Test sending test webhook with UUID."""
        mock_result = {
            "success": True,
            "webhook_id": "550e8400-e29b-41d4-a716-446655440000"
        }
        with patch('src.tools.webhooks.MealieClient', return_value=create_mock_client(test_value=mock_result)):
            result = webhooks_test("550e8400-e29b-41d4-a716-446655440000")

        data = json.loads(result)
        assert data["success"] is True


class TestWebhooksErrorHandling:
    """Tests for error handling in webhooks tools."""

    def test_list_api_error(self):
        """Test handling API error when listing webhooks."""
        from src.client import MealieAPIError

        mock_client = create_mock_client()
        mock_client.list_webhooks = MagicMock(
            side_effect=MealieAPIError("API Error", 500, "Internal Server Error")
        )

        with patch('src.tools.webhooks.MealieClient', return_value=mock_client):
            result = webhooks_list()

        data = json.loads(result)
        assert "error" in data
        assert data["status_code"] == 500

    def test_create_api_error(self):
        """Test handling API error when creating webhook."""
        from src.client import MealieAPIError

        mock_client = create_mock_client()
        mock_client.create_webhook = MagicMock(
            side_effect=MealieAPIError("Invalid URL", 400, "Bad Request")
        )

        with patch('src.tools.webhooks.MealieClient', return_value=mock_client):
            result = webhooks_create("invalid-url", "09:00:00")

        data = json.loads(result)
        assert "error" in data
        assert data["status_code"] == 400

    def test_get_not_found_error(self):
        """Test handling 404 error when getting non-existent webhook."""
        from src.client import MealieAPIError

        mock_client = create_mock_client()
        mock_client.get_webhook = MagicMock(
            side_effect=MealieAPIError("Not found", 404, "Webhook not found")
        )

        with patch('src.tools.webhooks.MealieClient', return_value=mock_client):
            result = webhooks_get("nonexistent-id")

        data = json.loads(result)
        assert "error" in data
        assert data["status_code"] == 404

    def test_update_api_error(self):
        """Test handling API error when updating webhook."""
        from src.client import MealieAPIError

        mock_client = create_mock_client()
        mock_client.update_webhook = MagicMock(
            side_effect=MealieAPIError("Update failed", 500, "Server error")
        )

        with patch('src.tools.webhooks.MealieClient', return_value=mock_client):
            result = webhooks_update("123", url="https://example.com")

        data = json.loads(result)
        assert "error" in data

    def test_delete_api_error(self):
        """Test handling API error when deleting webhook."""
        from src.client import MealieAPIError

        mock_client = create_mock_client()
        mock_client.delete_webhook = MagicMock(
            side_effect=MealieAPIError("Delete failed", 403, "Forbidden")
        )

        with patch('src.tools.webhooks.MealieClient', return_value=mock_client):
            result = webhooks_delete("123")

        data = json.loads(result)
        assert "error" in data
        assert data["status_code"] == 403

    def test_test_api_error(self):
        """Test handling API error when testing webhook."""
        from src.client import MealieAPIError

        mock_client = create_mock_client()
        mock_client.test_webhook = MagicMock(
            side_effect=MealieAPIError("Test failed", 500, "Server error")
        )

        with patch('src.tools.webhooks.MealieClient', return_value=mock_client):
            result = webhooks_test("123")

        data = json.loads(result)
        assert "error" in data
        assert data["status_code"] == 500

    def test_unexpected_exception(self):
        """Test handling unexpected exception."""
        mock_client = create_mock_client()
        mock_client.list_webhooks = MagicMock(
            side_effect=RuntimeError("Unexpected error")
        )

        with patch('src.tools.webhooks.MealieClient', return_value=mock_client):
            result = webhooks_list()

        data = json.loads(result)
        assert "error" in data
        assert "Unexpected error" in data["error"]
