"""Tests for the FORK extended tools (generic API, reparse, audit, images, tools, patch)."""
import json
from unittest.mock import MagicMock, patch

import respx
from httpx import Response

from src.tools import extended
from src.tools.extended import (
    api_request,
    find_image_on_page,
    recipes_audit,
    recipes_fill_missing_images,
    recipes_patch,
    recipes_reparse,
    recipes_set_tools,
    _servings_from_yield,
)


def mock_client(get=None, post=None, put=None):
    m = MagicMock()
    m.__enter__ = MagicMock(return_value=m)
    m.__exit__ = MagicMock(return_value=None)
    m.base_url = "http://mealie"
    m.get = MagicMock(side_effect=get) if callable(get) else MagicMock(return_value=get)
    m.post = MagicMock(side_effect=post) if callable(post) else MagicMock(return_value=post)
    m.put = MagicMock(side_effect=put) if callable(put) else MagicMock(return_value=put)
    m._make_request = MagicMock(return_value={"ok": True})
    return m


def unparsed(text, ref):
    return {"quantity": 1.0, "unit": None, "food": None, "note": text, "display": f"1 {text}",
            "title": None, "originalText": None, "referenceId": ref}


def parsed_result(text, qty, unit, food, conf=0.99, note=""):
    return {"input": text, "confidence": {"average": conf},
            "ingredient": {"quantity": qty, "unit": unit, "food": food, "note": note}}


class TestApiRequest:
    def test_rejects_bad_method_and_path(self):
        assert "error" in json.loads(api_request("TRACE", "/api/x"))
        assert "error" in json.loads(api_request("GET", "/docs"))

    def test_passes_through(self):
        m = mock_client()
        with patch("src.tools.extended.MealieClient", return_value=m):
            out = json.loads(api_request("get", "/api/foods", params={"search": "x"}))
        m._make_request.assert_called_once_with("GET", "/api/foods", params={"search": "x"})
        assert out["response"] == {"ok": True}

    def test_truncates(self):
        m = mock_client()
        m._make_request = MagicMock(return_value={"big": "x" * 500})
        with patch("src.tools.extended.MealieClient", return_value=m):
            out = api_request("GET", "/api/foods", max_chars=100)
        assert "truncated" in out


class TestServingsFromYield:
    def test_servings(self):
        assert _servings_from_yield({"recipeYield": "8 servings", "recipeServings": 0}) == \
            {"recipeServings": 8.0, "recipeYield": ""}

    def test_range(self):
        assert _servings_from_yield({"recipeYield": "4-6 servings"})["recipeServings"] == 4.0

    def test_other_unit(self):
        assert _servings_from_yield({"recipeYield": "12 muffins"}) == \
            {"recipeYieldQuantity": 12.0, "recipeYield": "muffins"}

    def test_already_set(self):
        assert _servings_from_yield({"recipeYield": "8 servings", "recipeServings": 6}) == {}


class TestReparse:
    def _recipe(self):
        return {"slug": "r", "recipeYield": "4 servings", "recipeServings": 0, "recipeYieldQuantity": 0,
                "recipeIngredient": [
                    unparsed("1 cup flour", "a"),
                    unparsed("1 jalapeno pepper, minced", "b"),
                    unparsed("Kosher salt and pepper", "c"),
                    {"quantity": 2, "unit": {"id": "u1", "name": "cup"}, "food": {"id": "f9", "name": "milk"},
                     "note": "", "originalText": "2 cups milk", "referenceId": "d"},
                ]}

    def test_reparse_saves_structured(self):
        recipe = self._recipe()
        cup = {"id": "u1", "name": "cup"}

        def post(path, json=None):
            if path == "/api/parser/ingredients":
                assert json["ingredients"] == ["1 cup flour", "1 jalapeno pepper, minced", "Kosher salt and pepper"]
                return [
                    parsed_result("1 cup flour", 1.0, cup, {"id": "f1", "name": "flour"}),
                    parsed_result("1 jalapeno pepper, minced", 1.0, None, {"id": None, "name": "jalapeno pepper"},
                                  note="minced"),
                    parsed_result("Kosher salt and pepper", 0, None, {"id": "f2", "name": "salt"}, conf=0.4),
                ]
            if path == "/api/foods":
                return {"id": "new", "name": json["name"]}
            raise AssertionError(path)

        m = mock_client(get=recipe, post=post, put={"slug": "r"})
        with patch("src.tools.extended.MealieClient", return_value=m):
            out = json.loads(recipes_reparse("r"))

        assert out["lines_parsed"] == 2
        assert out["created_foods"] == ["jalapeno pepper"]
        assert out["low_confidence_kept_as_text"][0]["line"] == "Kosher salt and pepper"
        assert out["servings_change"] == {"recipeServings": 4.0, "recipeYield": ""}
        saved = m.put.call_args.kwargs["json"]
        ings = saved["recipeIngredient"]
        assert ings[0]["food"]["id"] == "f1" and ings[0]["referenceId"] == "a"
        assert ings[1]["food"]["id"] == "new" and ings[1]["note"] == "minced"
        assert ings[2]["quantity"] is None and ings[2]["food"] is None
        assert ings[3]["food"]["id"] == "f9"  # already structured, untouched
        assert saved["recipeServings"] == 4.0

    def test_dry_run_does_not_save(self):
        m = mock_client(get=self._recipe(), post=[
            parsed_result("1 cup flour", 1.0, {"id": "u1", "name": "cup"}, {"id": "f1", "name": "flour"}),
            parsed_result("x", 1.0, None, {"id": "f3", "name": "jalapeno"}),
            parsed_result("y", 1.0, None, {"id": "f2", "name": "salt"}),
        ])
        with patch("src.tools.extended.MealieClient", return_value=m):
            out = json.loads(recipes_reparse("r", dry_run=True))
        assert out["dry_run"] is True and out["lines_parsed"] == 3
        m.put.assert_not_called()

    def test_unknown_unit_moves_to_note(self):
        recipe = {"slug": "r", "recipeIngredient": [unparsed("2 sprigs thyme", "a")]}
        m = mock_client(get=recipe, post=[parsed_result("2 sprigs thyme", 2.0, {"id": None, "name": "sprig"},
                                                        {"id": "f", "name": "thyme"})], put={})
        with patch("src.tools.extended.MealieClient", return_value=m):
            out = json.loads(recipes_reparse("r", fix_servings=False))
        assert out["unit_moved_to_note"] == ["sprig"]
        ing = m.put.call_args.kwargs["json"]["recipeIngredient"][0]
        assert ing["unit"] is None and ing["note"].startswith("sprig")


