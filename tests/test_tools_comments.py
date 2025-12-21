"""Tests for comments tools."""
import json
from unittest.mock import MagicMock, patch
from src.tools.comments import comments_get_recipe, comments_create, comments_get, comments_update, comments_delete


def create_mock_client(get_value=None, post_value=None, put_value=None, delete_value=None):
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=None)
    if get_value:
        mock.get_recipe_comments = MagicMock(return_value=get_value)
        mock.get_comment = MagicMock(return_value=get_value)
    if post_value:
        mock.create_comment = MagicMock(return_value=post_value)
    if put_value:
        mock.update_comment = MagicMock(return_value=put_value)
    if delete_value:
        mock.delete_comment = MagicMock(return_value=delete_value)
    return mock


class TestComments:
    def test_comments_get_recipe(self):
        mock_data = [{"id": "1", "text": "Great recipe!"}]
        with patch('src.tools.comments.MealieClient', return_value=create_mock_client(get_value=mock_data)):
            result = comments_get_recipe("test-recipe")
        data = json.loads(result)
        assert data["success"] is True

    def test_comments_create(self):
        mock_data = {"id": "123", "text": "Comment"}
        with patch('src.tools.comments.MealieClient', return_value=create_mock_client(post_value=mock_data)):
            result = comments_create("recipe-1", "Comment")
        data = json.loads(result)
        assert data["success"] is True
        assert data["message"] == "Comment created successfully"

    def test_comments_get(self):
        mock_data = {"id": "123", "text": "Comment"}
        with patch('src.tools.comments.MealieClient', return_value=create_mock_client(get_value=mock_data)):
            result = comments_get("123")
        data = json.loads(result)
        assert data["success"] is True

    def test_comments_update(self):
        mock_data = {"id": "123", "text": "Updated"}
        with patch('src.tools.comments.MealieClient', return_value=create_mock_client(put_value=mock_data)):
            result = comments_update("123", "Updated")
        data = json.loads(result)
        assert data["success"] is True
        assert data["message"] == "Comment updated successfully"

    def test_comments_delete(self):
        with patch('src.tools.comments.MealieClient', return_value=create_mock_client(delete_value=None)):
            result = comments_delete("123")
        data = json.loads(result)
        assert data["success"] is True
        assert data["message"] == "Comment deleted successfully"
