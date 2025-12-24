"""Tests for recipe actions tools."""
import json
from unittest.mock import MagicMock, patch
from src.tools.recipe_actions import (
    recipe_actions_list,
    recipe_actions_create,
    recipe_actions_get,
    recipe_actions_update,
    recipe_actions_delete,
    recipe_actions_trigger
)


def create_mock_client(
    list_value=None,
    get_value=None,
    post_value=None,
    put_value=None,
    delete_value=None,
    trigger_value=None
):
    """Create a mock MealieClient with configurable return values."""
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=None)

    if list_value is not None:
        mock.list_recipe_actions = MagicMock(return_value=list_value)
    if get_value is not None:
        mock.get_recipe_action = MagicMock(return_value=get_value)
    if post_value is not None:
        mock.create_recipe_action = MagicMock(return_value=post_value)
    if put_value is not None:
        mock.update_recipe_action = MagicMock(return_value=put_value)
    if delete_value is not None:
        mock.delete_recipe_action = MagicMock(return_value=delete_value)
    if trigger_value is not None:
        mock.trigger_recipe_action = MagicMock(return_value=trigger_value)

    return mock


class TestRecipeActionsList:
    """Tests for recipe_actions_list function."""

    def test_list_default_params(self):
        """Test listing recipe actions with default parameters."""
        mock_data = {
            "items": [
                {"id": "1", "type": "link", "title": "Open in App"},
                {"id": "2", "type": "post", "title": "Send Webhook"}
            ],
            "total": 2,
            "page": 1,
            "per_page": 50
        }
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(list_value=mock_data)):
            result = recipe_actions_list()

        data = json.loads(result)
        assert data["success"] is True
        assert "actions" in data
        assert len(data["actions"]["items"]) == 2

    def test_list_with_pagination(self):
        """Test listing recipe actions with custom pagination."""
        mock_data = {
            "items": [{"id": "1", "type": "link", "title": "Test"}],
            "total": 100,
            "page": 2,
            "per_page": 10
        }
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(list_value=mock_data)):
            result = recipe_actions_list(page=2, per_page=10)

        data = json.loads(result)
        assert data["success"] is True

    def test_list_with_ordering(self):
        """Test listing recipe actions with ordering."""
        mock_data = {
            "items": [{"id": "1", "type": "link", "title": "Action A"}],
            "total": 1,
            "page": 1,
            "per_page": 50
        }
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(list_value=mock_data)):
            result = recipe_actions_list(order_by="title", order_direction="asc")

        data = json.loads(result)
        assert data["success"] is True

    def test_list_empty_result(self):
        """Test listing when no recipe actions exist."""
        mock_data = {"items": [], "total": 0, "page": 1, "per_page": 50}
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(list_value=mock_data)):
            result = recipe_actions_list()

        data = json.loads(result)
        assert data["success"] is True
        assert len(data["actions"]["items"]) == 0


class TestRecipeActionsCreate:
    """Tests for recipe_actions_create function."""

    def test_create_link_action(self):
        """Test creating a link-type action."""
        mock_action = {
            "id": "123",
            "type": "link",
            "title": "Open in App",
            "url": "myapp://recipe/"
        }
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(post_value=mock_action)):
            result = recipe_actions_create("link", "Open in App", "myapp://recipe/")

        data = json.loads(result)
        assert data["success"] is True
        assert data["message"] == "Recipe action created successfully"
        assert data["action"]["type"] == "link"
        assert data["action"]["title"] == "Open in App"

    def test_create_post_action(self):
        """Test creating a post-type (webhook) action."""
        mock_action = {
            "id": "456",
            "type": "post",
            "title": "Send to Service",
            "url": "https://api.example.com/webhook"
        }
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(post_value=mock_action)):
            result = recipe_actions_create("post", "Send to Service", "https://api.example.com/webhook")

        data = json.loads(result)
        assert data["success"] is True
        assert data["action"]["type"] == "post"
        assert "webhook" in data["action"]["url"]

    def test_create_with_special_characters_in_title(self):
        """Test creating action with special characters in title."""
        mock_action = {
            "id": "789",
            "type": "link",
            "title": "Recipe → App (β)",
            "url": "custom://open"
        }
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(post_value=mock_action)):
            result = recipe_actions_create("link", "Recipe → App (β)", "custom://open")

        data = json.loads(result)
        assert data["success"] is True


