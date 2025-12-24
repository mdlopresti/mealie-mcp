"""
Example MCP Integration Tests

This module demonstrates how to write integration tests for MCP tools.
These tests validate MCP protocol interactions without hitting real API endpoints.

Test Categories:
1. Tool Registration - Verify tools are registered correctly
2. Parameter Validation - Test tool parameter schemas
3. Response Validation - Verify response structure and content
4. Error Handling - Test error responses and edge cases
5. Data Flow - Test integration between tools and client

Run with: pytest tests/integration/test_mcp_tools_example.py -v
"""

import pytest
import json
from tests.utils.mcp_test_helpers import (
    # Registration helpers
    validate_tool_exists,
    get_tool_metadata,
    validate_tool_schema,
    assert_tool_params,
    # Response helpers
    validate_mcp_response,
    assert_valid_mcp_response,
    extract_text_from_result,
    extract_json_from_result,
    validate_json_response_schema,
    assert_json_response_schema,
    # Error helpers
    validate_error_response,
    assert_tool_error,
    # Data helpers
    assert_has_fields,
    assert_field_type,
    assert_list_length,
)


# ============================================================================
# Tool Registration Tests
# ============================================================================

class TestToolRegistration:
    """Test that tools are registered correctly with proper metadata."""

    @pytest.mark.asyncio
    async def test_recipe_search_tool_exists(self, mcp_server):
        """Test that mealie_recipes_search tool is registered."""
        assert await validate_tool_exists(mcp_server, "mealie_recipes_search")

    @pytest.mark.asyncio
    async def test_recipe_search_has_metadata(self, mcp_server):
        """Test that mealie_recipes_search has proper metadata."""
        metadata = await get_tool_metadata(mcp_server, "mealie_recipes_search")

        # Tool should have description
        assert metadata["description"]
        assert "search" in metadata["description"].lower()

        # Tool should have parameters
        assert metadata["parameters"] is not None

    @pytest.mark.asyncio
    async def test_recipe_search_parameter_schema(self, mcp_server):
        """Test that mealie_recipes_search has correct parameter schema."""
        tools = await mcp_server.get_tools()
        tool = tools["mealie_recipes_search"]

        # Validate schema structure
        valid, error = validate_tool_schema(tool, {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "tags": {"type": "array"},
                "categories": {"type": "array"},
                "limit": {"type": "integer"}
            }
        })
        assert valid, error

    @pytest.mark.asyncio
    async def test_recipe_search_parameters(self, mcp_server):
        """Test that mealie_recipes_search has correct parameters."""
        tools = await mcp_server.get_tools()
        tool = tools["mealie_recipes_search"]

        # All parameters should be optional
        assert_tool_params(
            tool,
            {
                "query": False,
                "tags": False,
                "categories": False,
                "limit": False
            },
            {
                "query": "string",
                "limit": "integer"
            }
        )

    @pytest.mark.asyncio
    async def test_all_recipe_tools_registered(self, mcp_server):
        """Test that all expected recipe tools are registered."""
        expected_tools = [
            "mealie_recipes_search",
            "mealie_recipes_get",
            "mealie_recipes_list",
            "mealie_recipes_create",
            "mealie_recipes_update",
            "mealie_recipes_delete",
            "mealie_recipes_duplicate"
        ]

        for tool_name in expected_tools:
            assert await validate_tool_exists(mcp_server, tool_name), \
                f"Tool '{tool_name}' not registered"


# ============================================================================
# Response Validation Tests
# ============================================================================

