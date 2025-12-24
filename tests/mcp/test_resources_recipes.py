"""
Tests for Recipe MCP Resources.

Tests for recipes://list and recipes://{slug} resource providers.
"""

import pytest
import respx
from httpx import Response
from tests.mcp.helpers import validate_resource_uri


class TestRecipeResourceRegistration:
    """Test that recipe resources are properly registered."""

    @pytest.mark.asyncio
    async def test_recipes_list_resource_registered(self, mcp_server):
        """Test that recipes://list resource is registered."""
        resources = await mcp_server.get_resources()
        assert "recipes://list" in resources

    @pytest.mark.asyncio
    async def test_recipes_slug_resource_registered(self, mcp_server):
        """Test that recipes://{slug} templated resource is registered."""
        templates = await mcp_server.get_resource_templates()
        assert "recipes://{slug}" in templates

    @pytest.mark.asyncio
    async def test_recipes_list_uri_format(self, mcp_server):
        """Test that recipes://list URI follows MCP format."""
        resources = await mcp_server.get_resources()
        assert validate_resource_uri("recipes://list")

    @pytest.mark.asyncio
    async def test_recipes_slug_uri_format(self):
        """Test that recipes://{slug} URI follows MCP format."""
        # Test with a sample slug
        assert validate_resource_uri("recipes://test-recipe")
        assert validate_resource_uri("recipes://my-recipe-123")

    @pytest.mark.asyncio
    async def test_recipes_list_has_description(self, mcp_server):
        """Test that recipes://list has a description."""
        resources = await mcp_server.get_resources()
        resource = resources["recipes://list"]
        assert resource.description is not None
        assert len(resource.description) > 0
        assert "recipe" in resource.description.lower()


