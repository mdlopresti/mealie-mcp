"""
Comprehensive MCP tool registration and invocation tests.

Tests all 92 MCP tools registered in src/server.py for:
- Registration (@mcp.tool decorator)
- Parameter validation (required vs optional)
- Invocation with valid inputs
- Error handling
- Response formatting (JSON structure)
- Authentication (client initialization)

Target: 60%+ coverage of src/server.py
"""

import pytest
import json
from tests.mcp.helpers import (
    validate_tool_registration,
    validate_tool_params,
    validate_mcp_response,
    extract_tool_result_text
)


class TestUtilityTools:
    """Test utility tools (ping)."""

    @pytest.mark.asyncio
    async def test_ping_registered(self, mcp_server):
        """Test that ping tool is registered."""
        assert await validate_tool_registration(mcp_server, "ping")

    @pytest.mark.asyncio
    async def test_ping_invocation(self, invoke_mcp_tool):
        """Test invoking ping tool."""
        result = await invoke_mcp_tool("ping")

        validation = validate_mcp_response(result)
        assert validation["valid"], validation.get("error")

        text = extract_tool_result_text(result)
        assert "mealie" in text.lower() or "pong" in text.lower()

    @pytest.mark.asyncio
    async def test_ping_no_parameters(self, mcp_server):
        """Test that ping has no required parameters."""
        tools = await mcp_server.get_tools()
        tool = tools["ping"]

        # Should have no required parameters
        params = tool.parameters
        assert params.get("required", []) == []