class TestRecipeActionsGet:
    """Tests for recipe_actions_get function."""

    def test_get_existing_action(self):
        """Test getting an existing recipe action."""
        mock_action = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "type": "link",
            "title": "Open in App",
            "url": "myapp://recipe/"
        }
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(get_value=mock_action)):
            result = recipe_actions_get("550e8400-e29b-41d4-a716-446655440000")

        data = json.loads(result)
        assert data["success"] is True
        assert data["action"]["id"] == "550e8400-e29b-41d4-a716-446655440000"

    def test_get_with_uuid_validation(self):
        """Test get with properly formatted UUID."""
        mock_action = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "type": "post",
            "title": "Webhook Action",
            "url": "https://example.com"
        }
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(get_value=mock_action)):
            result = recipe_actions_get("123e4567-e89b-12d3-a456-426614174000")

        data = json.loads(result)
        assert data["success"] is True


class TestRecipeActionsUpdate:
    """Tests for recipe_actions_update function."""

    def test_update_title_only(self):
        """Test updating only the title."""
        mock_action = {
            "id": "123",
            "type": "link",
            "title": "New Title",
            "url": "myapp://recipe/"
        }
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(put_value=mock_action)):
            result = recipe_actions_update("123", title="New Title")

        data = json.loads(result)
        assert data["success"] is True
        assert data["message"] == "Recipe action updated successfully"
        assert data["action"]["title"] == "New Title"

    def test_update_url_only(self):
        """Test updating only the URL."""
        mock_action = {
            "id": "123",
            "type": "post",
            "title": "Send Webhook",
            "url": "https://new.example.com/webhook"
        }
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(put_value=mock_action)):
            result = recipe_actions_update("123", url="https://new.example.com/webhook")

        data = json.loads(result)
        assert data["success"] is True
        assert "new.example.com" in data["action"]["url"]

    def test_update_action_type(self):
        """Test updating the action type."""
        mock_action = {
            "id": "123",
            "type": "post",
            "title": "Action",
            "url": "https://example.com"
        }
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(put_value=mock_action)):
            result = recipe_actions_update("123", action_type="post")

        data = json.loads(result)
        assert data["success"] is True
        assert data["action"]["type"] == "post"

    def test_update_all_fields(self):
        """Test updating all fields at once."""
        mock_action = {
            "id": "123",
            "type": "link",
            "title": "Updated Title",
            "url": "newapp://recipe/"
        }
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(put_value=mock_action)):
            result = recipe_actions_update(
                "123",
                action_type="link",
                title="Updated Title",
                url="newapp://recipe/"
            )

        data = json.loads(result)
        assert data["success"] is True
        assert data["action"]["type"] == "link"
        assert data["action"]["title"] == "Updated Title"


class TestRecipeActionsDelete:
    """Tests for recipe_actions_delete function."""

    def test_delete_existing_action(self):
        """Test deleting an existing recipe action."""
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(delete_value=None)):
            result = recipe_actions_delete("123")

        data = json.loads(result)
        assert data["success"] is True
        assert data["message"] == "Recipe action deleted successfully"

    def test_delete_with_uuid(self):
        """Test deleting with UUID identifier."""
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(delete_value=None)):
            result = recipe_actions_delete("550e8400-e29b-41d4-a716-446655440000")

        data = json.loads(result)
        assert data["success"] is True


class TestRecipeActionsTrigger:
    """Tests for recipe_actions_trigger function."""

    def test_trigger_link_action(self):
        """Test triggering a link-type action."""
        mock_result = {
            "url": "myapp://recipe/sous-vide-salmon",
            "type": "link"
        }
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(trigger_value=mock_result)):
            result = recipe_actions_trigger("123", "sous-vide-salmon")

        data = json.loads(result)
        assert data["success"] is True
        assert data["message"] == "Recipe action triggered successfully"
        assert "sous-vide-salmon" in data["result"]["url"]

    def test_trigger_post_action(self):
        """Test triggering a post-type (webhook) action."""
        mock_result = {
            "status": "sent",
            "response_code": 200,
            "type": "post"
        }
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(trigger_value=mock_result)):
            result = recipe_actions_trigger("456", "chicken-recipe")

        data = json.loads(result)
        assert data["success"] is True
        assert data["result"]["status"] == "sent"
        assert data["result"]["response_code"] == 200

    def test_trigger_with_special_recipe_slug(self):
        """Test triggering with recipe slug containing special characters."""
        mock_result = {
            "url": "myapp://recipe/sous-vide-pork-tenderloin-2024",
            "type": "link"
        }
        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(trigger_value=mock_result)):
            result = recipe_actions_trigger("123", "sous-vide-pork-tenderloin-2024")

        data = json.loads(result)
        assert data["success"] is True
        assert "pork-tenderloin" in data["result"]["url"]

    def test_trigger_multiple_times(self):
        """Test triggering the same action multiple times."""
        mock_result = {"url": "myapp://recipe/test", "type": "link"}

        with patch('src.tools.recipe_actions.MealieClient', return_value=create_mock_client(trigger_value=mock_result)):
            result1 = recipe_actions_trigger("123", "recipe-1")
            result2 = recipe_actions_trigger("123", "recipe-2")

        data1 = json.loads(result1)
        data2 = json.loads(result2)
        assert data1["success"] is True
        assert data2["success"] is True


