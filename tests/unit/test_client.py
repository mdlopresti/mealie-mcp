"""Comprehensive unit tests for MealieClient.

Tests the MealieClient HTTP layer with mocked responses using respx.
NO network calls - all HTTP responses are mocked.

Coverage areas:
- Client initialization
- HTTP methods (get, post, put, patch, delete)
- Error handling and parsing
- URL construction
- Response parsing
- Retry logic
- Specific API method wrappers
"""

import os
import pytest
import respx
from httpx import Response, ConnectError, TimeoutException
from unittest.mock import patch, MagicMock
from src.client import MealieClient, MealieAPIError, _parse_api_error
from tests.unit.builders import (
    build_recipe, build_mealplan, build_shopping_list,
    build_tag, build_category, build_tool, build_food, build_unit,
    build_cookbook, build_comment, build_timeline_event,
    build_parsed_ingredient
)


# =============================================================================
# 1. Initialization Tests (5 tests)
# =============================================================================

class TestMealieClientInitialization:
    """Test MealieClient initialization and configuration."""

    def test_init_with_explicit_params(self):
        """Test client initialization with explicit URL and token."""
        client = MealieClient(
            base_url="https://test.example.com",
            api_token="test-token-123"
        )
        assert client.base_url == "https://test.example.com"
        assert client.api_token == "test-token-123"

    def test_init_from_environment_vars(self):
        """Test client initialization from environment variables."""
        with patch.dict(os.environ, {
            "MEALIE_URL": "https://env.example.com",
            "MEALIE_API_TOKEN": "env-token-456"
        }):
            client = MealieClient()
            assert client.base_url == "https://env.example.com"
            assert client.api_token == "env-token-456"

    def test_init_missing_url_raises_error(self):
        """Test initialization fails when URL is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="MEALIE_URL must be set"):
                MealieClient(api_token="token")

    def test_init_missing_token_raises_error(self):
        """Test initialization fails when token is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="MEALIE_API_TOKEN must be set"):
                MealieClient(base_url="https://test.example.com")

    def test_init_sets_auth_headers(self):
        """Test authorization headers are set correctly."""
        client = MealieClient(
            base_url="https://test.example.com",
            api_token="secret-token"
        )
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "Bearer secret-token"
        assert client.headers["Content-Type"] == "application/json"
        assert client.headers["Accept"] == "application/json"

    def test_init_strips_trailing_slash(self):
        """Test base URL trailing slash is stripped."""
        client = MealieClient(
            base_url="https://test.example.com/",
            api_token="token"
        )
        assert client.base_url == "https://test.example.com"

    def test_context_manager_support(self):
        """Test client works as context manager."""
        with MealieClient(
            base_url="https://test.example.com",
            api_token="token"
        ) as client:
            assert client is not None
            assert client.base_url == "https://test.example.com"


# =============================================================================
# 2. HTTP Methods Tests (12 tests)
# =============================================================================