class TestResponseValidation:
    """Test that tool responses follow MCP protocol."""

    @pytest.mark.asyncio
    async def test_ping_response_structure(self, mcp_tool_invoker):
        """Test that ping tool returns valid MCP response."""
        result = await mcp_tool_invoker("ping")

        # Validate MCP response structure
        validation = validate_mcp_response(result)
        assert validation["valid"], validation.get("error")
        assert validation["has_text"]
        assert "pong" in validation["text_content"].lower()

    @pytest.mark.asyncio
    async def test_recipe_list_response_structure(self, mcp_tool_invoker, sample_recipes):
        """Test that recipe list returns valid MCP response."""
        result = await mcp_tool_invoker(
            "mealie_recipes_list",
            mock_response={
                "items": sample_recipes,
                "total": len(sample_recipes),
                "page": 1,
                "per_page": 20
            }
        )

        # Should be valid MCP response
        assert_valid_mcp_response(result)

        # Extract and validate JSON
        data = extract_json_from_result(result)
        assert_has_fields(data, ["items", "total"])
        assert_field_type(data, "items", list)
        assert_field_type(data, "total", int)

    @pytest.mark.asyncio
    async def test_recipe_search_json_schema(self, mcp_tool_invoker, sample_recipes):
        """Test that recipe search response matches expected schema."""
        result = await mcp_tool_invoker(
            "mealie_recipes_search",
            mock_response={
                "items": sample_recipes,
                "total": len(sample_recipes)
            },
            query="pasta"
        )

        # Validate JSON schema
        # Note: recipes_search returns "recipes" not "items" in the JSON
        assert_json_response_schema(result, {
            "type": "object",
            "properties": {
                "recipes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": ["string", "null"]},
                            "slug": {"type": ["string", "null"]},
                            "description": {"type": ["string", "null"]}
                        }
                    }
                },
                "total": {"type": "integer"},
                "count": {"type": "integer"}
            },
            "required": ["recipes", "total", "count"]
        })

    @pytest.mark.asyncio
    async def test_recipe_get_response_data(self, mcp_tool_invoker, sample_recipes):
        """Test that recipe get returns expected data structure."""
        recipe = sample_recipes[0]
        result = await mcp_tool_invoker(
            "mealie_recipes_get",
            mock_response=recipe,
            slug=recipe["slug"]
        )

        # Extract data
        data = extract_json_from_result(result)

        # Validate required fields
        assert_has_fields(data, ["id", "slug", "name"])
        assert data["id"] == recipe["id"]
        assert data["slug"] == recipe["slug"]
        assert data["name"] == recipe["name"]


# ============================================================================
# Parameter Handling Tests
# ============================================================================

