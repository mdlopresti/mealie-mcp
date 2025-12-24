"""Tests for event notifications tools."""
import json
import pytest
from unittest.mock import MagicMock, patch
from src.tools.notifications import (
    notifications_list,
    notifications_create,
    notifications_get,
    notifications_update,
    notifications_delete,
    notifications_test,
)
from src.client import MealieAPIError


def create_mock_client(list_value=None, create_value=None, get_value=None, 
                       update_value=None, delete_value=None, test_value=None, error=None):
    """Create a mock MealieClient for testing."""
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=None)
    
    if error:
        mock.list_notifications = MagicMock(side_effect=error)
        mock.create_notification = MagicMock(side_effect=error)
        mock.get_notification = MagicMock(side_effect=error)
        mock.update_notification = MagicMock(side_effect=error)
        mock.delete_notification = MagicMock(side_effect=error)
        mock.test_notification = MagicMock(side_effect=error)
    else:
        if list_value is not None:
            mock.list_notifications = MagicMock(return_value=list_value)
        if create_value is not None:
            mock.create_notification = MagicMock(return_value=create_value)
        if get_value is not None:
            mock.get_notification = MagicMock(return_value=get_value)
        if update_value is not None:
            mock.update_notification = MagicMock(return_value=update_value)
        if delete_value is not None:
            mock.delete_notification = MagicMock(return_value=delete_value)
        if test_value is not None:
            mock.test_notification = MagicMock(return_value=test_value)
    
    return mock


class TestNotificationsList:
    """Tests for notifications_list function."""
    
    def test_list_empty(self):
        """Test listing notifications when none exist."""
        mock_data = []
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(list_value=mock_data)):
            result = notifications_list()
        data = json.loads(result)
        assert data["total"] == 0
        assert data["notifications"] == []
    
    def test_list_single(self):
        """Test listing a single notification."""
        mock_data = [{"id": "id-1", "name": "Test", "enabled": True, "groupId": "g1", "householdId": "h1", "options": {}}]
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(list_value=mock_data)):
            result = notifications_list()
        data = json.loads(result)
        assert data["total"] == 1
    
    def test_list_multiple(self):
        """Test listing multiple notifications."""
        mock_data = [
            {"id": "id-1", "name": "Discord", "enabled": True, "groupId": "g1", "householdId": "h1", "options": {}},
            {"id": "id-2", "name": "Email", "enabled": False, "groupId": "g1", "householdId": "h1", "options": {}}
        ]
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(list_value=mock_data)):
            result = notifications_list()
        data = json.loads(result)
        assert data["total"] == 2
    
    def test_list_error(self):
        """Test list handling errors."""
        error = MealieAPIError("Error", status_code=500, response_body="Error")
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(error=error)):
            result = notifications_list()
        data = json.loads(result)
        assert "error" in data


class TestNotificationsCreate:
    """Tests for notifications_create function."""
    
    def test_create_minimal(self):
        """Test creating notification with minimal params."""
        mock_data = {"id": "id-1", "name": "Test", "enabled": True, "groupId": "g1", "householdId": "h1", "options": {}}
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(create_value=mock_data)):
            result = notifications_create(name="Test")
        data = json.loads(result)
        assert data["name"] == "Test"
        assert data["message"] == "Notification created successfully"
    
    def test_create_with_apprise_url(self):
        """Test creating with Apprise URL."""
        mock_data = {"id": "id-1", "name": "Discord", "enabled": True, "groupId": "g1", "householdId": "h1", "options": {}}
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(create_value=mock_data)):
            result = notifications_create(name="Discord", apprise_url="discord://test")
        data = json.loads(result)
        assert data["name"] == "Discord"
    
    def test_create_with_options(self):
        """Test creating with event options."""
        mock_data = {"id": "id-1", "name": "Test", "enabled": True, "groupId": "g1", "householdId": "h1", 
                     "options": {"mealplanEntryCreated": True}}
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(create_value=mock_data)):
            result = notifications_create(name="Test", options={"mealplanEntryCreated": True})
        data = json.loads(result)
        assert data["options"]["mealplanEntryCreated"] is True
    
    def test_create_disabled(self):
        """Test creating disabled notification."""
        mock_data = {"id": "id-1", "name": "Test", "enabled": False, "groupId": "g1", "householdId": "h1", "options": {}}
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(create_value=mock_data)):
            result = notifications_create(name="Test", enabled=False)
        data = json.loads(result)
        assert data["enabled"] is False
    
    def test_create_error(self):
        """Test create handling errors."""
        error = MealieAPIError("Error", status_code=400, response_body="Error")
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(error=error)):
            result = notifications_create(name="Test")
        data = json.loads(result)
        assert "error" in data


class TestNotificationsGet:
    """Tests for notifications_get function."""
    
    def test_get_success(self):
        """Test getting notification by ID."""
        mock_data = {"id": "id-1", "name": "Test", "enabled": True, "groupId": "g1", "householdId": "h1", "options": {}}
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(get_value=mock_data)):
            result = notifications_get("id-1")
        data = json.loads(result)
        assert data["id"] == "id-1"
    
    def test_get_not_found(self):
        """Test getting non-existent notification."""
        error = MealieAPIError("Not found", status_code=404, response_body="Not found")
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(error=error)):
            result = notifications_get("invalid")
        data = json.loads(result)
        assert "error" in data
        assert data["status_code"] == 404