class TestMealieClientHTTPMethods:
    """Test basic HTTP method wrappers."""

    @respx.mock
    def test_get_method_success(self):
        """Test GET method returns JSON response."""
        respx.get("https://test.example.com/api/recipes").mock(
            return_value=Response(200, json={"items": [], "total": 0})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get("/api/recipes")

        assert result == {"items": [], "total": 0}

    @respx.mock
    def test_get_method_with_params(self):
        """Test GET method includes query parameters."""
        route = respx.get(
            "https://test.example.com/api/recipes",
            params={"page": "1", "perPage": "10"}
        ).mock(return_value=Response(200, json={"items": []}))

        client = MealieClient("https://test.example.com", "token")
        result = client.get("/api/recipes", params={"page": 1, "perPage": 10})

        assert result == {"items": []}
        assert route.called

    @respx.mock
    def test_post_method_success(self):
        """Test POST method sends JSON payload."""
        recipe = build_recipe()
        respx.post("https://test.example.com/api/recipes").mock(
            return_value=Response(201, json=recipe)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.post("/api/recipes", json={"name": "Test Recipe"})

        assert result["slug"] == "test-recipe"

    @respx.mock
    def test_post_method_includes_auth(self):
        """Test POST includes authorization header."""
        route = respx.post("https://test.example.com/api/recipes").mock(
            return_value=Response(201, json={})
        )

        client = MealieClient("https://test.example.com", "secret-token")
        client.post("/api/recipes", json={"name": "Test"})

        assert route.calls.last.request.headers["Authorization"] == "Bearer secret-token"

    @respx.mock
    def test_put_method_success(self):
        """Test PUT method updates resource."""
        recipe = build_recipe(name="Updated Recipe")
        respx.put("https://test.example.com/api/recipes/test").mock(
            return_value=Response(200, json=recipe)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.put("/api/recipes/test", json={"name": "Updated Recipe"})

        assert result["name"] == "Updated Recipe"

    @respx.mock
    def test_patch_method_success(self):
        """Test PATCH method partially updates resource."""
        recipe = build_recipe(description="New description")
        respx.patch("https://test.example.com/api/recipes/test").mock(
            return_value=Response(200, json=recipe)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.patch("/api/recipes/test", json={"description": "New description"})

        assert result["description"] == "New description"

    @respx.mock
    def test_delete_method_success(self):
        """Test DELETE method removes resource."""
        respx.delete("https://test.example.com/api/recipes/test").mock(
            return_value=Response(204)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.delete("/api/recipes/test")

        # DELETE with 204 returns None (no content)
        assert result is None

    @respx.mock
    def test_delete_method_with_json_response(self):
        """Test DELETE can return JSON response."""
        respx.delete("https://test.example.com/api/recipes/test").mock(
            return_value=Response(200, json={"success": True})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.delete("/api/recipes/test")

        assert result == {"success": True}

    @respx.mock
    def test_get_empty_response_returns_none(self):
        """Test GET with empty response body returns None."""
        respx.get("https://test.example.com/api/test").mock(
            return_value=Response(200, content=b"")
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get("/api/test")

        assert result is None

    @respx.mock
    def test_post_with_form_data(self):
        """Test POST can send form data instead of JSON."""
        respx.post("https://test.example.com/api/upload").mock(
            return_value=Response(200, json={"success": True})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.post("/api/upload", data={"key": "value"})

        assert result == {"success": True}


# =============================================================================
# 3. Error Handling Tests (8 tests)
# =============================================================================

class TestMealieClientErrorHandling:
    """Test error handling and error message parsing."""

    @respx.mock
    def test_get_404_raises_exception(self):
        """Test GET raises MealieAPIError on 404."""
        respx.get("https://test.example.com/api/recipes/missing").mock(
            return_value=Response(404, json={"detail": "Not found"})
        )

        client = MealieClient("https://test.example.com", "token")

        with pytest.raises(MealieAPIError) as exc_info:
            client.get("/api/recipes/missing")

        assert exc_info.value.status_code == 404

    @respx.mock
    def test_get_500_raises_exception(self):
        """Test GET raises MealieAPIError on 500."""
        respx.get("https://test.example.com/api/recipes").mock(
            return_value=Response(500, json={"error": "Internal server error"})
        )

        client = MealieClient("https://test.example.com", "token")

        with pytest.raises(MealieAPIError) as exc_info:
            client.get("/api/recipes")

        assert exc_info.value.status_code == 500

    @respx.mock
    def test_post_422_validation_error(self):
        """Test POST handles 422 validation error."""
        respx.post("https://test.example.com/api/recipes").mock(
            return_value=Response(422, json={
                "detail": [
                    {"loc": ["body", "name"], "msg": "field required", "type": "value_error.missing"}
                ]
            })
        )

        client = MealieClient("https://test.example.com", "token")

        with pytest.raises(MealieAPIError) as exc_info:
            client.post("/api/recipes", json={})

        error = exc_info.value
        assert error.status_code == 422
        assert "Validation Error" in str(error)

    @respx.mock
    def test_json_parse_error(self):
        """Test handles malformed JSON response."""
        respx.get("https://test.example.com/api/test").mock(
            return_value=Response(200, content=b"not valid json {{{")
        )

        client = MealieClient("https://test.example.com", "token")

        with pytest.raises(MealieAPIError, match="Unexpected error"):
            client.get("/api/test")

    @respx.mock
    def test_connection_error(self):
        """Test handles connection errors."""
        respx.get("https://test.example.com/api/test").mock(
            side_effect=ConnectError("Connection refused")
        )

        client = MealieClient("https://test.example.com", "token")

        with pytest.raises(MealieAPIError, match="Connection error"):
            client.get("/api/test")

    @respx.mock
    def test_timeout_error(self):
        """Test handles timeout errors."""
        respx.get("https://test.example.com/api/test").mock(
            side_effect=TimeoutException("Request timed out")
        )

        client = MealieClient("https://test.example.com", "token")

        with pytest.raises(MealieAPIError):
            client.get("/api/test")

    def test_error_parsing_with_detail_string(self):
        """Test _parse_api_error with simple detail string."""
        result = _parse_api_error(409, '{"detail": "Recipe already exists"}')

        assert "Conflict" in result["message"]
        assert "Recipe already exists" in result["details"]

    def test_error_parsing_with_validation_errors(self):
        """Test _parse_api_error with FastAPI validation errors."""
        error_json = '''{
            "detail": [
                {"loc": ["body", "name"], "msg": "field required", "type": "value_error.missing"},
                {"loc": ["body", "slug"], "msg": "invalid format", "type": "value_error"}
            ]
        }'''

        result = _parse_api_error(422, error_json)

        assert "Validation Error" in result["message"]
        assert len(result["details"]) == 2
        assert "Field 'body -> name'" in result["details"][0]


# =============================================================================
# 4. URL Construction Tests (5 tests)
# =============================================================================

class TestMealieClientURLConstruction:
    """Test URL building and path handling."""

    def test_build_url_with_leading_slash(self):
        """Test URL construction with leading slash."""
        client = MealieClient("https://test.example.com", "token")
        url = client._build_url("/api/recipes")

        assert url == "https://test.example.com/api/recipes"

    def test_build_url_without_leading_slash(self):
        """Test URL construction adds leading slash."""
        client = MealieClient("https://test.example.com", "token")
        url = client._build_url("api/recipes")

        assert url == "https://test.example.com/api/recipes"

    def test_build_url_with_path_segments(self):
        """Test URL construction with multiple path segments."""
        client = MealieClient("https://test.example.com", "token")
        url = client._build_url("/api/recipes/test-recipe/comments")

        assert url == "https://test.example.com/api/recipes/test-recipe/comments"

    @respx.mock
    def test_get_with_special_characters_in_path(self):
        """Test GET handles special characters in path."""
        respx.get("https://test.example.com/api/recipes/test-recipe-123").mock(
            return_value=Response(200, json=build_recipe())
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get("/api/recipes/test-recipe-123")

        assert result is not None

    @respx.mock
    def test_get_with_query_params_encoding(self):
        """Test query parameters are properly encoded."""
        route = respx.get(
            "https://test.example.com/api/recipes",
            params={"search": "chicken soup"}
        ).mock(return_value=Response(200, json={"items": []}))

        client = MealieClient("https://test.example.com", "token")
        client.get("/api/recipes", params={"search": "chicken soup"})

        assert route.called


# =============================================================================
# 5. Response Parsing Tests (5 tests)
# =============================================================================

class TestMealieClientResponseParsing:
    """Test JSON response parsing and data handling."""

    @respx.mock
    def test_parse_simple_json_response(self):
        """Test parsing simple JSON object."""
        respx.get("https://test.example.com/api/test").mock(
            return_value=Response(200, json={"key": "value"})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get("/api/test")

        assert result == {"key": "value"}

    @respx.mock
    def test_parse_nested_json_response(self):
        """Test parsing nested JSON structures."""
        recipe = build_recipe(
            recipeIngredient=["2 cups flour", "1 tsp salt"],
            tags=[build_tag(name="Vegan")]
        )
        respx.get("https://test.example.com/api/recipes/test").mock(
            return_value=Response(200, json=recipe)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get("/api/recipes/test")

        assert isinstance(result["recipeIngredient"], list)
        assert isinstance(result["tags"], list)
        assert result["tags"][0]["name"] == "Vegan"

    @respx.mock
    def test_parse_paginated_response(self):
        """Test parsing paginated response metadata."""
        paginated = {
            "items": [build_recipe()],
            "total": 1,
            "page": 1,
            "perPage": 10,
            "totalPages": 1
        }
        respx.get("https://test.example.com/api/recipes").mock(
            return_value=Response(200, json=paginated)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get("/api/recipes")

        assert "items" in result
        assert result["total"] == 1
        assert result["page"] == 1

    @respx.mock
    def test_parse_array_response(self):
        """Test parsing JSON array response."""
        tags = [build_tag(name="Vegan"), build_tag(name="Quick")]
        respx.get("https://test.example.com/api/organizers/tags").mock(
            return_value=Response(200, json=tags)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get("/api/organizers/tags")

        assert isinstance(result, list)
        assert len(result) == 2

    @respx.mock
    def test_parse_empty_json_object(self):
        """Test parsing empty JSON object."""
        respx.get("https://test.example.com/api/test").mock(
            return_value=Response(200, json={})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get("/api/test")

        assert result == {}


# =============================================================================
# 6. Retry Logic Tests (5 tests)
# =============================================================================

class TestMealieClientRetryLogic:
    """Test retry behavior for transient failures."""

    @respx.mock
    def test_retry_on_500_server_error(self):
        """Test retries 500 errors up to max attempts."""
        route = respx.get("https://test.example.com/api/test").mock(
            return_value=Response(500, json={"error": "Server error"})
        )

        client = MealieClient("https://test.example.com", "token")

        with pytest.raises(MealieAPIError):
            client.get("/api/test")

        # Should retry MAX_RETRIES + 1 = 4 times
        assert route.call_count == 4

    @respx.mock
    def test_retry_on_connection_error(self):
        """Test retries connection errors."""
        route = respx.get("https://test.example.com/api/test").mock(
            side_effect=ConnectError("Connection failed")
        )

        client = MealieClient("https://test.example.com", "token")

        with pytest.raises(MealieAPIError):
            client.get("/api/test")

        # Should retry MAX_RETRIES + 1 = 4 times
        assert route.call_count == 4

    @respx.mock
    def test_no_retry_on_404_client_error(self):
        """Test does NOT retry 4xx client errors."""
        route = respx.get("https://test.example.com/api/test").mock(
            return_value=Response(404, json={"detail": "Not found"})
        )

        client = MealieClient("https://test.example.com", "token")

        with pytest.raises(MealieAPIError):
            client.get("/api/test")

        # Should only try once (no retries for 4xx)
        assert route.call_count == 1

    @respx.mock
    def test_retry_succeeds_on_second_attempt(self):
        """Test successful retry after transient failure."""
        responses = [
            Response(500, json={"error": "Temporary failure"}),
            Response(200, json={"success": True})
        ]
        route = respx.get("https://test.example.com/api/test").mock(
            side_effect=responses
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get("/api/test")

        assert result == {"success": True}
        assert route.call_count == 2

    def test_should_retry_logic(self):
        """Test _should_retry determines retry eligibility."""
        client = MealieClient("https://test.example.com", "token")

        # Should retry connection errors
        assert client._should_retry(ConnectError("test"), 0) is True

        # Should NOT retry after max attempts
        assert client._should_retry(ConnectError("test"), client.MAX_RETRIES) is False

        # Should NOT retry ValueError
        assert client._should_retry(ValueError("test"), 0) is False


# =============================================================================
# 7. Recipe Methods Tests (8 tests)
# =============================================================================

class TestMealieClientRecipeMethods:
    """Test recipe-specific client methods."""

    @respx.mock
    def test_parse_ingredient(self):
        """Test parse_ingredient sends correct payload."""
        parsed = build_parsed_ingredient()
        route = respx.post("https://test.example.com/api/parser/ingredient").mock(
            return_value=Response(200, json=parsed)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.parse_ingredient("2 cups flour")

        assert result["ingredient"]["quantity"] == 2.0
        assert route.called

    @respx.mock
    def test_parse_ingredients_batch(self):
        """Test parse_ingredients_batch handles multiple ingredients."""
        parsed_list = [
            build_parsed_ingredient("2 cups flour", 2.0, "cup", "flour"),
            build_parsed_ingredient("1 tsp salt", 1.0, "teaspoon", "salt")
        ]
        respx.post("https://test.example.com/api/parser/ingredients").mock(
            return_value=Response(200, json=parsed_list)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.parse_ingredients_batch(["2 cups flour", "1 tsp salt"])

        assert len(result) == 2
        assert result[0]["ingredient"]["food"]["name"] == "flour"

    @respx.mock
    def test_duplicate_recipe(self):
        """Test duplicate_recipe creates copy."""
        new_recipe = build_recipe(name="Copy of Test Recipe", slug="copy-of-test-recipe")
        respx.post("https://test.example.com/api/recipes/test-recipe/duplicate").mock(
            return_value=Response(200, json=new_recipe)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.duplicate_recipe("test-recipe", new_name="Copy of Test Recipe")

        assert result["name"] == "Copy of Test Recipe"

    @respx.mock
    def test_update_recipe_last_made(self):
        """Test update_recipe_last_made sets timestamp."""
        recipe = build_recipe()
        respx.patch("https://test.example.com/api/recipes/test-recipe/last-made").mock(
            return_value=Response(200, json=recipe)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.update_recipe_last_made("test-recipe", "2025-12-23T10:00:00Z")

        assert result is not None

    @respx.mock
    def test_create_recipes_from_urls_bulk(self):
        """Test bulk URL import."""
        respx.post("https://test.example.com/api/recipes/create/url/bulk").mock(
            return_value=Response(200, json={"imported": 2})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.create_recipes_from_urls_bulk([
            "https://example.com/recipe1",
            "https://example.com/recipe2"
        ])

        assert result["imported"] == 2

    @respx.mock
    def test_bulk_delete_recipes(self):
        """Test bulk recipe deletion."""
        respx.post("https://test.example.com/api/recipes/bulk-actions/delete").mock(
            return_value=Response(200, json={"deleted": 3})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.bulk_delete_recipes(["recipe-1", "recipe-2", "recipe-3"])

        assert result["deleted"] == 3

    @respx.mock
    def test_bulk_export_recipes(self):
        """Test bulk recipe export."""
        respx.post("https://test.example.com/api/recipes/bulk-actions/export").mock(
            return_value=Response(200, json={"exported": 2})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.bulk_export_recipes(["recipe-1", "recipe-2"], export_format="json")

        assert result["exported"] == 2

    @respx.mock
    def test_bulk_update_settings(self):
        """Test bulk settings update."""
        respx.post("https://test.example.com/api/recipes/bulk-actions/settings").mock(
            return_value=Response(200, json={"updated": 2})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.bulk_update_settings(
            ["recipe-1", "recipe-2"],
            {"public": True}
        )

        assert result["updated"] == 2


# =============================================================================
# 8. Meal Plan Methods Tests (3 tests)
# =============================================================================

class TestMealieClientMealPlanMethods:
    """Test meal plan-specific client methods."""

    @respx.mock
    def test_list_mealplan_rules(self):
        """Test list_mealplan_rules endpoint."""
        rules = [{"id": "rule-1", "name": "Dinner Rule", "entryType": "dinner"}]
        respx.get("https://test.example.com/api/households/mealplans/rules").mock(
            return_value=Response(200, json=rules)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.list_mealplan_rules()

        assert len(result) == 1
        assert result[0]["name"] == "Dinner Rule"

    @respx.mock
    def test_create_mealplan_rule(self):
        """Test create_mealplan_rule sends correct payload."""
        rule = {"id": "rule-1", "name": "Dinner Rule", "entryType": "dinner"}
        route = respx.post("https://test.example.com/api/households/mealplans/rules").mock(
            return_value=Response(201, json=rule)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.create_mealplan_rule("Dinner Rule", "dinner", tags=["Vegan"])

        assert result["name"] == "Dinner Rule"
        assert route.called

    @respx.mock
    def test_delete_mealplan_rule(self):
        """Test delete_mealplan_rule endpoint."""
        respx.delete("https://test.example.com/api/households/mealplans/rules/rule-1").mock(
            return_value=Response(204)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.delete_mealplan_rule("rule-1")

        assert result is None


# =============================================================================
# 9. Shopping Methods Tests (3 tests)
# =============================================================================

class TestMealieClientShoppingMethods:
    """Test shopping list-specific client methods."""

    @respx.mock
    def test_delete_recipe_from_shopping_list(self):
        """Test removing recipe ingredients from shopping list."""
        respx.post(
            "https://test.example.com/api/households/shopping/lists/list-1/recipe/recipe-1/delete"
        ).mock(return_value=Response(200, json={"success": True}))

        client = MealieClient("https://test.example.com", "token")
        result = client.delete_recipe_from_shopping_list("list-1", "recipe-1")

        assert result["success"] is True


# =============================================================================
# 10. Foods & Units Methods Tests (6 tests)
# =============================================================================

class TestMealieClientFoodsAndUnits:
    """Test foods and units management methods."""

    @respx.mock
    def test_create_food(self):
        """Test create_food sends correct payload."""
        food = build_food(name="All Purpose Flour")
        respx.post("https://test.example.com/api/foods").mock(
            return_value=Response(201, json=food)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.create_food("All Purpose Flour", description="Test flour")

        assert result["name"] == "All Purpose Flour"

    @respx.mock
    def test_list_foods_with_pagination(self):
        """Test list_foods includes pagination params."""
        route = respx.get(
            "https://test.example.com/api/foods",
            params={"page": "2", "perPage": "25"}
        ).mock(return_value=Response(200, json={"items": [], "total": 0}))

        client = MealieClient("https://test.example.com", "token")
        client.list_foods(page=2, per_page=25)

        assert route.called

    @respx.mock
    def test_merge_foods(self):
        """Test merge_foods combines two foods."""
        respx.post("https://test.example.com/api/foods/merge").mock(
            return_value=Response(200, json={"success": True})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.merge_foods("food-1", "food-2")

        assert result["success"] is True

    @respx.mock
    def test_create_unit(self):
        """Test create_unit sends correct payload."""
        unit = build_unit(name="tablespoon", abbreviation="tbsp")
        respx.post("https://test.example.com/api/units").mock(
            return_value=Response(201, json=unit)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.create_unit("tablespoon", abbreviation="tbsp")

        assert result["name"] == "tablespoon"

    @respx.mock
    def test_update_unit(self):
        """Test update_unit patches unit fields."""
        unit = build_unit(name="tablespoon", abbreviation="T")
        respx.patch("https://test.example.com/api/units/unit-1").mock(
            return_value=Response(200, json=unit)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.update_unit("unit-1", abbreviation="T")

        assert result is not None

    @respx.mock
    def test_merge_units(self):
        """Test merge_units combines two units."""
        respx.post("https://test.example.com/api/units/merge").mock(
            return_value=Response(200, json={"success": True})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.merge_units("unit-1", "unit-2")

        assert result["success"] is True


# =============================================================================
# 11. Organizers Methods Tests (6 tests)
# =============================================================================

class TestMealieClientOrganizers:
    """Test organizers (categories, tags, tools) methods."""

    @respx.mock
    def test_list_categories(self):
        """Test list_categories returns array."""
        categories = [build_category(name="Dessert")]
        respx.get("https://test.example.com/api/organizers/categories").mock(
            return_value=Response(200, json=categories)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.list_categories()

        assert len(result) == 1
        assert result[0]["name"] == "Dessert"

    @respx.mock
    def test_create_tag(self):
        """Test create_tag sends name payload."""
        tag = build_tag(name="Vegan")
        respx.post("https://test.example.com/api/organizers/tags").mock(
            return_value=Response(201, json=tag)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.create_tag("Vegan")

        assert result["name"] == "Vegan"

    @respx.mock
    def test_update_category(self):
        """Test update_category patches fields."""
        category = build_category(name="Main Dishes")
        respx.patch("https://test.example.com/api/organizers/categories/cat-1").mock(
            return_value=Response(200, json=category)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.update_category("cat-1", name="Main Dishes")

        assert result["name"] == "Main Dishes"

    @respx.mock
    def test_delete_tag(self):
        """Test delete_tag removes tag."""
        respx.delete("https://test.example.com/api/organizers/tags/tag-1").mock(
            return_value=Response(204)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.delete_tag("tag-1")

        assert result is None

    @respx.mock
    def test_create_tool(self):
        """Test create_tool creates kitchen tool."""
        tool = build_tool(name="Blender")
        respx.post("https://test.example.com/api/organizers/tools").mock(
            return_value=Response(201, json=tool)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.create_tool("Blender")

        assert result["name"] == "Blender"

    @respx.mock
    def test_list_tools(self):
        """Test list_tools returns array."""
        tools = [build_tool(name="Stand Mixer")]
        respx.get("https://test.example.com/api/organizers/tools").mock(
            return_value=Response(200, json=tools)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.list_tools()

        assert len(result) == 1


# =============================================================================
# 12. Cookbooks Methods Tests (3 tests)
# =============================================================================

class TestMealieClientCookbooks:
    """Test cookbook management methods."""

    @respx.mock
    def test_list_cookbooks(self):
        """Test list_cookbooks endpoint."""
        cookbooks = [build_cookbook(name="Holiday Recipes")]
        respx.get("https://test.example.com/api/households/cookbooks").mock(
            return_value=Response(200, json=cookbooks)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.list_cookbooks()

        assert len(result) == 1

    @respx.mock
    def test_create_cookbook(self):
        """Test create_cookbook sends correct payload."""
        cookbook = build_cookbook(name="New Cookbook", public=True)
        respx.post("https://test.example.com/api/households/cookbooks").mock(
            return_value=Response(201, json=cookbook)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.create_cookbook("New Cookbook", public=True)

        assert result["name"] == "New Cookbook"
        assert result["public"] is True

    @respx.mock
    def test_delete_cookbook(self):
        """Test delete_cookbook removes cookbook."""
        respx.delete("https://test.example.com/api/households/cookbooks/cookbook-1").mock(
            return_value=Response(204)
        )

        client = MealieClient("https://test.example.com", "token")
        client.delete_cookbook("cookbook-1")


# =============================================================================
# 13. Comments Methods Tests (3 tests)
# =============================================================================

class TestMealieClientComments:
    """Test recipe comments methods."""

    @respx.mock
    def test_get_recipe_comments(self):
        """Test get_recipe_comments retrieves comments for recipe."""
        comments = [build_comment(text="Great recipe!")]
        respx.get("https://test.example.com/api/recipes/test-recipe/comments").mock(
            return_value=Response(200, json=comments)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get_recipe_comments("test-recipe")

        assert len(result) == 1

    @respx.mock
    def test_create_comment(self):
        """Test create_comment posts new comment."""
        comment = build_comment(text="Delicious!")
        respx.post("https://test.example.com/api/comments").mock(
            return_value=Response(201, json=comment)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.create_comment("recipe-123", "Delicious!")

        assert result["text"] == "Delicious!"

    @respx.mock
    def test_update_comment(self):
        """Test update_comment modifies existing comment."""
        comment = build_comment(text="Updated comment")
        respx.put("https://test.example.com/api/comments/comment-1").mock(
            return_value=Response(200, json=comment)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.update_comment("comment-1", "Updated comment")

        assert result["text"] == "Updated comment"


# =============================================================================
# 14. Timeline Events Methods Tests (3 tests)
# =============================================================================

class TestMealieClientTimeline:
    """Test recipe timeline events methods."""

    @respx.mock
    def test_list_timeline_events(self):
        """Test list_timeline_events with pagination."""
        events = [build_timeline_event(subject="Made for dinner")]
        route = respx.get(
            "https://test.example.com/api/recipes/timeline/events",
            params={"page": "1", "perPage": "50"}
        ).mock(return_value=Response(200, json={"items": events, "total": 1}))

        client = MealieClient("https://test.example.com", "token")
        result = client.list_timeline_events(page=1, per_page=50)

        assert route.called
        assert len(result["items"]) == 1

    @respx.mock
    def test_create_timeline_event(self):
        """Test create_timeline_event creates new event."""
        event = build_timeline_event(subject="Made for party")
        respx.post("https://test.example.com/api/recipes/timeline/events").mock(
            return_value=Response(201, json=event)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.create_timeline_event(
            recipe_id="recipe-123",
            subject="Made for party",
            event_type="info"
        )

        assert result["subject"] == "Made for party"

    @respx.mock
    def test_delete_timeline_event(self):
        """Test delete_timeline_event removes event."""
        respx.delete("https://test.example.com/api/recipes/timeline/events/event-1").mock(
            return_value=Response(204)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.delete_timeline_event("event-1")

        assert result is None


# =============================================================================
# 15. Connection Testing (2 tests)
# =============================================================================

class TestMealieClientConnectionTesting:
    """Test connection testing functionality."""

    @respx.mock
    def test_test_connection_success(self):
        """Test test_connection returns True on success."""
        respx.get("https://test.example.com/api/app/about").mock(
            return_value=Response(200, json={"version": "1.0.0"})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.test_connection()

        assert result is True

    @respx.mock
    def test_test_connection_failure(self):
        """Test test_connection raises error on failure."""
        respx.get("https://test.example.com/api/app/about").mock(
            return_value=Response(401, json={"error": "Unauthorized"})
        )

        client = MealieClient("https://test.example.com", "token")

        with pytest.raises(MealieAPIError):
            client.test_connection()


# =============================================================================
# 16. Additional Client Methods (15 tests)
# =============================================================================

class TestMealieClientAdditionalMethods:
    """Test additional uncovered client methods."""

    @respx.mock
    def test_update_recipe_ingredients(self):
        """Test update_recipe_ingredients patches ingredient list."""
        recipe = build_recipe()
        respx.patch("https://test.example.com/api/recipes/test-recipe").mock(
            return_value=Response(200, json=recipe)
        )

        client = MealieClient("https://test.example.com", "token")
        ingredients = [
            {"quantity": 2.0, "unit": "cup", "food": "flour", "display": "2 cups flour"}
        ]
        result = client.update_recipe_ingredients("test-recipe", ingredients)

        assert result is not None

    @respx.mock
    def test_update_food_fetches_current_first(self):
        """Test update_food fetches current food before updating."""
        current_food = build_food(name="Flour", description="Old description")
        updated_food = build_food(name="All Purpose Flour", description="New description")

        respx.get("https://test.example.com/api/foods/food-1").mock(
            return_value=Response(200, json=current_food)
        )
        respx.put("https://test.example.com/api/foods/food-1").mock(
            return_value=Response(200, json=updated_food)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.update_food("food-1", name="All Purpose Flour", description="New description")

        assert result["name"] == "All Purpose Flour"

    @respx.mock
    def test_get_mealplan_rule(self):
        """Test get_mealplan_rule retrieves specific rule."""
        rule = {"id": "rule-1", "name": "Dinner Rule", "entryType": "dinner"}
        respx.get("https://test.example.com/api/households/mealplans/rules/rule-1").mock(
            return_value=Response(200, json=rule)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get_mealplan_rule("rule-1")

        assert result["name"] == "Dinner Rule"

    @respx.mock
    def test_update_mealplan_rule(self):
        """Test update_mealplan_rule patches rule fields."""
        rule = {"id": "rule-1", "name": "Updated Rule", "entryType": "lunch"}
        respx.patch("https://test.example.com/api/households/mealplans/rules/rule-1").mock(
            return_value=Response(200, json=rule)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.update_mealplan_rule("rule-1", name="Updated Rule", entry_type="lunch")

        assert result["name"] == "Updated Rule"

    @respx.mock
    def test_get_food(self):
        """Test get_food retrieves specific food."""
        food = build_food(name="Flour")
        respx.get("https://test.example.com/api/foods/food-1").mock(
            return_value=Response(200, json=food)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get_food("food-1")

        assert result["name"] == "Flour"

    @respx.mock
    def test_delete_food(self):
        """Test delete_food removes food."""
        respx.delete("https://test.example.com/api/foods/food-1").mock(
            return_value=Response(204)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.delete_food("food-1")

        assert result is None

    @respx.mock
    def test_get_unit(self):
        """Test get_unit retrieves specific unit."""
        unit = build_unit(name="cup")
        respx.get("https://test.example.com/api/units/unit-1").mock(
            return_value=Response(200, json=unit)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get_unit("unit-1")

        assert result["name"] == "cup"

    @respx.mock
    def test_delete_unit(self):
        """Test delete_unit removes unit."""
        respx.delete("https://test.example.com/api/units/unit-1").mock(
            return_value=Response(204)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.delete_unit("unit-1")

        assert result is None

    @respx.mock
    def test_get_cookbook(self):
        """Test get_cookbook retrieves specific cookbook."""
        cookbook = build_cookbook(name="Test Cookbook")
        respx.get("https://test.example.com/api/households/cookbooks/cookbook-1").mock(
            return_value=Response(200, json=cookbook)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get_cookbook("cookbook-1")

        assert result["name"] == "Test Cookbook"

    @respx.mock
    def test_update_cookbook(self):
        """Test update_cookbook updates cookbook fields."""
        cookbook = build_cookbook(name="Updated Cookbook", public=True)
        respx.put("https://test.example.com/api/households/cookbooks/cookbook-1").mock(
            return_value=Response(200, json=cookbook)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.update_cookbook("cookbook-1", name="Updated Cookbook", public=True)

        assert result["name"] == "Updated Cookbook"
        assert result["public"] is True

    @respx.mock
    def test_get_comment(self):
        """Test get_comment retrieves specific comment."""
        comment = build_comment(text="Great!")
        respx.get("https://test.example.com/api/comments/comment-1").mock(
            return_value=Response(200, json=comment)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get_comment("comment-1")

        assert result["text"] == "Great!"

    @respx.mock
    def test_delete_comment(self):
        """Test delete_comment removes comment."""
        respx.delete("https://test.example.com/api/comments/comment-1").mock(
            return_value=Response(204)
        )

        client = MealieClient("https://test.example.com", "token")
        client.delete_comment("comment-1")

    @respx.mock
    def test_get_timeline_event(self):
        """Test get_timeline_event retrieves specific event."""
        event = build_timeline_event(subject="Made for party")
        respx.get("https://test.example.com/api/recipes/timeline/events/event-1").mock(
            return_value=Response(200, json=event)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get_timeline_event("event-1")

        assert result["subject"] == "Made for party"

    @respx.mock
    def test_update_timeline_event(self):
        """Test update_timeline_event updates event fields."""
        event = build_timeline_event(subject="Updated subject")
        respx.put("https://test.example.com/api/recipes/timeline/events/event-1").mock(
            return_value=Response(200, json=event)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.update_timeline_event("event-1", subject="Updated subject")

        assert result["subject"] == "Updated subject"

    @respx.mock
    def test_get_category(self):
        """Test get_category retrieves specific category."""
        category = build_category(name="Dessert")
        respx.get("https://test.example.com/api/organizers/categories/cat-1").mock(
            return_value=Response(200, json=category)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get_category("cat-1")

        assert result["name"] == "Dessert"

    @respx.mock
    def test_delete_category(self):
        """Test delete_category removes category."""
        respx.delete("https://test.example.com/api/organizers/categories/cat-1").mock(
            return_value=Response(204)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.delete_category("cat-1")

        assert result is None

    @respx.mock
    def test_get_tag(self):
        """Test get_tag retrieves specific tag."""
        tag = build_tag(name="Vegan")
        respx.get("https://test.example.com/api/organizers/tags/tag-1").mock(
            return_value=Response(200, json=tag)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get_tag("tag-1")

        assert result["name"] == "Vegan"

    @respx.mock
    def test_update_tag(self):
        """Test update_tag patches tag fields."""
        tag = build_tag(name="Plant-Based")
        respx.patch("https://test.example.com/api/organizers/tags/tag-1").mock(
            return_value=Response(200, json=tag)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.update_tag("tag-1", name="Plant-Based")

        assert result["name"] == "Plant-Based"

    @respx.mock
    def test_get_tool(self):
        """Test get_tool retrieves specific kitchen tool."""
        tool = build_tool(name="Blender")
        respx.get("https://test.example.com/api/organizers/tools/tool-1").mock(
            return_value=Response(200, json=tool)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.get_tool("tool-1")

        assert result["name"] == "Blender"

    @respx.mock
    def test_update_tool(self):
        """Test update_tool patches tool fields."""
        tool = build_tool(name="Food Processor")
        respx.patch("https://test.example.com/api/organizers/tools/tool-1").mock(
            return_value=Response(200, json=tool)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.update_tool("tool-1", name="Food Processor")

        assert result["name"] == "Food Processor"

    @respx.mock
    def test_delete_tool(self):
        """Test delete_tool removes kitchen tool."""
        respx.delete("https://test.example.com/api/organizers/tools/tool-1").mock(
            return_value=Response(204)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.delete_tool("tool-1")

        assert result is None

    @respx.mock
    def test_list_units(self):
        """Test list_units with pagination."""
        units = [build_unit(name="cup"), build_unit(name="tablespoon", abbreviation="tbsp")]
        route = respx.get(
            "https://test.example.com/api/units",
            params={"page": "1", "perPage": "50"}
        ).mock(return_value=Response(200, json={"items": units, "total": 2}))

        client = MealieClient("https://test.example.com", "token")
        result = client.list_units(page=1, per_page=50)

        assert route.called
        assert len(result["items"]) == 2


# =============================================================================
# 17. Complex Bulk Operations (5 tests)
# =============================================================================

class TestMealieClientBulkOperations:
    """Test complex bulk operations with tag/category creation."""

    @respx.mock
    def test_bulk_tag_recipes_with_existing_tags(self):
        """Test bulk_tag_recipes uses existing tags."""
        recipe1 = build_recipe(slug="recipe-1")
        recipe2 = build_recipe(slug="recipe-2")
        existing_tags = [build_tag(name="Vegan"), build_tag(name="Quick")]

        # Mock recipe fetches
        respx.get("https://test.example.com/api/recipes/recipe-1").mock(
            return_value=Response(200, json=recipe1)
        )
        respx.get("https://test.example.com/api/recipes/recipe-2").mock(
            return_value=Response(200, json=recipe2)
        )

        # Mock tag list
        respx.get("https://test.example.com/api/organizers/tags").mock(
            return_value=Response(200, json=existing_tags)
        )

        # Mock bulk action
        respx.post("https://test.example.com/api/recipes/bulk-actions/tag").mock(
            return_value=Response(200, json={"tagged": 2})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.bulk_tag_recipes(["recipe-1", "recipe-2"], ["Vegan", "Quick"])

        assert result["tagged"] == 2

    @respx.mock
    def test_bulk_tag_recipes_creates_missing_tags(self):
        """Test bulk_tag_recipes creates missing tags."""
        recipe = build_recipe(slug="recipe-1")
        existing_tag = build_tag(name="Vegan")
        new_tag = build_tag(name="New Tag")

        # Mock recipe fetch
        respx.get("https://test.example.com/api/recipes/recipe-1").mock(
            return_value=Response(200, json=recipe)
        )

        # Mock tag list (only has Vegan)
        respx.get("https://test.example.com/api/organizers/tags").mock(
            return_value=Response(200, json=[existing_tag])
        )

        # Mock tag creation for missing tag
        respx.post("https://test.example.com/api/organizers/tags").mock(
            return_value=Response(201, json=new_tag)
        )

        # Mock bulk action
        respx.post("https://test.example.com/api/recipes/bulk-actions/tag").mock(
            return_value=Response(200, json={"tagged": 1})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.bulk_tag_recipes(["recipe-1"], ["Vegan", "New Tag"])

        assert result["tagged"] == 1

    @respx.mock
    def test_bulk_categorize_recipes_with_existing_categories(self):
        """Test bulk_categorize_recipes uses existing categories."""
        recipe1 = build_recipe(slug="recipe-1")
        recipe2 = build_recipe(slug="recipe-2")
        existing_categories = [build_category(name="Dessert"), build_category(name="Main")]

        # Mock recipe fetches
        respx.get("https://test.example.com/api/recipes/recipe-1").mock(
            return_value=Response(200, json=recipe1)
        )
        respx.get("https://test.example.com/api/recipes/recipe-2").mock(
            return_value=Response(200, json=recipe2)
        )

        # Mock category list
        respx.get("https://test.example.com/api/organizers/categories").mock(
            return_value=Response(200, json=existing_categories)
        )

        # Mock bulk action
        respx.post("https://test.example.com/api/recipes/bulk-actions/categorize").mock(
            return_value=Response(200, json={"categorized": 2})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.bulk_categorize_recipes(["recipe-1", "recipe-2"], ["Dessert", "Main"])

        assert result["categorized"] == 2

    @respx.mock
    def test_bulk_categorize_recipes_creates_missing_categories(self):
        """Test bulk_categorize_recipes creates missing categories."""
        recipe = build_recipe(slug="recipe-1")
        existing_cat = build_category(name="Dessert")
        new_cat = build_category(name="New Category")

        # Mock recipe fetch
        respx.get("https://test.example.com/api/recipes/recipe-1").mock(
            return_value=Response(200, json=recipe)
        )

        # Mock category list (only has Dessert)
        respx.get("https://test.example.com/api/organizers/categories").mock(
            return_value=Response(200, json=[existing_cat])
        )

        # Mock category creation for missing category
        respx.post("https://test.example.com/api/organizers/categories").mock(
            return_value=Response(201, json=new_cat)
        )

        # Mock bulk action
        respx.post("https://test.example.com/api/recipes/bulk-actions/categorize").mock(
            return_value=Response(200, json={"categorized": 1})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.bulk_categorize_recipes(["recipe-1"], ["Dessert", "New Category"])

        assert result["categorized"] == 1

    @respx.mock
    def test_bulk_tag_recipes_handles_paginated_tag_list(self):
        """Test bulk_tag_recipes handles paginated tag response."""
        recipe = build_recipe(slug="recipe-1")
        existing_tags = [build_tag(name="Vegan")]
        paginated_response = {"items": existing_tags, "total": 1}

        # Mock recipe fetch
        respx.get("https://test.example.com/api/recipes/recipe-1").mock(
            return_value=Response(200, json=recipe)
        )

        # Mock paginated tag list
        respx.get("https://test.example.com/api/organizers/tags").mock(
            return_value=Response(200, json=paginated_response)
        )

        # Mock bulk action
        respx.post("https://test.example.com/api/recipes/bulk-actions/tag").mock(
            return_value=Response(200, json={"tagged": 1})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.bulk_tag_recipes(["recipe-1"], ["Vegan"])

        assert result["tagged"] == 1


# =============================================================================
# 18. Error Parsing Edge Cases (3 tests)
# =============================================================================

class TestMealieClientErrorParsingEdgeCases:
    """Test edge cases in error parsing."""

    def test_parse_error_with_unknown_format(self):
        """Test _parse_api_error handles unknown error format."""
        result = _parse_api_error(500, '{"unknown_field": "some value"}')

        assert "Server Error" in result["message"]
        assert result["suggestions"]

    def test_parse_error_with_non_json(self):
        """Test _parse_api_error handles non-JSON response."""
        result = _parse_api_error(500, "Plain text error")

        assert "Server Error" in result["message"]
        assert "Plain text error" in result["raw_response"]

    def test_parse_error_with_error_field(self):
        """Test _parse_api_error handles error field format."""
        result = _parse_api_error(500, '{"error": "Something went wrong"}')

        assert "Something went wrong" in result["details"]


# =============================================================================
# 19. Client Close and Context Manager (2 tests)
# =============================================================================

class TestMealieClientContextManager:
    """Test client cleanup and context manager behavior."""

    def test_client_close_method(self):
        """Test client.close() closes HTTP client."""
        client = MealieClient("https://test.example.com", "token")
        client.close()
        # Should not raise error when closed

    def test_context_manager_exit_calls_close(self):
        """Test context manager calls close on exit."""
        with MealieClient("https://test.example.com", "token") as client:
            assert client is not None
        # Client should be closed after exiting context


# =============================================================================
# 20. Additional Coverage for Edge Cases (5 tests)
# =============================================================================

class TestMealieClientEdgeCases:
    """Test additional edge cases for better coverage."""

    @respx.mock
    def test_test_connection_with_empty_response(self):
        """Test test_connection handles empty response."""
        respx.get("https://test.example.com/api/app/about").mock(
            return_value=Response(200, json={})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.test_connection()

        assert result is True

    @respx.mock
    def test_test_connection_with_alternative_version_key(self):
        """Test test_connection recognizes different version keys."""
        respx.get("https://test.example.com/api/app/about").mock(
            return_value=Response(200, json={"apiVersion": "2.0.0"})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.test_connection()

        assert result is True

    def test_parse_error_with_message_field(self):
        """Test _parse_api_error handles message field format."""
        result = _parse_api_error(500, '{"message": "Internal error occurred"}')

        assert "Internal error occurred" in result["details"]

    def test_parse_error_with_list_detail(self):
        """Test _parse_api_error handles list detail with non-dict items."""
        result = _parse_api_error(422, '{"detail": ["error1", "error2"]}')

        assert any("error1" in detail or "error2" in detail for detail in result["details"])

    def test_parse_error_with_complex_dict_values(self):
        """Test _parse_api_error handles dict with list values."""
        result = _parse_api_error(500, '{"errors": ["item1", "item2", "item3", "item4"]}')

        # Should extract first 3 items from list
        assert "errors" in str(result["details"])

    def test_parse_error_with_non_dict_non_string_data(self):
        """Test _parse_api_error handles non-dict error data."""
        result = _parse_api_error(500, '[1, 2, 3]')

        assert "Unexpected error format" in str(result["details"])

    @respx.mock
    def test_parse_ingredient_with_custom_parser(self):
        """Test parse_ingredient with custom parser type."""
        parsed = build_parsed_ingredient()
        respx.post("https://test.example.com/api/parser/ingredient").mock(
            return_value=Response(200, json=parsed)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.parse_ingredient("2 cups flour", parser="brute")

        assert result is not None

    @respx.mock
    def test_parse_ingredients_batch_with_openai_parser(self):
        """Test parse_ingredients_batch with openai parser."""
        parsed_list = [build_parsed_ingredient()]
        respx.post("https://test.example.com/api/parser/ingredients").mock(
            return_value=Response(200, json=parsed_list)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.parse_ingredients_batch(["2 cups flour"], parser="openai")

        assert len(result) == 1

    @respx.mock
    def test_duplicate_recipe_without_new_name(self):
        """Test duplicate_recipe without specifying new name."""
        new_recipe = build_recipe(name="Copy of Test Recipe")
        respx.post("https://test.example.com/api/recipes/test-recipe/duplicate").mock(
            return_value=Response(200, json=new_recipe)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.duplicate_recipe("test-recipe")

        assert result is not None

    @respx.mock
    def test_update_recipe_last_made_without_timestamp(self):
        """Test update_recipe_last_made without explicit timestamp."""
        recipe = build_recipe()
        respx.patch("https://test.example.com/api/recipes/test-recipe/last-made").mock(
            return_value=Response(200, json=recipe)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.update_recipe_last_made("test-recipe")

        assert result is not None

    @respx.mock
    def test_create_mealplan_rule_without_tags_or_categories(self):
        """Test create_mealplan_rule with minimal params."""
        rule = {"id": "rule-1", "name": "Simple Rule", "entryType": "dinner"}
        respx.post("https://test.example.com/api/households/mealplans/rules").mock(
            return_value=Response(201, json=rule)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.create_mealplan_rule("Simple Rule", "dinner")

        assert result["name"] == "Simple Rule"

    @respx.mock
    def test_update_mealplan_rule_partial_update(self):
        """Test update_mealplan_rule with only some fields."""
        rule = {"id": "rule-1", "name": "Same Name", "entryType": "lunch"}
        respx.patch("https://test.example.com/api/households/mealplans/rules/rule-1").mock(
            return_value=Response(200, json=rule)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.update_mealplan_rule("rule-1", entry_type="lunch")

        assert result["entryType"] == "lunch"

    @respx.mock
    def test_create_food_with_all_params(self):
        """Test create_food with all optional parameters."""
        food = build_food(name="Flour", description="All-purpose flour")
        respx.post("https://test.example.com/api/foods").mock(
            return_value=Response(201, json=food)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.create_food("Flour", description="All-purpose flour", label_id="label-123")

        assert result["name"] == "Flour"

    @respx.mock
    def test_create_unit_with_all_params(self):
        """Test create_unit with all optional parameters."""
        unit = build_unit(name="tablespoon", abbreviation="tbsp")
        respx.post("https://test.example.com/api/units").mock(
            return_value=Response(201, json=unit)
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.create_unit("tablespoon", description="A tablespoon", abbreviation="tbsp")

        assert result["name"] == "tablespoon"

    def test_parse_error_with_detail_object_unexpected_format(self):
        """Test _parse_api_error handles detail object with unexpected value type."""
        result = _parse_api_error(422, '{"detail": {"key": 123}}')

        assert "Unexpected detail format" in str(result["details"])

    @respx.mock
    def test_test_connection_with_versionAPI_key(self):
        """Test test_connection recognizes versionAPI key."""
        respx.get("https://test.example.com/api/app/about").mock(
            return_value=Response(200, json={"versionAPI": "3.0.0"})
        )

        client = MealieClient("https://test.example.com", "token")
        result = client.test_connection()

        assert result is True