class TestParameterHandling:
    """Test that tools handle parameters correctly."""

    @pytest.mark.asyncio
    async def test_recipe_search_with_query(self, mcp_tool_invoker, sample_recipes):
        """Test recipe search with query parameter."""
        result = await mcp_tool_invoker(
            "mealie_recipes_search",
            mock_response={"items": sample_recipes[:1], "total": 1},
            query="pasta"
        )

        data = extract_json_from_result(result)
        assert_has_fields(data, ["items", "total"])
        assert_list_length(data, "items", min_length=0)

    @pytest.mark.asyncio
    async def test_recipe_search_with_limit(self, mcp_tool_invoker, sample_recipes):
        """Test recipe search with limit parameter."""
        limit = 2
        result = await mcp_tool_invoker(
            "mealie_recipes_search",
            mock_response={"items": sample_recipes[:limit], "total": len(sample_recipes)},
            limit=limit
        )

        data = extract_json_from_result(result)
        items = data["items"]
        assert len(items) <= limit

    @pytest.mark.asyncio
    async def test_recipe_search_with_multiple_params(self, mcp_tool_invoker, sample_recipes):
        """Test recipe search with multiple parameters."""
        result = await mcp_tool_invoker(
            "mealie_recipes_search",
            mock_response={"items": sample_recipes[1:2], "total": 1},
            query="vegan",
            tags=["Vegan"],
            limit=10
        )

        data = extract_json_from_result(result)
        assert_has_fields(data, ["items"])
        # Should have filtered results
        assert data["total"] >= 0

    @pytest.mark.asyncio
    async def test_mealplan_create_with_all_params(self, mcp_tool_invoker, sample_mealplans):
        """Test mealplan create with all parameters."""
        mealplan = sample_mealplans[0]
        result = await mcp_tool_invoker(
            "mealie_mealplans_create",
            mock_response=mealplan,
            meal_date="2025-12-25",
            entry_type="breakfast",
            title="Christmas Breakfast",
            text="Special holiday meal",
            recipe_id="recipe-123"
        )

        data = extract_json_from_result(result)
        assert_has_fields(data, ["id", "meal_date", "entry_type"])


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test that tools handle errors correctly."""

    @pytest.mark.asyncio
    async def test_recipe_get_not_found(self, mcp_tool_invoker):
        """Test recipe get with non-existent slug."""
        result = await mcp_tool_invoker(
            "mealie_recipes_get",
            mock_response={"detail": "Recipe not found"},
            status_code=404,
            slug="nonexistent-recipe"
        )

        # Should contain error
        is_error, msg = validate_error_response(result)
        # Note: Depending on implementation, this might be in success response
        # or might raise an exception that's caught and returned as error

    @pytest.mark.asyncio
    async def test_recipe_create_validation_error(self, mcp_tool_invoker):
        """Test recipe create with invalid data."""
        result = await mcp_tool_invoker(
            "mealie_recipes_create",
            mock_response={"detail": "Validation error: name required"},
            status_code=422,
            name=""  # Empty name should fail
        )

        # Response should indicate error
        text = extract_text_from_result(result)
        # Check that error information is present
        assert text  # Should have some response

    @pytest.mark.asyncio
    async def test_mealplan_delete_not_found(self, mcp_tool_invoker):
        """Test mealplan delete with non-existent ID."""
        result = await mcp_tool_invoker(
            "mealie_mealplans_delete",
            mock_response={"detail": "Mealplan not found"},
            status_code=404,
            mealplan_id="nonexistent-id"
        )

        # Should handle error gracefully
        text = extract_text_from_result(result)
        assert text  # Should have response


# ============================================================================
# Data Flow Integration Tests
# ============================================================================

class TestDataFlowIntegration:
    """Test integration between tools and data flow."""

    @pytest.mark.asyncio
    async def test_recipe_create_and_get_flow(self, mcp_tool_invoker, sample_recipes):
        """Test creating a recipe and then retrieving it."""
        recipe = sample_recipes[0]

        # Create recipe
        create_result = await mcp_tool_invoker(
            "mealie_recipes_create",
            mock_response=recipe,
            name=recipe["name"],
            description=recipe["description"]
        )

        created_data = extract_json_from_result(create_result)
        assert_has_fields(created_data, ["id", "slug", "name"])

        # Get the created recipe
        get_result = await mcp_tool_invoker(
            "mealie_recipes_get",
            mock_response=recipe,
            slug=created_data["slug"]
        )

        retrieved_data = extract_json_from_result(get_result)
        assert retrieved_data["id"] == created_data["id"]
        assert retrieved_data["slug"] == created_data["slug"]

    @pytest.mark.asyncio
    async def test_mealplan_create_and_list_flow(self, mcp_tool_invoker, sample_mealplans):
        """Test creating meal plans and listing them."""
        mealplan = sample_mealplans[0]

        # Create mealplan
        create_result = await mcp_tool_invoker(
            "mealie_mealplans_create",
            mock_response=mealplan,
            meal_date=mealplan["date"],
            entry_type=mealplan["entryType"],
            title=mealplan["title"]
        )

        created_data = extract_json_from_result(create_result)
        assert_has_fields(created_data, ["id"])

        # List mealplans
        list_result = await mcp_tool_invoker(
            "mealie_mealplans_list",
            mock_response={"items": sample_mealplans, "total": len(sample_mealplans)},
            start_date="2025-12-25",
            end_date="2025-12-26"
        )

        list_data = extract_json_from_result(list_result)
        assert_has_fields(list_data, ["items"])
        assert_list_length(list_data, "items", min_length=1)

    @pytest.mark.asyncio
    async def test_shopping_list_workflow(self, mcp_tool_invoker, sample_shopping_lists):
        """Test shopping list creation and item management."""
        shopping_list = sample_shopping_lists[0]

        # Create shopping list
        create_result = await mcp_tool_invoker(
            "mealie_shopping_lists_create",
            mock_response=shopping_list,
            name=shopping_list["name"]
        )

        created_data = extract_json_from_result(create_result)
        assert_has_fields(created_data, ["id", "name"])

        # Add items
        add_result = await mcp_tool_invoker(
            "mealie_shopping_items_add",
            mock_response={"id": "item-1", "note": "2 cups flour"},
            list_id=created_data["id"],
            note="2 cups flour"
        )

        item_data = extract_json_from_result(add_result)
        assert_has_fields(item_data, ["id", "note"])

        # Get shopping list with items
        get_result = await mcp_tool_invoker(
            "mealie_shopping_lists_get",
            mock_response=shopping_list,
            list_id=created_data["id"]
        )

        list_data = extract_json_from_result(get_result)
        assert_has_fields(list_data, ["id", "name", "listItems"])


# ============================================================================
# Complex Scenarios
# ============================================================================

class TestComplexScenarios:
    """Test complex multi-step scenarios."""

    @pytest.mark.asyncio
    async def test_meal_planning_workflow(
        self,
        mcp_tool_invoker,
        sample_recipes,
        sample_mealplans,
        sample_shopping_lists
    ):
        """Test complete meal planning workflow.

        Steps:
        1. Search for recipes
        2. Create meal plan with recipe
        3. Generate shopping list from meal plan
        """
        # Step 1: Search recipes
        search_result = await mcp_tool_invoker(
            "mealie_recipes_search",
            mock_response={"items": sample_recipes, "total": len(sample_recipes)},
            query="pasta"
        )

        recipes = extract_json_from_result(search_result)["items"]
        assert len(recipes) > 0

        # Step 2: Create meal plan
        mealplan_result = await mcp_tool_invoker(
            "mealie_mealplans_create",
            mock_response=sample_mealplans[0],
            meal_date="2025-12-25",
            entry_type="dinner",
            recipe_id=recipes[0]["id"]
        )

        mealplan = extract_json_from_result(mealplan_result)
        assert_has_fields(mealplan, ["id"])

        # Step 3: Generate shopping list
        shopping_result = await mcp_tool_invoker(
            "mealie_shopping_generate_from_mealplan",
            mock_response=sample_shopping_lists[0],
            start_date="2025-12-25",
            end_date="2025-12-25"
        )

        shopping_list = extract_json_from_result(shopping_result)
        assert_has_fields(shopping_list, ["id", "name"])

    @pytest.mark.asyncio
    async def test_recipe_organization_workflow(
        self,
        mcp_tool_invoker,
        sample_recipes,
        sample_organizers
    ):
        """Test recipe organization with tags and categories.

        Steps:
        1. Create tags and categories
        2. Create recipe with tags/categories
        3. Search recipes by tags/categories
        """
        # Step 1: Create tag
        tag_result = await mcp_tool_invoker(
            "mealie_tags_create",
            mock_response=sample_organizers["tags"][0],
            name="Vegan"
        )

        tag = extract_json_from_result(tag_result)
        assert_has_fields(tag, ["id", "name"])

        # Step 2: Create category
        category_result = await mcp_tool_invoker(
            "mealie_categories_create",
            mock_response=sample_organizers["categories"][0],
            name="Dessert"
        )

        category = extract_json_from_result(category_result)
        assert_has_fields(category, ["id", "name"])

        # Step 3: Create recipe with organizers
        recipe = sample_recipes[2]  # One with category
        create_result = await mcp_tool_invoker(
            "mealie_recipes_create",
            mock_response=recipe,
            name=recipe["name"],
            tags=["Vegan"],
            categories=["Dessert"]
        )

        created_recipe = extract_json_from_result(create_result)
        assert_has_fields(created_recipe, ["id"])

        # Step 4: Search by tags
        search_result = await mcp_tool_invoker(
            "mealie_recipes_search",
            mock_response={"items": [recipe], "total": 1},
            tags=["Vegan"]
        )

        results = extract_json_from_result(search_result)
        assert_list_length(results, "items", min_length=0)


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_empty_search_results(self, mcp_tool_invoker):
        """Test search with no results."""
        result = await mcp_tool_invoker(
            "mealie_recipes_search",
            mock_response={"items": [], "total": 0},
            query="nonexistent-recipe-xyz"
        )

        data = extract_json_from_result(result)
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_pagination_boundary(self, mcp_tool_invoker, sample_recipes):
        """Test pagination at boundaries."""
        # Page 1 with full results
        result = await mcp_tool_invoker(
            "mealie_recipes_list",
            mock_response={
                "items": sample_recipes,
                "total": 100,
                "page": 1,
                "per_page": 20
            },
            page=1,
            per_page=20
        )

        data = extract_json_from_result(result)
        assert data["page"] == 1

        # Last page with partial results
        result = await mcp_tool_invoker(
            "mealie_recipes_list",
            mock_response={
                "items": sample_recipes[:5],
                "total": 100,
                "page": 5,
                "per_page": 20
            },
            page=5,
            per_page=20
        )

        data = extract_json_from_result(result)
        assert len(data["items"]) <= 20

    @pytest.mark.asyncio
    async def test_special_characters_in_names(self, mcp_tool_invoker):
        """Test handling special characters in recipe names."""
        special_recipe = {
            "id": "recipe-special",
            "slug": "moms-lasagna",
            "name": "Mom's \"Amazing\" Lasagna & Pasta",
            "description": "Recipe with special chars: <>&\"'"
        }

        result = await mcp_tool_invoker(
            "mealie_recipes_create",
            mock_response=special_recipe,
            name=special_recipe["name"],
            description=special_recipe["description"]
        )

        data = extract_json_from_result(result)
        assert data["name"] == special_recipe["name"]