class TestNotificationsUpdate:
    """Tests for notifications_update function."""
    
    def test_update_name(self):
        """Test updating notification name."""
        mock_data = {"id": "id-1", "name": "Updated", "enabled": True, "groupId": "g1", "householdId": "h1", "options": {}}
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(update_value=mock_data)):
            result = notifications_update("id-1", name="Updated")
        data = json.loads(result)
        assert data["name"] == "Updated"
        assert data["message"] == "Notification updated successfully"
    
    def test_update_enabled(self):
        """Test toggling enabled status."""
        mock_data = {"id": "id-1", "name": "Test", "enabled": False, "groupId": "g1", "householdId": "h1", "options": {}}
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(update_value=mock_data)):
            result = notifications_update("id-1", enabled=False)
        data = json.loads(result)
        assert data["enabled"] is False
    
    def test_update_options(self):
        """Test updating event options."""
        mock_data = {"id": "id-1", "name": "Test", "enabled": True, "groupId": "g1", "householdId": "h1",
                     "options": {"recipeCreated": True}}
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(update_value=mock_data)):
            result = notifications_update("id-1", options={"recipeCreated": True})
        data = json.loads(result)
        assert data["options"]["recipeCreated"] is True
    
    def test_update_apprise_url(self):
        """Test updating Apprise URL."""
        mock_data = {"id": "id-1", "name": "Test", "enabled": True, "groupId": "g1", "householdId": "h1", "options": {}}
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(update_value=mock_data)):
            result = notifications_update("id-1", apprise_url="slack://test")
        data = json.loads(result)
        assert data["id"] == "id-1"
    
    def test_update_error(self):
        """Test update handling errors."""
        error = MealieAPIError("Error", status_code=404, response_body="Not found")
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(error=error)):
            result = notifications_update("invalid", name="Test")
        data = json.loads(result)
        assert "error" in data


class TestNotificationsDelete:
    """Tests for notifications_delete function."""
    
    def test_delete_success(self):
        """Test deleting notification."""
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(delete_value=None)):
            result = notifications_delete("id-1")
        data = json.loads(result)
        assert data["success"] is True
        assert "deleted successfully" in data["message"]
    
    def test_delete_not_found(self):
        """Test deleting non-existent notification."""
        error = MealieAPIError("Not found", status_code=404, response_body="Not found")
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(error=error)):
            result = notifications_delete("invalid")
        data = json.loads(result)
        assert "error" in data


class TestNotificationsTest:
    """Tests for notifications_test function."""
    
    def test_test_success(self):
        """Test sending test notification."""
        mock_data = {"status": "sent"}
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(test_value=mock_data)):
            result = notifications_test("id-1")
        data = json.loads(result)
        assert data["success"] is True
        assert "Test notification sent successfully" in data["message"]
    
    def test_test_invalid_config(self):
        """Test with invalid Apprise config."""
        error = MealieAPIError("Invalid URL", status_code=400, response_body="Bad request")
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(error=error)):
            result = notifications_test("id-1")
        data = json.loads(result)
        assert "error" in data
    
    def test_test_not_found(self):
        """Test with non-existent notification."""
        error = MealieAPIError("Not found", status_code=404, response_body="Not found")
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(error=error)):
            result = notifications_test("invalid")
        data = json.loads(result)
        assert "error" in data


class TestNotificationsEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_create_all_event_types(self):
        """Test creating with all event types."""
        all_events = {
            "testMessage": True,
            "recipeCreated": True,
            "mealplanEntryCreated": True,
            "shoppingListCreated": True,
        }
        mock_data = {"id": "id-1", "name": "All", "enabled": True, "groupId": "g1", "householdId": "h1", "options": all_events}
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(create_value=mock_data)):
            result = notifications_create(name="All", options=all_events)
        data = json.loads(result)
        assert data["options"]["recipeCreated"] is True
    
    def test_unexpected_error(self):
        """Test handling unexpected exceptions."""
        error = Exception("Unexpected")
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(error=error)):
            result = notifications_list()
        data = json.loads(result)
        assert "error" in data


class TestNotificationsIntegration:
    """Integration tests covering multiple notification operations."""
    
    def test_create_get_update_workflow(self):
        """Test full workflow: create -> get -> update."""
        create_data = {"id": "id-1", "name": "Workflow Test", "enabled": True, "groupId": "g1", "householdId": "h1", "options": {}}
        update_data = {"id": "id-1", "name": "Updated Workflow", "enabled": False, "groupId": "g1", "householdId": "h1", "options": {"testMessage": True}}
        
        # Create
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(create_value=create_data)):
            create_result = notifications_create(name="Workflow Test")
        create_json = json.loads(create_result)
        assert create_json["name"] == "Workflow Test"
        
        # Get
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(get_value=create_data)):
            get_result = notifications_get("id-1")
        get_json = json.loads(get_result)
        assert get_json["id"] == "id-1"
        
        # Update
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(update_value=update_data)):
            update_result = notifications_update("id-1", name="Updated Workflow", enabled=False, options={"testMessage": True})
        update_json = json.loads(update_result)
        assert update_json["name"] == "Updated Workflow"
        assert update_json["enabled"] is False
    
    def test_create_test_delete_workflow(self):
        """Test workflow: create -> test -> delete."""
        create_data = {"id": "id-1", "name": "Test Workflow", "enabled": True, "groupId": "g1", "householdId": "h1", "options": {}}
        test_data = {"status": "sent"}
        
        # Create
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(create_value=create_data)):
            create_result = notifications_create(name="Test Workflow", apprise_url="discord://test")
        create_json = json.loads(create_result)
        assert create_json["id"] == "id-1"
        
        # Test
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(test_value=test_data)):
            test_result = notifications_test("id-1")
        test_json = json.loads(test_result)
        assert test_json["success"] is True
        
        # Delete
        with patch("src.tools.notifications.MealieClient", return_value=create_mock_client(delete_value=None)):
            delete_result = notifications_delete("id-1")
        delete_json = json.loads(delete_result)
        assert delete_json["success"] is True