class TestRecipeActionsErrorHandling:
    """Tests for error handling in recipe actions tools."""

    def test_list_api_error(self):
        """Test handling API error when listing actions."""
        from src.client import MealieAPIError

        mock_client = create_mock_client()
        mock_client.list_recipe_actions = MagicMock(
            side_effect=MealieAPIError("API Error", 500, "Internal Server Error")
        )

        with patch('src.tools.recipe_actions.MealieClient', return_value=mock_client):
            result = recipe_actions_list()

        data = json.loads(result)
        assert "error" in data
        assert data["status_code"] == 500

    def test_create_api_error(self):
        """Test handling API error when creating action."""
        from src.client import MealieAPIError

        mock_client = create_mock_client()
        mock_client.create_recipe_action = MagicMock(
            side_effect=MealieAPIError("Invalid action type", 400, "Bad Request")
        )

        with patch('src.tools.recipe_actions.MealieClient', return_value=mock_client):
            result = recipe_actions_create("invalid", "Title", "url")

        data = json.loads(result)
        assert "error" in data
        assert data["status_code"] == 400

    def test_get_not_found_error(self):
        """Test handling 404 error when getting non-existent action."""
        from src.client import MealieAPIError

        mock_client = create_mock_client()
        mock_client.get_recipe_action = MagicMock(
            side_effect=MealieAPIError("Not found", 404, "Action not found")
        )

        with patch('src.tools.recipe_actions.MealieClient', return_value=mock_client):
            result = recipe_actions_get("nonexistent-id")

        data = json.loads(result)
        assert "error" in data
        assert data["status_code"] == 404

    def test_update_api_error(self):
        """Test handling API error when updating action."""
        from src.client import MealieAPIError

        mock_client = create_mock_client()
        mock_client.update_recipe_action = MagicMock(
            side_effect=MealieAPIError("Update failed", 500, "Server error")
        )

        with patch('src.tools.recipe_actions.MealieClient', return_value=mock_client):
            result = recipe_actions_update("123", title="New")

        data = json.loads(result)
        assert "error" in data

    def test_delete_api_error(self):
        """Test handling API error when deleting action."""
        from src.client import MealieAPIError

        mock_client = create_mock_client()
        mock_client.delete_recipe_action = MagicMock(
            side_effect=MealieAPIError("Delete failed", 403, "Forbidden")
        )

        with patch('src.tools.recipe_actions.MealieClient', return_value=mock_client):
            result = recipe_actions_delete("123")

        data = json.loads(result)
        assert "error" in data
        assert data["status_code"] == 403

    def test_trigger_api_error(self):
        """Test handling API error when triggering action."""
        from src.client import MealieAPIError

        mock_client = create_mock_client()
        mock_client.trigger_recipe_action = MagicMock(
            side_effect=MealieAPIError("Trigger failed", 500, "Webhook error")
        )

        with patch('src.tools.recipe_actions.MealieClient', return_value=mock_client):
            result = recipe_actions_trigger("123", "recipe-slug")

        data = json.loads(result)
        assert "error" in data
        assert data["status_code"] == 500

    def test_unexpected_exception(self):
        """Test handling unexpected exception."""
        mock_client = create_mock_client()
        mock_client.list_recipe_actions = MagicMock(
            side_effect=RuntimeError("Unexpected error")
        )

        with patch('src.tools.recipe_actions.MealieClient', return_value=mock_client):
            result = recipe_actions_list()

        data = json.loads(result)
        assert "error" in data
        assert "Unexpected error" in data["error"]