class TestPatchAndTools:
    def test_patch_merges_nested(self):
        recipe = {"slug": "r", "settings": {"public": False, "locked": False}, "recipeServings": 0}
        m = mock_client(get=recipe, put={"slug": "r"})
        with patch("src.tools.extended.MealieClient", return_value=m):
            out = json.loads(recipes_patch("r", {"settings": {"public": True}, "recipeServings": 4}))
        sent = m.put.call_args.kwargs["json"]
        assert sent["settings"] == {"public": True, "locked": False} and sent["recipeServings"] == 4
        assert out["success"]

    def test_patch_protects_ids(self):
        assert "error" in json.loads(recipes_patch("r", {"id": "x"}))

    def test_set_tools_creates_missing(self):
        def get(path, params=None):
            if path == "/api/organizers/tools":
                return {"items": [{"id": "t1", "name": "Blender", "slug": "blender"}], "total_pages": 1}
            return {"slug": "r", "tools": []}
        m = mock_client(get=get, post={"id": "t2", "name": "Air Fryer", "slug": "air-fryer"}, put={})
        with patch("src.tools.extended.MealieClient", return_value=m):
            out = json.loads(recipes_set_tools("r", ["blender", "Air Fryer"]))
        assert out["tools"] == ["Blender", "Air Fryer"] and out["created_tools"] == ["Air Fryer"]


class TestAudit:
    def test_flags(self):
        def get(path, params=None):
            if path == "/api/recipes":
                return {"items": [{"slug": "a"}], "total_pages": 1}
            return {"slug": "a", "name": "A", "image": None, "description": "", "recipeCategory": [],
                    "tags": [], "tools": [], "recipeServings": 0, "recipeIngredient": [unparsed("1 egg", "x")]}
        m = mock_client(get=get)
        with patch("src.tools.extended.MealieClient", return_value=m):
            out = json.loads(recipes_audit())
        assert "unparsed_ingredients:1/1" in out["recipes"][0]["flags"]
        assert out["flag_counts"]["no_image"] == 1


class TestImages:
    @respx.mock
    def test_find_image_jsonld(self):
        html = ('<html><script type="application/ld+json">{"@graph":[{"@type":"Recipe",'
                '"image":["https://img/1.jpg"]}]}</script></html>')
        respx.get("https://site/recipe").mock(return_value=Response(200, text=html))
        assert find_image_on_page("https://site/recipe") == "https://img/1.jpg"

    @respx.mock
    def test_find_image_og(self):
        html = '<meta property="og:image" content="https://img/og.jpg">'
        respx.get("https://site/r2").mock(return_value=Response(200, text=html))
        assert find_image_on_page("https://site/r2") == "https://img/og.jpg"

    def test_fill_missing(self):
        recipes = {"a": {"slug": "a", "image": None, "orgURL": "https://site/a"},
                   "b": {"slug": "b", "image": None, "orgURL": None},
                   "c": {"slug": "c", "image": "abcd", "orgURL": "https://site/c"}}
        m = mock_client(get=lambda path, params=None: recipes[path.rsplit("/", 1)[-1]], post={"image": "new"})
        with patch("src.tools.extended.MealieClient", return_value=m), \
                patch.object(extended, "find_image_on_page", return_value="https://img/a.jpg"):
            out = json.loads(recipes_fill_missing_images(slugs=["a", "b", "c"]))
        assert out["filled"] == [{"slug": "a", "image": "https://img/a.jpg"}]
        assert out["no_source_url"] == ["b"] and out["already_has_image"] == 1
        m.post.assert_called_once_with("/api/recipes/a/image", json={"url": "https://img/a.jpg", "includeTags": False})