class TestRecipesListResource:
    """Test recipes://list resource provider."""

    @pytest.mark.asyncio
    async def test_read_recipes_list_empty(self, mcp_server, mealie_env):
        """Test reading recipes://list with no recipes."""
        with respx.mock:
            # Mock empty response
            respx.get(url__startswith="https://test.mealie.example.com/api/recipes").mock(
                return_value=Response(200, json={"items": [], "total": 0})
            )

            resources = await mcp_server.get_resources()
            resource = resources["recipes://list"]
            content = await resource.read()

            assert isinstance(content, str)
            assert "# Recipes in Mealie" in content
            assert "Total Recipes" in content

    @pytest.mark.asyncio
    async def test_read_recipes_list_with_recipes(self, mcp_server, mealie_env):
        """Test reading recipes://list with multiple recipes."""
        with respx.mock:
            # Mock response with recipes
            mock_recipes = {
                "items": [
                    {
                        "name": "Pasta Carbonara",
                        "slug": "pasta-carbonara",
                        "recipeCategory": {"name": "Dinner"},
                        "tags": [{"name": "Italian"}, {"name": "Pasta"}]
                    },
                    {
                        "name": "Caesar Salad",
                        "slug": "caesar-salad",
                        "recipeCategory": {"name": "Salad"},
                        "tags": [{"name": "Healthy"}]
                    }
                ],
                "total": 2
            }
            respx.get(url__startswith="https://test.mealie.example.com/api/recipes").mock(
                return_value=Response(200, json=mock_recipes)
            )

            resources = await mcp_server.get_resources()
            resource = resources["recipes://list"]
            content = await resource.read()

            # Verify content structure
            assert "Total Recipes**: 2" in content
            assert "Pasta Carbonara" in content
            assert "pasta-carbonara" in content
            assert "Caesar Salad" in content
            assert "caesar-salad" in content

    @pytest.mark.asyncio
    async def test_read_recipes_list_organized_by_category(self, mcp_server, mealie_env):
        """Test that recipes://list organizes recipes by category."""
        with respx.mock:
            mock_recipes = {
                "items": [
                    {
                        "name": "Recipe 1",
                        "slug": "recipe-1",
                        "recipeCategory": {"name": "Dinner"},
                        "tags": []
                    },
                    {
                        "name": "Recipe 2",
                        "slug": "recipe-2",
                        "recipeCategory": {"name": "Dinner"},
                        "tags": []
                    },
                    {
                        "name": "Recipe 3",
                        "slug": "recipe-3",
                        "recipeCategory": {"name": "Breakfast"},
                        "tags": []
                    }
                ],
                "total": 3
            }
            respx.get(url__startswith="https://test.mealie.example.com/api/recipes").mock(
                return_value=Response(200, json=mock_recipes)
            )

            resources = await mcp_server.get_resources()
            resource = resources["recipes://list"]
            content = await resource.read()

            # Should have category headers
            assert "## Dinner" in content
            assert "## Breakfast" in content
            # Verify recipes are under correct categories
            assert content.index("## Dinner") < content.index("Recipe 1")
            assert content.index("## Breakfast") < content.index("Recipe 3")

    @pytest.mark.asyncio
    async def test_read_recipes_list_with_tags(self, mcp_server, mealie_env):
        """Test that recipes://list shows recipe tags."""
        with respx.mock:
            mock_recipes = {
                "items": [
                    {
                        "name": "Tagged Recipe",
                        "slug": "tagged-recipe",
                        "recipeCategory": {"name": "Dinner"},
                        "tags": [{"name": "Quick"}, {"name": "Easy"}]
                    }
                ],
                "total": 1
            }
            respx.get(url__startswith="https://test.mealie.example.com/api/recipes").mock(
                return_value=Response(200, json=mock_recipes)
            )

            resources = await mcp_server.get_resources()
            resource = resources["recipes://list"]
            content = await resource.read()

            # Should display tags
            assert "Quick" in content
            assert "Easy" in content

    @pytest.mark.asyncio
    async def test_read_recipes_list_uncategorized(self, mcp_server, mealie_env):
        """Test that uncategorized recipes are handled correctly."""
        with respx.mock:
            mock_recipes = {
                "items": [
                    {
                        "name": "Uncategorized Recipe",
                        "slug": "uncategorized-recipe",
                        "recipeCategory": None,
                        "tags": []
                    }
                ],
                "total": 1
            }
            respx.get(url__startswith="https://test.mealie.example.com/api/recipes").mock(
                return_value=Response(200, json=mock_recipes)
            )

            resources = await mcp_server.get_resources()
            resource = resources["recipes://list"]
            content = await resource.read()

            # Should have uncategorized section
            assert "## Uncategorized" in content
            assert "Uncategorized Recipe" in content

    @pytest.mark.asyncio
    async def test_read_recipes_list_pagination(self, mcp_server, mealie_env):
        """Test that recipes://list handles pagination."""
        with respx.mock:
            # First page
            page1_recipes = {
                "items": [{"name": f"Recipe {i}", "slug": f"recipe-{i}", "recipeCategory": {"name": "Test"}, "tags": []} for i in range(1, 101)],
                "total": 150
            }
            # Second page
            page2_recipes = {
                "items": [{"name": f"Recipe {i}", "slug": f"recipe-{i}", "recipeCategory": {"name": "Test"}, "tags": []} for i in range(101, 151)],
                "total": 150
            }

            # Mock both pages
            respx.get(url__startswith="https://test.mealie.example.com/api/recipes", params__contains={"page": "1"}).mock(
                return_value=Response(200, json=page1_recipes)
            )
            respx.get(url__startswith="https://test.mealie.example.com/api/recipes", params__contains={"page": "2"}).mock(
                return_value=Response(200, json=page2_recipes)
            )

            resources = await mcp_server.get_resources()
            resource = resources["recipes://list"]
            content = await resource.read()

            # Should fetch all pages
            assert "Total Recipes**: 150" in content
            assert "Recipe 1" in content
            assert "Recipe 150" in content

    @pytest.mark.asyncio
    async def test_read_recipes_list_api_error(self, mcp_server, mealie_env):
        """Test recipes://list handles API errors gracefully."""
        with respx.mock:
            # Mock 500 error
            respx.get(url__startswith="https://test.mealie.example.com/api/recipes").mock(
                return_value=Response(500, json={"error": "Internal server error"})
            )

            resources = await mcp_server.get_resources()
            resource = resources["recipes://list"]
            content = await resource.read()

            # Should return error message
            assert isinstance(content, str)
            assert "error" in content.lower() or "Error" in content


