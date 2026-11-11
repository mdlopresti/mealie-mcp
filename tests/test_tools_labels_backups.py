"""Tests for label, backup and food-search tools."""
import json
from unittest.mock import MagicMock, patch

from src.tools.labels import labels_list, labels_create, labels_update, labels_delete
from src.tools.backups import backups_list, backups_create, backups_get_download_url, backups_delete
from src.tools.foods import foods_list


def mock_client(**methods):
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=None)
    mock.base_url = "http://mealie.local:9000/"
    for name, value in methods.items():
        setattr(mock, name, MagicMock(return_value=value))
    return mock


class TestLabels:
    def test_list_slims_items(self):
        data = {"items": [{"id": "1", "name": "Produce", "color": "#00ff00", "groupId": "g"}], "total": 1}
        with patch("src.tools.labels.MealieClient", return_value=mock_client(list_labels=data)):
            result = json.loads(labels_list())
        assert result == {"total": 1, "labels": [{"id": "1", "name": "Produce", "color": "#00ff00"}]}

    def test_create(self):
        m = mock_client(create_label={"id": "2", "name": "Bakery", "color": "#959595"})
        with patch("src.tools.labels.MealieClient", return_value=m):
            result = json.loads(labels_create("Bakery"))
        m.create_label.assert_called_once_with(name="Bakery", color="#959595")
        assert result["success"] and result["label"]["name"] == "Bakery"

    def test_update_requires_field(self):
        assert "error" in json.loads(labels_update("1"))

    def test_update(self):
        m = mock_client(update_label={"id": "1", "name": "Bread & Salty Snacks", "color": "#959595"})
        with patch("src.tools.labels.MealieClient", return_value=m):
            result = json.loads(labels_update("1", name="Bread & Salty Snacks"))
        m.update_label.assert_called_once_with("1", name="Bread & Salty Snacks", color=None)
        assert result["label"]["name"] == "Bread & Salty Snacks"

    def test_delete(self):
        with patch("src.tools.labels.MealieClient", return_value=mock_client(delete_label=None)):
            assert json.loads(labels_delete("1"))["success"]


class TestBackups:
    def test_list(self):
        data = {"imports": [{"name": "a.zip", "date": "2026-11-11", "size": "7 MB"}], "templates": []}
        with patch("src.tools.backups.MealieClient", return_value=mock_client(list_backups=data)):
            result = json.loads(backups_list())
        assert result["total"] == 1 and result["backups"][0]["name"] == "a.zip"

    def test_create(self):
        with patch("src.tools.backups.MealieClient", return_value=mock_client(create_backup={"message": "ok"})):
            assert json.loads(backups_create())["success"]

    def test_download_url(self):
        with patch("src.tools.backups.MealieClient", return_value=mock_client(get_backup_token={"fileToken": "tok"})):
            result = json.loads(backups_get_download_url("a.zip"))
        assert result["download_url"] == "http://mealie.local:9000/api/utils/download?token=tok"

    def test_download_url_missing_token(self):
        with patch("src.tools.backups.MealieClient", return_value=mock_client(get_backup_token={})):
            assert "error" in json.loads(backups_get_download_url("a.zip"))

    def test_delete(self):
        with patch("src.tools.backups.MealieClient", return_value=mock_client(delete_backup=None)):
            assert json.loads(backups_delete("a.zip"))["success"]


class TestFoodsListSearch:
    def test_passes_filters_and_slims(self):
        data = {"page": 1, "per_page": 50, "total": 1, "total_pages": 1, "items": [{
            "id": "f1", "name": "onion", "pluralName": "onions", "aliases": [{"name": "yellow onion"}],
            "labelId": None, "label": None, "createdAt": "2026-01-03", "description": "", "extras": {},
        }]}
        m = mock_client(list_foods=data)
        with patch("src.tools.foods.MealieClient", return_value=m):
            result = json.loads(foods_list(search="onion", query_filter="labelId IS NULL", slim=True))
        m.list_foods.assert_called_once_with(1, 50, search="onion", order_by=None,
                                             order_direction=None, query_filter="labelId IS NULL")
        assert result["items"] == [{"id": "f1", "name": "onion", "pluralName": "onions",
                                    "aliases": ["yellow onion"], "labelId": None, "label": None,
                                    "createdAt": "2026-01-03"}]

    def test_full_by_default(self):
        data = {"items": [{"id": "f1", "name": "onion", "extras": {}}]}
        with patch("src.tools.foods.MealieClient", return_value=mock_client(list_foods=data)):
            assert json.loads(foods_list())["items"][0]["extras"] == {}
