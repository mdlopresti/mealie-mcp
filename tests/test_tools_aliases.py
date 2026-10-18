"""
Tests for ingredient alias management (foods and units).

Covers the alias normalization helpers, the client read-modify-write methods,
and the MCP tool wrappers.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
import respx
from httpx import Response

from src.client import MealieClient, alias_names, normalize_aliases
from src.tools.foods import (
    foods_aliases_add,
    foods_aliases_list,
    foods_aliases_remove,
    units_aliases_add,
    units_aliases_list,
    units_aliases_remove,
)


BASE_URL = "https://test.example.com"


def create_mock_client():
    """Helper to create a mocked MealieClient usable as a context manager."""
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=None)
    return mock


def food(aliases, food_id="food-1", name="green onion"):
    """Build a food payload with the given alias names."""
    return {"id": food_id, "name": name, "aliases": [{"name": a} for a in aliases]}


def unit(aliases, unit_id="unit-1", name="tablespoon"):
    """Build a unit payload with the given alias names."""
    return {"id": unit_id, "name": name, "aliases": [{"name": a} for a in aliases]}


class TestNormalizeAliases:
    """Test the alias normalization helper."""

    def test_none_and_empty_return_empty_list(self):
        assert normalize_aliases(None) == []
        assert normalize_aliases([]) == []

    def test_strings_become_name_dicts(self):
        assert normalize_aliases(["scallions"]) == [{"name": "scallions"}]

    def test_accepts_dicts(self):
        assert normalize_aliases([{"name": "scallions"}]) == [{"name": "scallions"}]

    def test_mixed_strings_and_dicts(self):
        result = normalize_aliases(["scallions", {"name": "spring onions"}])
        assert result == [{"name": "scallions"}, {"name": "spring onions"}]

    def test_whitespace_is_trimmed(self):
        assert normalize_aliases(["  scallions  "]) == [{"name": "scallions"}]

    def test_deduplicates_case_insensitively_keeping_first(self):
        result = normalize_aliases(["Scallions", "scallions", "SCALLIONS"])
        assert result == [{"name": "Scallions"}]

    def test_preserves_order(self):
        result = normalize_aliases(["b", "a", "c"])
        assert [a["name"] for a in result] == ["b", "a", "c"]

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            normalize_aliases(["  "])

    def test_bad_type_raises(self):
        with pytest.raises(ValueError, match="must be a string or a dict"):
            normalize_aliases([42])


class TestAliasNames:
    """Test extracting alias names from a food/unit object."""

    def test_extracts_names(self):
        assert alias_names(food(["scallions", "spring onions"])) == [
            "scallions", "spring onions"
        ]

    def test_missing_key_returns_empty(self):
        assert alias_names({"id": "food-1"}) == []

    def test_null_aliases_returns_empty(self):
        assert alias_names({"id": "food-1", "aliases": None}) == []

    def test_skips_malformed_entries(self):
        item = {"aliases": [{"name": "ok"}, {}, "not-a-dict", {"name": ""}]}
        assert alias_names(item) == ["ok"]


class TestFoodAliasClient:
    """Test the MealieClient food alias methods."""

    @respx.mock
    def test_get_food_aliases(self):
        respx.get(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["scallions"]))
        )

        client = MealieClient(BASE_URL, "token")

        assert client.get_food_aliases("food-1") == ["scallions"]

    @respx.mock
    def test_add_food_aliases_preserves_existing(self):
        respx.get(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["scallions"]))
        )
        put = respx.put(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["scallions", "spring onions"]))
        )

        client = MealieClient(BASE_URL, "token")
        client.add_food_aliases("food-1", ["spring onions"])

        sent = json.loads(put.calls[0].request.content)
        assert sent["aliases"] == [{"name": "scallions"}, {"name": "spring onions"}]

    @respx.mock
    def test_add_food_aliases_is_idempotent(self):
        respx.get(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["scallions"]))
        )
        put = respx.put(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["scallions"]))
        )

        client = MealieClient(BASE_URL, "token")
        client.add_food_aliases("food-1", ["SCALLIONS"])

        sent = json.loads(put.calls[0].request.content)
        assert sent["aliases"] == [{"name": "scallions"}]

    @respx.mock
    def test_remove_food_aliases_is_case_insensitive(self):
        respx.get(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["scallions", "spring onions"]))
        )
        put = respx.put(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["spring onions"]))
        )

        client = MealieClient(BASE_URL, "token")
        client.remove_food_aliases("food-1", ["SCALLIONS"])

        sent = json.loads(put.calls[0].request.content)
        assert sent["aliases"] == [{"name": "spring onions"}]

    @respx.mock
    def test_remove_unknown_alias_is_a_noop(self):
        respx.get(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["scallions"]))
        )
        put = respx.put(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["scallions"]))
        )

        client = MealieClient(BASE_URL, "token")
        client.remove_food_aliases("food-1", ["nope"])

        sent = json.loads(put.calls[0].request.content)
        assert sent["aliases"] == [{"name": "scallions"}]

    @respx.mock
    def test_invalid_aliases_are_rejected_before_any_request(self):
        get = respx.get(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["scallions"]))
        )
        client = MealieClient(BASE_URL, "token")

        with pytest.raises(ValueError, match="cannot be empty"):
            client.add_food_aliases("food-1", ["  "])
        with pytest.raises(ValueError, match="must be a string or a dict"):
            client.remove_food_aliases("food-1", [42])
        with pytest.raises(ValueError, match="cannot be empty"):
            client.update_food("food-1", aliases=[""])

        assert not get.called

    @respx.mock
    def test_update_food_replaces_aliases(self):
        respx.get(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["scallions"]))
        )
        put = respx.put(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["spring onions"]))
        )

        client = MealieClient(BASE_URL, "token")
        client.update_food("food-1", aliases=["spring onions"])

        sent = json.loads(put.calls[0].request.content)
        assert sent["aliases"] == [{"name": "spring onions"}]

    @respx.mock
    def test_update_food_with_empty_list_clears_aliases(self):
        respx.get(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["scallions"]))
        )
        put = respx.put(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food([]))
        )

        client = MealieClient(BASE_URL, "token")
        client.update_food("food-1", aliases=[])

        sent = json.loads(put.calls[0].request.content)
        assert sent["aliases"] == []

    @respx.mock
    def test_update_food_without_aliases_leaves_them_untouched(self):
        respx.get(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["scallions"]))
        )
        put = respx.put(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["scallions"], name="onion"))
        )

        client = MealieClient(BASE_URL, "token")
        client.update_food("food-1", name="onion")

        sent = json.loads(put.calls[0].request.content)
        assert sent["aliases"] == [{"name": "scallions"}]
        assert sent["name"] == "onion"

    @respx.mock
    def test_create_food_with_aliases(self):
        post = respx.post(f"{BASE_URL}/api/foods").mock(
            return_value=Response(201, json=food(["scallions"]))
        )

        client = MealieClient(BASE_URL, "token")
        client.create_food("green onion", aliases=["scallions"])

        sent = json.loads(post.calls[0].request.content)
        assert sent["aliases"] == [{"name": "scallions"}]

    @respx.mock
    def test_create_food_without_aliases_omits_the_field(self):
        post = respx.post(f"{BASE_URL}/api/foods").mock(
            return_value=Response(201, json=food([]))
        )

        client = MealieClient(BASE_URL, "token")
        client.create_food("green onion")

        assert "aliases" not in json.loads(post.calls[0].request.content)


class TestUnitAliasClient:
    """Test the MealieClient unit alias methods."""

    @respx.mock
    def test_get_unit_aliases(self):
        respx.get(f"{BASE_URL}/api/units/unit-1").mock(
            return_value=Response(200, json=unit(["tblsp"]))
        )

        client = MealieClient(BASE_URL, "token")

        assert client.get_unit_aliases("unit-1") == ["tblsp"]

    @respx.mock
    def test_add_unit_aliases_preserves_existing(self):
        respx.get(f"{BASE_URL}/api/units/unit-1").mock(
            return_value=Response(200, json=unit(["tblsp"]))
        )
        put = respx.put(f"{BASE_URL}/api/units/unit-1").mock(
            return_value=Response(200, json=unit(["tblsp", "T"]))
        )

        client = MealieClient(BASE_URL, "token")
        client.add_unit_aliases("unit-1", ["T"])

        sent = json.loads(put.calls[0].request.content)
        assert sent["aliases"] == [{"name": "tblsp"}, {"name": "T"}]

    @respx.mock
    def test_remove_unit_aliases(self):
        respx.get(f"{BASE_URL}/api/units/unit-1").mock(
            return_value=Response(200, json=unit(["tblsp", "T"]))
        )
        put = respx.put(f"{BASE_URL}/api/units/unit-1").mock(
            return_value=Response(200, json=unit(["T"]))
        )

        client = MealieClient(BASE_URL, "token")
        client.remove_unit_aliases("unit-1", ["tblsp"])

        sent = json.loads(put.calls[0].request.content)
        assert sent["aliases"] == [{"name": "T"}]

    @respx.mock
    def test_invalid_unit_aliases_are_rejected_before_any_request(self):
        get = respx.get(f"{BASE_URL}/api/units/unit-1").mock(
            return_value=Response(200, json=unit(["tblsp"]))
        )
        client = MealieClient(BASE_URL, "token")

        with pytest.raises(ValueError, match="cannot be empty"):
            client.add_unit_aliases("unit-1", ["  "])
        with pytest.raises(ValueError, match="must be a string or a dict"):
            client.remove_unit_aliases("unit-1", [None])
        with pytest.raises(ValueError, match="cannot be empty"):
            client.update_unit("unit-1", aliases=[""])

        assert not get.called

    @respx.mock
    def test_update_unit_preserves_unsent_fields(self):
        respx.get(f"{BASE_URL}/api/units/unit-1").mock(
            return_value=Response(200, json={
                "id": "unit-1",
                "name": "tablespoon",
                "abbreviation": "tbsp",
                "aliases": [{"name": "tblsp"}],
            })
        )
        put = respx.put(f"{BASE_URL}/api/units/unit-1").mock(
            return_value=Response(200, json=unit(["tblsp"]))
        )

        client = MealieClient(BASE_URL, "token")
        client.update_unit("unit-1", name="Tablespoon")

        sent = json.loads(put.calls[0].request.content)
        assert sent["name"] == "Tablespoon"
        assert sent["abbreviation"] == "tbsp"
        assert sent["aliases"] == [{"name": "tblsp"}]

    @respx.mock
    def test_create_unit_with_aliases(self):
        post = respx.post(f"{BASE_URL}/api/units").mock(
            return_value=Response(201, json=unit(["tblsp"]))
        )

        client = MealieClient(BASE_URL, "token")
        client.create_unit("tablespoon", aliases=["tblsp"])

        sent = json.loads(post.calls[0].request.content)
        assert sent["aliases"] == [{"name": "tblsp"}]


class TestFoodAliasTools:
    """Test the food alias MCP tool wrappers."""

    def test_foods_aliases_list(self):
        mock_client = create_mock_client()
        mock_client.get_food.return_value = food(["scallions"])

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            data = json.loads(foods_aliases_list("food-1"))

        assert data == {
            "food_id": "food-1",
            "name": "green onion",
            "aliases": ["scallions"],
        }

    def test_foods_aliases_add_returns_resulting_list(self):
        mock_client = create_mock_client()
        mock_client.add_food_aliases.return_value = food(["scallions", "spring onions"])

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            data = json.loads(foods_aliases_add("food-1", ["spring onions"]))

        assert data["success"] is True
        assert data["food_id"] == "food-1"
        assert data["aliases"] == ["scallions", "spring onions"]
        mock_client.add_food_aliases.assert_called_once_with("food-1", ["spring onions"])
        # The tool must not pre-fetch; the client method already reads the food
        mock_client.get_food.assert_not_called()
        mock_client.get_food_aliases.assert_not_called()

    def test_foods_aliases_remove_returns_resulting_list(self):
        mock_client = create_mock_client()
        mock_client.remove_food_aliases.return_value = food(["spring onions"])

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            data = json.loads(foods_aliases_remove("food-1", ["scallions"]))

        assert data["success"] is True
        assert data["aliases"] == ["spring onions"]
        mock_client.remove_food_aliases.assert_called_once_with("food-1", ["scallions"])
        mock_client.get_food_aliases.assert_not_called()

    @respx.mock
    def test_foods_aliases_add_makes_one_get_and_one_put(self):
        """End-to-end through the real client: exactly two HTTP requests."""
        get = respx.get(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["scallions"]))
        )
        put = respx.put(f"{BASE_URL}/api/foods/food-1").mock(
            return_value=Response(200, json=food(["scallions", "spring onions"]))
        )

        with patch('src.tools.foods.MealieClient',
                   return_value=MealieClient(BASE_URL, "token")):
            data = json.loads(foods_aliases_add("food-1", ["spring onions"]))

        assert data["success"] is True
        assert data["aliases"] == ["scallions", "spring onions"]
        assert get.call_count == 1
        assert put.call_count == 1

    def test_foods_aliases_add_surfaces_api_errors(self):
        from src.client import MealieAPIError

        mock_client = create_mock_client()
        mock_client.add_food_aliases.side_effect = MealieAPIError(
            "Not found", status_code=404, response_body="{}"
        )

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            data = json.loads(foods_aliases_add("nope", ["x"]))

        assert data["status_code"] == 404
        assert "success" not in data

    def test_foods_aliases_add_surfaces_validation_errors(self):
        mock_client = create_mock_client()
        mock_client.add_food_aliases.side_effect = ValueError("Alias names cannot be empty")

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            data = json.loads(foods_aliases_add("food-1", ["  "]))

        assert "Alias names cannot be empty" in data["error"]


class TestUnitAliasTools:
    """Test the unit alias MCP tool wrappers."""

    def test_units_aliases_list(self):
        mock_client = create_mock_client()
        mock_client.get_unit.return_value = unit(["tblsp"])

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            data = json.loads(units_aliases_list("unit-1"))

        assert data == {
            "unit_id": "unit-1",
            "name": "tablespoon",
            "aliases": ["tblsp"],
        }

    def test_units_aliases_add_returns_resulting_list(self):
        mock_client = create_mock_client()
        mock_client.add_unit_aliases.return_value = unit(["tblsp", "T"])

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            data = json.loads(units_aliases_add("unit-1", ["T"]))

        assert data["success"] is True
        assert data["unit_id"] == "unit-1"
        assert data["aliases"] == ["tblsp", "T"]
        mock_client.get_unit_aliases.assert_not_called()

    def test_units_aliases_remove_returns_resulting_list(self):
        mock_client = create_mock_client()
        mock_client.remove_unit_aliases.return_value = unit(["T"])

        with patch('src.tools.foods.MealieClient', return_value=mock_client):
            data = json.loads(units_aliases_remove("unit-1", ["tblsp"]))

        assert data["success"] is True
        assert data["aliases"] == ["T"]
        mock_client.get_unit_aliases.assert_not_called()

    @respx.mock
    def test_units_aliases_remove_makes_one_get_and_one_put(self):
        """End-to-end through the real client: exactly two HTTP requests."""
        get = respx.get(f"{BASE_URL}/api/units/unit-1").mock(
            return_value=Response(200, json=unit(["tblsp", "T"]))
        )
        put = respx.put(f"{BASE_URL}/api/units/unit-1").mock(
            return_value=Response(200, json=unit(["T"]))
        )

        with patch('src.tools.foods.MealieClient',
                   return_value=MealieClient(BASE_URL, "token")):
            data = json.loads(units_aliases_remove("unit-1", ["tblsp"]))

        assert data["success"] is True
        assert data["aliases"] == ["T"]
        assert get.call_count == 1
        assert put.call_count == 1