class TestRecipeDetailResource:
    """Test recipes://{slug} resource provider."""

    @pytest.mark.asyncio
    async def test_read_recipe_detail_basic(self, mcp_server, mealie_env):
        """Test reading a recipe detail resource."""
        with respx.mock:
            mock_recipe = {
                "name": "Test Recipe",
                "slug": "test-recipe",
                "description": "A test recipe",
                "recipeCategory": {"name": "Dinner"},
                "tags": [{"name": "Test"}],
                "recipeYield": "4 servings",
                "totalTime": "30 minutes",
                "prepTime": "10 minutes",
                "performTime": "20 minutes",
                "recipeIngredient": ["1 cup flour", "2 eggs"],
                "recipeInstructions": [
                    {"text": "Mix ingredients", "title": ""},
                    {"text": "Cook until done", "title": ""}
                ]
            }
            respx.get(url__regex=r".*\/api\/recipes\/test-recipe$").mock(
                return_value=Response(200, json=mock_recipe)
            )

            templates = await mcp_server.get_resource_templates()
            # Get the templated resource and read with parameter
            resource = templates["recipes://{slug}"]
            content = await resource.read({"slug": "test-recipe"})

            # Verify content structure
            assert "# Test Recipe" in content
            assert "A test recipe" in content
            assert "## Information" in content
            assert "## Ingredients" in content
            assert "## Instructions" in content

    @pytest.mark.asyncio
    async def test_read_recipe_detail_with_ingredients(self, mcp_server, mealie_env):
        """Test recipe detail includes ingredients."""
        with respx.mock:
            mock_recipe = {
                "name": "Recipe with Ingredients",
                "slug": "recipe-with-ingredients",
                "recipeIngredient": [
                    "2 cups flour",
                    "1 tsp salt",
                    "3 eggs"
                ]
            }
            respx.get(url__regex=r".*\/api\/recipes\/recipe-with-ingredients$").mock(
                return_value=Response(200, json=mock_recipe)
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["recipes://{slug}"]
            content = await resource.read({"slug": "recipe-with-ingredients"})

            # Verify ingredients are listed
            assert "2 cups flour" in content
            assert "1 tsp salt" in content
            assert "3 eggs" in content

    @pytest.mark.asyncio
    async def test_read_recipe_detail_structured_ingredients(self, mcp_server, mealie_env):
        """Test recipe detail with structured ingredients."""
        with respx.mock:
            mock_recipe = {
                "name": "Structured Recipe",
                "slug": "structured-recipe",
                "recipeIngredient": [
                    {
                        "quantity": "2",
                        "unit": {"name": "cups"},
                        "food": {"name": "flour"},
                        "note": "all-purpose"
                    }
                ]
            }
            respx.get(url__regex=r".*\/api\/recipes\/structured-recipe$").mock(
                return_value=Response(200, json=mock_recipe)
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["recipes://{slug}"]
            content = await resource.read({"slug": "structured-recipe"})

            # Verify structured ingredient is formatted
            assert "2 cups flour" in content
            assert "all-purpose" in content

    @pytest.mark.asyncio
    async def test_read_recipe_detail_with_instructions(self, mcp_server, mealie_env):
        """Test recipe detail includes instructions."""
        with respx.mock:
            mock_recipe = {
                "name": "Recipe with Steps",
                "slug": "recipe-with-steps",
                "recipeInstructions": [
                    {"text": "Preheat oven to 350°F", "title": "Preparation"},
                    {"text": "Mix dry ingredients", "title": "Mixing"},
                    {"text": "Bake for 30 minutes", "title": "Baking"}
                ]
            }
            respx.get(url__regex=r".*\/api\/recipes\/recipe-with-steps$").mock(
                return_value=Response(200, json=mock_recipe)
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["recipes://{slug}"]
            content = await resource.read({"slug": "recipe-with-steps"})

            # Verify instructions are present
            assert "Preheat oven" in content
            assert "Mix dry ingredients" in content
            assert "Bake for 30 minutes" in content
            assert "Preparation" in content
            assert "Mixing" in content
            assert "Baking" in content

    @pytest.mark.asyncio
    async def test_read_recipe_detail_with_nutrition(self, mcp_server, mealie_env):
        """Test recipe detail includes nutrition information."""
        with respx.mock:
            mock_recipe = {
                "name": "Healthy Recipe",
                "slug": "healthy-recipe",
                "nutrition": {
                    "calories": "300",
                    "proteinContent": "15g",
                    "carbohydrateContent": "40g",
                    "fatContent": "10g",
                    "fiberContent": "5g",
                    "sodiumContent": "200mg"
                }
            }
            respx.get(url__regex=r".*\/api\/recipes\/healthy-recipe$").mock(
                return_value=Response(200, json=mock_recipe)
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["recipes://{slug}"]
            content = await resource.read({"slug": "healthy-recipe"})

            # Verify nutrition section
            assert "## Nutrition" in content
            assert "300" in content  # calories
            assert "15g" in content  # protein
            assert "40g" in content  # carbs

    @pytest.mark.asyncio
    async def test_read_recipe_detail_with_notes(self, mcp_server, mealie_env):
        """Test recipe detail includes notes."""
        with respx.mock:
            mock_recipe = {
                "name": "Recipe with Notes",
                "slug": "recipe-with-notes",
                "notes": [
                    {"title": "Tip", "text": "Use fresh ingredients for best results"},
                    {"title": "Storage", "text": "Keeps in fridge for 3 days"}
                ]
            }
            respx.get(url__regex=r".*\/api\/recipes\/recipe-with-notes$").mock(
                return_value=Response(200, json=mock_recipe)
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["recipes://{slug}"]
            content = await resource.read({"slug": "recipe-with-notes"})

            # Verify notes section
            assert "## Notes" in content
            assert "Use fresh ingredients" in content
            assert "Keeps in fridge" in content

    @pytest.mark.asyncio
    async def test_read_recipe_detail_with_source_url(self, mcp_server, mealie_env):
        """Test recipe detail includes source URL."""
        with respx.mock:
            mock_recipe = {
                "name": "Imported Recipe",
                "slug": "imported-recipe",
                "orgURL": "https://example.com/original-recipe"
            }
            respx.get(url__regex=r".*\/api\/recipes\/imported-recipe$").mock(
                return_value=Response(200, json=mock_recipe)
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["recipes://{slug}"]
            content = await resource.read({"slug": "imported-recipe"})

            # Verify source section
            assert "## Source" in content
            assert "https://example.com/original-recipe" in content

    @pytest.mark.asyncio
    async def test_read_recipe_detail_not_found(self, mcp_server, mealie_env):
        """Test recipe detail handles 404 errors."""
        with respx.mock:
            respx.get(url__regex=r".*\/api\/recipes\/nonexistent$").mock(
                return_value=Response(404, json={"error": "Recipe not found"})
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["recipes://{slug}"]
            content = await resource.read({"slug": "nonexistent"})

            # Should return error message
            assert isinstance(content, str)
            assert "error" in content.lower() or "not found" in content.lower()

    @pytest.mark.asyncio
    async def test_read_recipe_detail_api_error(self, mcp_server, mealie_env):
        """Test recipe detail handles API errors."""
        with respx.mock:
            respx.get(url__regex=r".*\/api\/recipes\/error-recipe$").mock(
                return_value=Response(500, json={"error": "Internal server error"})
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["recipes://{slug}"]
            content = await resource.read({"slug": "error-recipe"})

            # Should return error message
            assert isinstance(content, str)
            assert "error" in content.lower()

    @pytest.mark.asyncio
    async def test_read_recipe_detail_with_timing(self, mcp_server, mealie_env):
        """Test recipe detail displays timing information."""
        with respx.mock:
            mock_recipe = {
                "name": "Timed Recipe",
                "slug": "timed-recipe",
                "totalTime": "1 hour",
                "prepTime": "15 minutes",
                "performTime": "45 minutes"
            }
            respx.get(url__regex=r".*\/api\/recipes\/timed-recipe$").mock(
                return_value=Response(200, json=mock_recipe)
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["recipes://{slug}"]
            content = await resource.read({"slug": "timed-recipe"})

            # Verify timing is displayed
            assert "Total Time" in content
            assert "1 hour" in content
            assert "Prep Time" in content
            assert "15 minutes" in content
            assert "Cook Time" in content
            assert "45 minutes" in content