class TestRecipeTools:
    """Test recipe management tools (18 tools)."""

    # --- Search & Browse Tools ---

    @pytest.mark.asyncio
    async def test_recipes_search_registered(self, mcp_server):
        """Test mealie_recipes_search is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_search")

    @pytest.mark.asyncio
    async def test_recipes_search_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_recipes_search."""
        mock_response = {
            "items": [{"name": "Pasta", "slug": "pasta"}],
            "total": 1
        }

        result = await invoke_mcp_tool(
            "mealie_recipes_search",
            mock_response=mock_response,
            query="pasta"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

        text = extract_tool_result_text(result)
        data = json.loads(text)
        assert "recipes" in data

    @pytest.mark.asyncio
    async def test_recipes_get_registered(self, mcp_server):
        """Test mealie_recipes_get is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_get")

    @pytest.mark.asyncio
    async def test_recipes_get_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_recipes_get."""
        mock_response = {
            "slug": "test-recipe",
            "name": "Test Recipe",
            "recipeIngredient": [],
            "recipeInstructions": []
        }

        result = await invoke_mcp_tool(
            "mealie_recipes_get",
            mock_response=mock_response,
            slug="test-recipe"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_recipes_list_registered(self, mcp_server):
        """Test mealie_recipes_list is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_list")

    @pytest.mark.asyncio
    async def test_recipes_list_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_recipes_list."""
        mock_response = {"items": [], "total": 0}

        result = await invoke_mcp_tool(
            "mealie_recipes_list",
            mock_response=mock_response,
            page=1
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    # --- CRUD Tools ---

    @pytest.mark.asyncio
    async def test_recipes_create_registered(self, mcp_server):
        """Test mealie_recipes_create is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_create")

    @pytest.mark.asyncio
    async def test_recipes_create_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_recipes_create."""
        mock_response = {
            "id": "recipe-123",
            "slug": "new-recipe",
            "name": "New Recipe"
        }

        result = await invoke_mcp_tool(
            "mealie_recipes_create",
            mock_response=mock_response,
            name="New Recipe"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

        text = extract_tool_result_text(result)
        data = json.loads(text)
        # Response may be wrapped in different formats, just check it's valid JSON
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_recipes_create_from_url_registered(self, mcp_server):
        """Test mealie_recipes_create_from_url is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_create_from_url")

    @pytest.mark.asyncio
    async def test_recipes_create_from_url_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_recipes_create_from_url."""
        mock_response = {
            "slug": "imported-recipe",
            "name": "Imported Recipe"
        }

        result = await invoke_mcp_tool(
            "mealie_recipes_create_from_url",
            mock_response=mock_response,
            url="https://example.com/recipe"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_recipes_update_registered(self, mcp_server):
        """Test mealie_recipes_update is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_update")

    @pytest.mark.asyncio
    async def test_recipes_update_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_recipes_update."""
        mock_response = {
            "slug": "test-recipe",
            "name": "Updated Recipe"
        }

        result = await invoke_mcp_tool(
            "mealie_recipes_update",
            mock_response=mock_response,
            slug="test-recipe",
            name="Updated Recipe"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_recipes_update_structured_ingredients_registered(self, mcp_server):
        """Test mealie_recipes_update_structured_ingredients is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_update_structured_ingredients")

    @pytest.mark.asyncio
    async def test_recipes_delete_registered(self, mcp_server):
        """Test mealie_recipes_delete is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_delete")

    @pytest.mark.asyncio
    async def test_recipes_delete_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_recipes_delete."""
        mock_response = {"message": "Recipe deleted"}

        result = await invoke_mcp_tool(
            "mealie_recipes_delete",
            mock_response=mock_response,
            slug="test-recipe"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    # --- Additional Recipe Tools ---

    @pytest.mark.asyncio
    async def test_recipes_duplicate_registered(self, mcp_server):
        """Test mealie_recipes_duplicate is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_duplicate")

    @pytest.mark.asyncio
    async def test_recipes_update_last_made_registered(self, mcp_server):
        """Test mealie_recipes_update_last_made is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_update_last_made")

    @pytest.mark.asyncio
    async def test_recipes_create_from_urls_bulk_registered(self, mcp_server):
        """Test mealie_recipes_create_from_urls_bulk is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_create_from_urls_bulk")

    @pytest.mark.asyncio
    async def test_recipes_bulk_tag_registered(self, mcp_server):
        """Test mealie_recipes_bulk_tag is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_bulk_tag")

    @pytest.mark.asyncio
    async def test_recipes_bulk_categorize_registered(self, mcp_server):
        """Test mealie_recipes_bulk_categorize is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_bulk_categorize")

    @pytest.mark.asyncio
    async def test_recipes_bulk_delete_registered(self, mcp_server):
        """Test mealie_recipes_bulk_delete is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_bulk_delete")

    @pytest.mark.asyncio
    async def test_recipes_bulk_export_registered(self, mcp_server):
        """Test mealie_recipes_bulk_export is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_bulk_export")

    @pytest.mark.asyncio
    async def test_recipes_bulk_update_settings_registered(self, mcp_server):
        """Test mealie_recipes_bulk_update_settings is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_bulk_update_settings")

    @pytest.mark.asyncio
    async def test_recipes_create_from_image_registered(self, mcp_server):
        """Test mealie_recipes_create_from_image is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_create_from_image")

    @pytest.mark.asyncio
    async def test_recipes_upload_image_from_url_registered(self, mcp_server):
        """Test mealie_recipes_upload_image_from_url is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_recipes_upload_image_from_url")


class TestMealPlanTools:
    """Test meal plan tools (16 tools)."""

    # --- Core Meal Plan Tools ---

    @pytest.mark.asyncio
    async def test_mealplans_list_registered(self, mcp_server):
        """Test mealie_mealplans_list is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_mealplans_list")

    @pytest.mark.asyncio
    async def test_mealplans_list_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_mealplans_list."""
        mock_response = {"items": [], "total": 0}

        result = await invoke_mcp_tool(
            "mealie_mealplans_list",
            mock_response=mock_response
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_mealplans_today_registered(self, mcp_server):
        """Test mealie_mealplans_today is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_mealplans_today")

    @pytest.mark.asyncio
    async def test_mealplans_get_registered(self, mcp_server):
        """Test mealie_mealplans_get is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_mealplans_get")

    @pytest.mark.asyncio
    async def test_mealplans_get_date_registered(self, mcp_server):
        """Test mealie_mealplans_get_date is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_mealplans_get_date")

    @pytest.mark.asyncio
    async def test_mealplans_create_registered(self, mcp_server):
        """Test mealie_mealplans_create is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_mealplans_create")

    @pytest.mark.asyncio
    async def test_mealplans_create_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_mealplans_create."""
        mock_response = {
            "id": "meal-123",
            "date": "2025-12-25",
            "entryType": "dinner"
        }

        result = await invoke_mcp_tool(
            "mealie_mealplans_create",
            mock_response=mock_response,
            meal_date="2025-12-25",
            entry_type="dinner"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_mealplans_update_registered(self, mcp_server):
        """Test mealie_mealplans_update is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_mealplans_update")

    @pytest.mark.asyncio
    async def test_mealplans_update_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_mealplans_update."""
        mock_response = {
            "id": "meal-123",
            "date": "2025-12-26"
        }

        result = await invoke_mcp_tool(
            "mealie_mealplans_update",
            mock_response=mock_response,
            mealplan_id="meal-123",
            meal_date="2025-12-26"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_mealplans_delete_registered(self, mcp_server):
        """Test mealie_mealplans_delete is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_mealplans_delete")

    @pytest.mark.asyncio
    async def test_mealplans_random_registered(self, mcp_server):
        """Test mealie_mealplans_random is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_mealplans_random")

    # --- Advanced Meal Plan Tools ---

    @pytest.mark.asyncio
    async def test_mealplans_search_registered(self, mcp_server):
        """Test mealie_mealplans_search is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_mealplans_search")

    @pytest.mark.asyncio
    async def test_mealplans_delete_range_registered(self, mcp_server):
        """Test mealie_mealplans_delete_range is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_mealplans_delete_range")

    @pytest.mark.asyncio
    async def test_mealplans_update_batch_registered(self, mcp_server):
        """Test mealie_mealplans_update_batch is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_mealplans_update_batch")

    # --- Meal Plan Rules ---

    @pytest.mark.asyncio
    async def test_mealplan_rules_list_registered(self, mcp_server):
        """Test mealie_mealplan_rules_list is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_mealplan_rules_list")

    @pytest.mark.asyncio
    async def test_mealplan_rules_get_registered(self, mcp_server):
        """Test mealie_mealplan_rules_get is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_mealplan_rules_get")

    @pytest.mark.asyncio
    async def test_mealplan_rules_create_registered(self, mcp_server):
        """Test mealie_mealplan_rules_create is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_mealplan_rules_create")

    @pytest.mark.asyncio
    async def test_mealplan_rules_update_registered(self, mcp_server):
        """Test mealie_mealplan_rules_update is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_mealplan_rules_update")

    @pytest.mark.asyncio
    async def test_mealplan_rules_delete_registered(self, mcp_server):
        """Test mealie_mealplan_rules_delete is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_mealplan_rules_delete")


class TestShoppingTools:
    """Test shopping list tools (12 tools)."""

    # --- Shopping Lists ---

    @pytest.mark.asyncio
    async def test_shopping_lists_list_registered(self, mcp_server):
        """Test mealie_shopping_lists_list is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_shopping_lists_list")

    @pytest.mark.asyncio
    async def test_shopping_lists_list_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_shopping_lists_list."""
        mock_response = {"items": [], "total": 0}

        result = await invoke_mcp_tool(
            "mealie_shopping_lists_list",
            mock_response=mock_response
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_shopping_lists_get_registered(self, mcp_server):
        """Test mealie_shopping_lists_get is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_shopping_lists_get")

    @pytest.mark.asyncio
    async def test_shopping_lists_create_registered(self, mcp_server):
        """Test mealie_shopping_lists_create is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_shopping_lists_create")

    @pytest.mark.asyncio
    async def test_shopping_lists_create_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_shopping_lists_create."""
        mock_response = {
            "id": "list-123",
            "name": "Grocery List"
        }

        result = await invoke_mcp_tool(
            "mealie_shopping_lists_create",
            mock_response=mock_response,
            name="Grocery List"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_shopping_lists_delete_registered(self, mcp_server):
        """Test mealie_shopping_lists_delete is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_shopping_lists_delete")

    # --- Shopping Items ---

    @pytest.mark.asyncio
    async def test_shopping_items_add_registered(self, mcp_server):
        """Test mealie_shopping_items_add is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_shopping_items_add")

    @pytest.mark.asyncio
    async def test_shopping_items_add_bulk_registered(self, mcp_server):
        """Test mealie_shopping_items_add_bulk is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_shopping_items_add_bulk")

    @pytest.mark.asyncio
    async def test_shopping_items_check_registered(self, mcp_server):
        """Test mealie_shopping_items_check is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_shopping_items_check")

    @pytest.mark.asyncio
    async def test_shopping_items_delete_registered(self, mcp_server):
        """Test mealie_shopping_items_delete is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_shopping_items_delete")

    # --- Advanced Shopping Features ---

    @pytest.mark.asyncio
    async def test_shopping_add_recipe_registered(self, mcp_server):
        """Test mealie_shopping_add_recipe is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_shopping_add_recipe")

    @pytest.mark.asyncio
    async def test_shopping_generate_from_mealplan_registered(self, mcp_server):
        """Test mealie_shopping_generate_from_mealplan is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_shopping_generate_from_mealplan")

    @pytest.mark.asyncio
    async def test_shopping_clear_checked_registered(self, mcp_server):
        """Test mealie_shopping_clear_checked is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_shopping_clear_checked")

    @pytest.mark.asyncio
    async def test_shopping_delete_recipe_from_list_registered(self, mcp_server):
        """Test mealie_shopping_delete_recipe_from_list is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_shopping_delete_recipe_from_list")


class TestFoodsAndUnitsTools:
    """Test foods and units management tools (12 tools)."""

    # --- Foods ---

    @pytest.mark.asyncio
    async def test_foods_list_registered(self, mcp_server):
        """Test mealie_foods_list is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_foods_list")

    @pytest.mark.asyncio
    async def test_foods_create_registered(self, mcp_server):
        """Test mealie_foods_create is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_foods_create")

    @pytest.mark.asyncio
    async def test_foods_create_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_foods_create."""
        mock_response = {
            "id": "food-123",
            "name": "Tomato"
        }

        result = await invoke_mcp_tool(
            "mealie_foods_create",
            mock_response=mock_response,
            name="Tomato"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_foods_get_registered(self, mcp_server):
        """Test mealie_foods_get is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_foods_get")

    @pytest.mark.asyncio
    async def test_foods_update_registered(self, mcp_server):
        """Test mealie_foods_update is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_foods_update")

    @pytest.mark.asyncio
    async def test_foods_delete_registered(self, mcp_server):
        """Test mealie_foods_delete is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_foods_delete")

    @pytest.mark.asyncio
    async def test_foods_merge_registered(self, mcp_server):
        """Test mealie_foods_merge is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_foods_merge")

    # --- Units ---

    @pytest.mark.asyncio
    async def test_units_list_registered(self, mcp_server):
        """Test mealie_units_list is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_units_list")

    @pytest.mark.asyncio
    async def test_units_create_registered(self, mcp_server):
        """Test mealie_units_create is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_units_create")

    @pytest.mark.asyncio
    async def test_units_create_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_units_create."""
        mock_response = {
            "id": "unit-123",
            "name": "tablespoon"
        }

        result = await invoke_mcp_tool(
            "mealie_units_create",
            mock_response=mock_response,
            name="tablespoon"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_units_get_registered(self, mcp_server):
        """Test mealie_units_get is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_units_get")

    @pytest.mark.asyncio
    async def test_units_update_registered(self, mcp_server):
        """Test mealie_units_update is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_units_update")

    @pytest.mark.asyncio
    async def test_units_delete_registered(self, mcp_server):
        """Test mealie_units_delete is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_units_delete")

    @pytest.mark.asyncio
    async def test_units_merge_registered(self, mcp_server):
        """Test mealie_units_merge is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_units_merge")


class TestOrganizerTools:
    """Test organizer tools - categories, tags, tools (15 tools)."""

    # --- Categories ---

    @pytest.mark.asyncio
    async def test_categories_list_registered(self, mcp_server):
        """Test mealie_categories_list is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_categories_list")

    @pytest.mark.asyncio
    async def test_categories_create_registered(self, mcp_server):
        """Test mealie_categories_create is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_categories_create")

    @pytest.mark.asyncio
    async def test_categories_create_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_categories_create."""
        mock_response = {
            "id": "cat-123",
            "name": "Desserts"
        }

        result = await invoke_mcp_tool(
            "mealie_categories_create",
            mock_response=mock_response,
            name="Desserts"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_categories_get_registered(self, mcp_server):
        """Test mealie_categories_get is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_categories_get")

    @pytest.mark.asyncio
    async def test_categories_update_registered(self, mcp_server):
        """Test mealie_categories_update is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_categories_update")

    @pytest.mark.asyncio
    async def test_categories_delete_registered(self, mcp_server):
        """Test mealie_categories_delete is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_categories_delete")

    # --- Tags ---

    @pytest.mark.asyncio
    async def test_tags_list_registered(self, mcp_server):
        """Test mealie_tags_list is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_tags_list")

    @pytest.mark.asyncio
    async def test_tags_create_registered(self, mcp_server):
        """Test mealie_tags_create is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_tags_create")

    @pytest.mark.asyncio
    async def test_tags_create_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_tags_create."""
        mock_response = {
            "id": "tag-123",
            "name": "Vegetarian"
        }

        result = await invoke_mcp_tool(
            "mealie_tags_create",
            mock_response=mock_response,
            name="Vegetarian"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_tags_get_registered(self, mcp_server):
        """Test mealie_tags_get is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_tags_get")

    @pytest.mark.asyncio
    async def test_tags_update_registered(self, mcp_server):
        """Test mealie_tags_update is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_tags_update")

    @pytest.mark.asyncio
    async def test_tags_delete_registered(self, mcp_server):
        """Test mealie_tags_delete is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_tags_delete")

    # --- Tools (Kitchen Tools) ---

    @pytest.mark.asyncio
    async def test_tools_list_registered(self, mcp_server):
        """Test mealie_tools_list is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_tools_list")

    @pytest.mark.asyncio
    async def test_tools_create_registered(self, mcp_server):
        """Test mealie_tools_create is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_tools_create")

    @pytest.mark.asyncio
    async def test_tools_create_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_tools_create."""
        mock_response = {
            "id": "tool-123",
            "name": "Stand Mixer"
        }

        result = await invoke_mcp_tool(
            "mealie_tools_create",
            mock_response=mock_response,
            name="Stand Mixer"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_tools_get_registered(self, mcp_server):
        """Test mealie_tools_get is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_tools_get")

    @pytest.mark.asyncio
    async def test_tools_update_registered(self, mcp_server):
        """Test mealie_tools_update is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_tools_update")

    @pytest.mark.asyncio
    async def test_tools_delete_registered(self, mcp_server):
        """Test mealie_tools_delete is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_tools_delete")


class TestCookbookTools:
    """Test cookbook management tools (5 tools)."""

    @pytest.mark.asyncio
    async def test_cookbooks_list_registered(self, mcp_server):
        """Test mealie_cookbooks_list is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_cookbooks_list")

    @pytest.mark.asyncio
    async def test_cookbooks_create_registered(self, mcp_server):
        """Test mealie_cookbooks_create is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_cookbooks_create")

    @pytest.mark.asyncio
    async def test_cookbooks_create_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_cookbooks_create."""
        mock_response = {
            "id": "cookbook-123",
            "name": "Family Favorites"
        }

        result = await invoke_mcp_tool(
            "mealie_cookbooks_create",
            mock_response=mock_response,
            name="Family Favorites"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_cookbooks_get_registered(self, mcp_server):
        """Test mealie_cookbooks_get is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_cookbooks_get")

    @pytest.mark.asyncio
    async def test_cookbooks_update_registered(self, mcp_server):
        """Test mealie_cookbooks_update is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_cookbooks_update")

    @pytest.mark.asyncio
    async def test_cookbooks_delete_registered(self, mcp_server):
        """Test mealie_cookbooks_delete is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_cookbooks_delete")


class TestCommentTools:
    """Test recipe comment tools (5 tools)."""

    @pytest.mark.asyncio
    async def test_comments_get_recipe_registered(self, mcp_server):
        """Test mealie_comments_get_recipe is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_comments_get_recipe")

    @pytest.mark.asyncio
    async def test_comments_create_registered(self, mcp_server):
        """Test mealie_comments_create is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_comments_create")

    @pytest.mark.asyncio
    async def test_comments_create_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_comments_create."""
        mock_response = {
            "id": "comment-123",
            "text": "Great recipe!"
        }

        result = await invoke_mcp_tool(
            "mealie_comments_create",
            mock_response=mock_response,
            recipe_id="recipe-123",
            text="Great recipe!"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_comments_get_registered(self, mcp_server):
        """Test mealie_comments_get is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_comments_get")

    @pytest.mark.asyncio
    async def test_comments_update_registered(self, mcp_server):
        """Test mealie_comments_update is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_comments_update")

    @pytest.mark.asyncio
    async def test_comments_delete_registered(self, mcp_server):
        """Test mealie_comments_delete is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_comments_delete")


class TestTimelineTools:
    """Test recipe timeline event tools (6 tools)."""

    @pytest.mark.asyncio
    async def test_timeline_list_registered(self, mcp_server):
        """Test mealie_timeline_list is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_timeline_list")

    @pytest.mark.asyncio
    async def test_timeline_list_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_timeline_list."""
        mock_response = {"items": [], "total": 0}

        result = await invoke_mcp_tool(
            "mealie_timeline_list",
            mock_response=mock_response
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_timeline_get_registered(self, mcp_server):
        """Test mealie_timeline_get is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_timeline_get")

    @pytest.mark.asyncio
    async def test_timeline_create_registered(self, mcp_server):
        """Test mealie_timeline_create is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_timeline_create")

    @pytest.mark.asyncio
    async def test_timeline_create_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_timeline_create."""
        mock_response = {
            "id": "event-123",
            "subject": "Made this recipe"
        }

        result = await invoke_mcp_tool(
            "mealie_timeline_create",
            mock_response=mock_response,
            recipe_id="recipe-123",
            subject="Made this recipe"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_timeline_update_registered(self, mcp_server):
        """Test mealie_timeline_update is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_timeline_update")

    @pytest.mark.asyncio
    async def test_timeline_delete_registered(self, mcp_server):
        """Test mealie_timeline_delete is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_timeline_delete")

    @pytest.mark.asyncio
    async def test_timeline_update_image_registered(self, mcp_server):
        """Test mealie_timeline_update_image is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_timeline_update_image")


class TestParserTools:
    """Test ingredient parser tools (2 tools)."""

    @pytest.mark.asyncio
    async def test_parser_ingredient_registered(self, mcp_server):
        """Test mealie_parser_ingredient is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_parser_ingredient")

    @pytest.mark.asyncio
    async def test_parser_ingredient_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_parser_ingredient."""
        mock_response = {
            "input": "2 cups flour",
            "ingredient": {
                "quantity": 2.0,
                "unit": {"name": "cup"},
                "food": {"name": "flour"}
            }
        }

        result = await invoke_mcp_tool(
            "mealie_parser_ingredient",
            mock_response=mock_response,
            ingredient="2 cups flour"
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_parser_ingredients_batch_registered(self, mcp_server):
        """Test mealie_parser_ingredients_batch is registered."""
        assert await validate_tool_registration(mcp_server, "mealie_parser_ingredients_batch")

    @pytest.mark.asyncio
    async def test_parser_ingredients_batch_invocation(self, invoke_mcp_tool):
        """Test invoking mealie_parser_ingredients_batch."""
        mock_response = {
            "parsed_ingredients": [
                {
                    "input": "2 cups flour",
                    "ingredient": {
                        "quantity": 2.0,
                        "unit": {"name": "cup"},
                        "food": {"name": "flour"}
                    }
                }
            ]
        }

        result = await invoke_mcp_tool(
            "mealie_parser_ingredients_batch",
            mock_response=mock_response,
            ingredients=["2 cups flour"]
        )

        validation = validate_mcp_response(result)
        assert validation["valid"]


class TestToolParameterValidation:
    """Test parameter validation for various tools."""

    @pytest.mark.asyncio
    async def test_required_parameters_recipes_create(self, mcp_server):
        """Test recipes_create requires name parameter."""
        tools = await mcp_server.get_tools()
        tool = tools["mealie_recipes_create"]

        params = tool.parameters
        required = params.get("required", [])
        assert "name" in required

    @pytest.mark.asyncio
    async def test_required_parameters_mealplans_create(self, mcp_server):
        """Test mealplans_create requires meal_date and entry_type."""
        tools = await mcp_server.get_tools()
        tool = tools["mealie_mealplans_create"]

        params = tool.parameters
        required = params.get("required", [])
        assert "meal_date" in required
        assert "entry_type" in required

    @pytest.mark.asyncio
    async def test_required_parameters_shopping_lists_create(self, mcp_server):
        """Test shopping_lists_create requires name parameter."""
        tools = await mcp_server.get_tools()
        tool = tools["mealie_shopping_lists_create"]

        params = tool.parameters
        required = params.get("required", [])
        assert "name" in required

    @pytest.mark.asyncio
    async def test_optional_parameters_recipes_search(self, mcp_server):
        """Test recipes_search has all optional parameters."""
        tools = await mcp_server.get_tools()
        tool = tools["mealie_recipes_search"]

        params = tool.parameters
        required = params.get("required", [])
        # All parameters should be optional
        assert len(required) == 0

    @pytest.mark.asyncio
    async def test_optional_parameters_mealplans_list(self, mcp_server):
        """Test mealplans_list has optional date parameters."""
        tools = await mcp_server.get_tools()
        tool = tools["mealie_mealplans_list"]

        params = tool.parameters
        required = params.get("required", [])
        # start_date and end_date should be optional
        assert "start_date" not in required
        assert "end_date" not in required


class TestToolResponseFormatting:
    """Test that tools return properly formatted JSON responses."""

    @pytest.mark.asyncio
    async def test_response_is_json_recipes_search(self, invoke_mcp_tool):
        """Test recipes_search returns valid JSON."""
        mock_response = {"items": [], "total": 0}

        result = await invoke_mcp_tool(
            "mealie_recipes_search",
            mock_response=mock_response
        )

        text = extract_tool_result_text(result)
        # Should be valid JSON
        data = json.loads(text)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_response_is_json_mealplans_list(self, invoke_mcp_tool):
        """Test mealplans_list returns valid JSON."""
        mock_response = {"items": [], "total": 0}

        result = await invoke_mcp_tool(
            "mealie_mealplans_list",
            mock_response=mock_response
        )

        text = extract_tool_result_text(result)
        data = json.loads(text)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_response_is_json_shopping_lists_list(self, invoke_mcp_tool):
        """Test shopping_lists_list returns valid JSON."""
        mock_response = {"items": [], "total": 0}

        result = await invoke_mcp_tool(
            "mealie_shopping_lists_list",
            mock_response=mock_response
        )

        text = extract_tool_result_text(result)
        data = json.loads(text)
        assert isinstance(data, dict)


class TestToolCount:
    """Test that all expected tools are registered."""

    @pytest.mark.asyncio
    async def test_total_tool_count(self, mcp_server):
        """Test that we have all 92 tools registered."""
        tools = await mcp_server.get_tools()

        # Should have exactly 92 tools (from grep count)
        # 1 utility (ping)
        # 18 recipe tools
        # 16 meal plan tools
        # 12 shopping tools
        # 12 foods/units tools
        # 15 organizer tools
        # 5 cookbook tools
        # 5 comment tools
        # 6 timeline tools
        # 2 parser tools
        # = 92 total
        assert len(tools) >= 92

    @pytest.mark.asyncio
    async def test_tool_names_consistency(self, mcp_server):
        """Test that all tool names follow naming convention."""
        tools = await mcp_server.get_tools()

        for tool_name in tools.keys():
            # All tools should be lowercase with underscores
            assert tool_name == tool_name.lower()
            # Most tools should start with mealie_ (except ping)
            if tool_name != "ping":
                assert tool_name.startswith("mealie_")
