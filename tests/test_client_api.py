"""
Comprehensive tests for MealieClient API methods.

Tests all client API methods using respx to mock HTTP responses.
"""

import pytest
import respx
from httpx import Response
from src.client import MealieClient, MealieAPIError


class TestRecipeAPIs:
    """Test recipe-related client methods."""

    @respx.mock
    def test_duplicate_recipe(self, mock_client, sample_recipe):
        """Test duplicate_recipe method."""
        route = respx.post(
            "https://test.mealie.example.com/api/recipes/test-recipe/duplicate"
        ).mock(return_value=Response(200, json=sample_recipe))

        result = mock_client.duplicate_recipe("test-recipe", "New Recipe")

        assert result["slug"] == "test-recipe"
        assert route.called

    @respx.mock
    def test_update_recipe_last_made(self, mock_client):
        """Test update_recipe_last_made method."""
        route = respx.put(
            "https://test.mealie.example.com/api/recipes/test-recipe/timeline/last-made"
        ).mock(return_value=Response(200, json={"lastMade": "2025-12-20"}))

        result = mock_client.update_recipe_last_made("test-recipe", "2025-12-20")

        assert "lastMade" in result
        assert route.called

    @respx.mock
    def test_create_recipes_from_urls_bulk(self, mock_client, sample_recipe):
        """Test bulk URL import."""
        route = respx.post(
            "https://test.mealie.example.com/api/recipes/create-url-bulk"
        ).mock(return_value=Response(200, json={"imported": [sample_recipe]}))

        result = mock_client.create_recipes_from_urls_bulk(
            ["https://example.com/recipe1", "https://example.com/recipe2"]
        )

        assert "imported" in result
        assert route.called

    @respx.mock
    def test_bulk_tag_recipes(self, mock_client, sample_tag):
        """Test bulk tag recipes."""
        route = respx.put(
            "https://test.mealie.example.com/api/recipes/bulk-actions/tag"
        ).mock(return_value=Response(200, json={"success": True}))

        result = mock_client.bulk_tag_recipes(
            ["recipe-1", "recipe-2"],
            ["Vegan", "Quick"]
        )

        assert route.called

    @respx.mock
    def test_bulk_categorize_recipes(self, mock_client):
        """Test bulk categorize recipes."""
        route = respx.put(
            "https://test.mealie.example.com/api/recipes/bulk-actions/categorize"
        ).mock(return_value=Response(200, json={"success": True}))

        result = mock_client.bulk_categorize_recipes(
            ["recipe-1", "recipe-2"],
            ["Dinner", "Main"]
        )

        assert route.called

    @respx.mock
    def test_bulk_delete_recipes(self, mock_client):
        """Test bulk delete recipes."""
        route = respx.delete(
            "https://test.mealie.example.com/api/recipes/bulk-actions"
        ).mock(return_value=Response(200, json={"deleted": 2}))

        result = mock_client.bulk_delete_recipes(["recipe-1", "recipe-2"])

        assert route.called

    @respx.mock
    def test_bulk_export_recipes(self, mock_client):
        """Test bulk export recipes."""
        route = respx.post(
            "https://test.mealie.example.com/api/recipes/bulk-actions/export"
        ).mock(return_value=Response(200, content=b"recipe data"))

        result = mock_client.bulk_export_recipes(["recipe-1"], "json")

        assert route.called

    @respx.mock
    def test_bulk_update_settings(self, mock_client):
        """Test bulk update settings."""
        route = respx.patch(
            "https://test.mealie.example.com/api/recipes/bulk-actions/settings"
        ).mock(return_value=Response(200, json={"updated": 2}))

        result = mock_client.bulk_update_settings(
            ["recipe-1", "recipe-2"],
            {"public": True}
        )

        assert route.called

    @respx.mock
    def test_upload_recipe_image_from_url(self, mock_client):
        """Test upload recipe image from URL."""
        # Mock image download
        image_route = respx.get("https://example.com/image.jpg").mock(
            return_value=Response(200, content=b"fake image data")
        )

        # Mock image upload
        upload_route = respx.put(
            "https://test.mealie.example.com/api/recipes/test-recipe/image"
        ).mock(return_value=Response(200, json={"success": True}))

        result = mock_client.upload_recipe_image_from_url(
            "test-recipe",
            "https://example.com/image.jpg"
        )

        assert image_route.called
        assert upload_route.called


class TestMealPlanAPIs:
    """Test meal plan-related client methods."""

    @respx.mock
    def test_list_mealplan_rules(self, mock_client):
        """Test list mealplan rules."""
        route = respx.get(
            "https://test.mealie.example.com/api/households/mealplans/rules"
        ).mock(return_value=Response(200, json=[{"id": "rule-1", "name": "Dinner Rule"}]))

        result = mock_client.list_mealplan_rules()

        assert len(result) == 1
        assert route.called

    @respx.mock
    def test_get_mealplan_rule(self, mock_client):
        """Test get mealplan rule."""
        route = respx.get(
            "https://test.mealie.example.com/api/households/mealplans/rules/rule-1"
        ).mock(return_value=Response(200, json={"id": "rule-1", "name": "Dinner Rule"}))

        result = mock_client.get_mealplan_rule("rule-1")

        assert result["id"] == "rule-1"
        assert route.called

    @respx.mock
    def test_create_mealplan_rule(self, mock_client):
        """Test create mealplan rule."""
        route = respx.post(
            "https://test.mealie.example.com/api/households/mealplans/rules"
        ).mock(return_value=Response(201, json={"id": "rule-new", "name": "Lunch Rule"}))

        result = mock_client.create_mealplan_rule(
            "Lunch Rule",
            "lunch",
            tags=["Quick"],
            categories=["Light"]
        )

        assert result["id"] == "rule-new"
        assert route.called

    @respx.mock
    def test_update_mealplan_rule(self, mock_client):
        """Test update mealplan rule."""
        route = respx.put(
            "https://test.mealie.example.com/api/households/mealplans/rules/rule-1"
        ).mock(return_value=Response(200, json={"id": "rule-1", "name": "Updated Rule"}))

        result = mock_client.update_mealplan_rule(
            "rule-1",
            name="Updated Rule"
        )

        assert result["name"] == "Updated Rule"
        assert route.called

    @respx.mock
    def test_delete_mealplan_rule(self, mock_client):
        """Test delete mealplan rule."""
        route = respx.delete(
            "https://test.mealie.example.com/api/households/mealplans/rules/rule-1"
        ).mock(return_value=Response(204))

        mock_client.delete_mealplan_rule("rule-1")

        assert route.called


class TestShoppingAPIs:
    """Test shopping-related client methods."""

    @respx.mock
    def test_delete_recipe_from_shopping_list(self, mock_client):
        """Test delete recipe from shopping list."""
        route = respx.delete(
            "https://test.mealie.example.com/api/shopping/items/item-1/recipe/recipe-1"
        ).mock(return_value=Response(200, json={"success": True}))

        result = mock_client.delete_recipe_from_shopping_list("item-1", "recipe-1")

        assert route.called


class TestFoodUnitAPIs:
    """Test food and unit management APIs."""

    @respx.mock
    def test_list_foods(self, mock_client):
        """Test list foods."""
        route = respx.get(
            "https://test.mealie.example.com/api/foods"
        ).mock(return_value=Response(200, json={"items": [{"id": "food-1", "name": "flour"}]}))

        result = mock_client.list_foods(page=1, per_page=50)

        assert "items" in result
        assert route.called

    @respx.mock
    def test_get_food(self, mock_client):
        """Test get food."""
        route = respx.get(
            "https://test.mealie.example.com/api/foods/food-1"
        ).mock(return_value=Response(200, json={"id": "food-1", "name": "flour"}))

        result = mock_client.get_food("food-1")

        assert result["id"] == "food-1"
        assert route.called

    @respx.mock
    def test_update_food(self, mock_client):
        """Test update food."""
        route = respx.put(
            "https://test.mealie.example.com/api/foods/food-1"
        ).mock(return_value=Response(200, json={"id": "food-1", "name": "Whole Wheat Flour"}))

        result = mock_client.update_food("food-1", name="Whole Wheat Flour")

        assert result["name"] == "Whole Wheat Flour"
        assert route.called

    @respx.mock
    def test_delete_food(self, mock_client):
        """Test delete food."""
        route = respx.delete(
            "https://test.mealie.example.com/api/foods/food-1"
        ).mock(return_value=Response(204))

        mock_client.delete_food("food-1")

        assert route.called

    @respx.mock
    def test_merge_foods(self, mock_client):
        """Test merge foods."""
        route = respx.put(
            "https://test.mealie.example.com/api/foods/food-1/merge/food-2"
        ).mock(return_value=Response(200, json={"success": True}))

        result = mock_client.merge_foods("food-1", "food-2")

        assert route.called

    @respx.mock
    def test_list_units(self, mock_client):
        """Test list units."""
        route = respx.get(
            "https://test.mealie.example.com/api/units"
        ).mock(return_value=Response(200, json={"items": [{"id": "unit-1", "name": "cup"}]}))

        result = mock_client.list_units(page=1, per_page=50)

        assert "items" in result
        assert route.called

    @respx.mock
    def test_get_unit(self, mock_client):
        """Test get unit."""
        route = respx.get(
            "https://test.mealie.example.com/api/units/unit-1"
        ).mock(return_value=Response(200, json={"id": "unit-1", "name": "cup"}))

        result = mock_client.get_unit("unit-1")

        assert result["id"] == "unit-1"
        assert route.called

    @respx.mock
    def test_update_unit(self, mock_client):
        """Test update unit."""
        route = respx.put(
            "https://test.mealie.example.com/api/units/unit-1"
        ).mock(return_value=Response(200, json={"id": "unit-1", "name": "cups"}))

        result = mock_client.update_unit("unit-1", name="cups")

        assert result["name"] == "cups"
        assert route.called

    @respx.mock
    def test_delete_unit(self, mock_client):
        """Test delete unit."""
        route = respx.delete(
            "https://test.mealie.example.com/api/units/unit-1"
        ).mock(return_value=Response(204))

        mock_client.delete_unit("unit-1")

        assert route.called

    @respx.mock
    def test_merge_units(self, mock_client):
        """Test merge units."""
        route = respx.put(
            "https://test.mealie.example.com/api/units/unit-1/merge/unit-2"
        ).mock(return_value=Response(200, json={"success": True}))

        result = mock_client.merge_units("unit-1", "unit-2")

        assert route.called


class TestOrganizerAPIs:
    """Test organizer (categories, tags, tools) APIs."""

    @respx.mock
    def test_list_categories(self, mock_client):
        """Test list categories."""
        route = respx.get(
            "https://test.mealie.example.com/api/organizers/categories"
        ).mock(return_value=Response(200, json=[{"id": "cat-1", "name": "Dessert"}]))

        result = mock_client.list_categories()

        assert len(result) == 1
        assert route.called

    @respx.mock
    def test_list_tags(self, mock_client):
        """Test list tags."""
        route = respx.get(
            "https://test.mealie.example.com/api/organizers/tags"
        ).mock(return_value=Response(200, json=[{"id": "tag-1", "name": "Vegan"}]))

        result = mock_client.list_tags()

        assert len(result) == 1
        assert route.called

    @respx.mock
    def test_list_tools(self, mock_client):
        """Test list tools."""
        route = respx.get(
            "https://test.mealie.example.com/api/organizers/tools"
        ).mock(return_value=Response(200, json=[{"id": "tool-1", "name": "Blender"}]))

        result = mock_client.list_tools()

        assert len(result) == 1
        assert route.called

    @respx.mock
    def test_create_category(self, mock_client):
        """Test create category."""
        route = respx.post(
            "https://test.mealie.example.com/api/organizers/categories"
        ).mock(return_value=Response(201, json={"id": "cat-new", "name": "Breakfast"}))

        result = mock_client.create_category("Breakfast")

        assert result["name"] == "Breakfast"
        assert route.called

    @respx.mock
    def test_create_tag(self, mock_client):
        """Test create tag."""
        route = respx.post(
            "https://test.mealie.example.com/api/organizers/tags"
        ).mock(return_value=Response(201, json={"id": "tag-new", "name": "Quick"}))

        result = mock_client.create_tag("Quick")

        assert result["name"] == "Quick"
        assert route.called

    @respx.mock
    def test_update_category(self, mock_client):
        """Test update category."""
        route = respx.put(
            "https://test.mealie.example.com/api/organizers/categories/cat-1"
        ).mock(return_value=Response(200, json={"id": "cat-1", "name": "Desserts"}))

        result = mock_client.update_category("cat-1", name="Desserts")

        assert result["name"] == "Desserts"
        assert route.called

    @respx.mock
    def test_delete_category(self, mock_client):
        """Test delete category."""
        route = respx.delete(
            "https://test.mealie.example.com/api/organizers/categories/cat-1"
        ).mock(return_value=Response(204))

        mock_client.delete_category("cat-1")

        assert route.called

    @respx.mock
    def test_update_tag(self, mock_client):
        """Test update tag."""
        route = respx.put(
            "https://test.mealie.example.com/api/organizers/tags/tag-1"
        ).mock(return_value=Response(200, json={"id": "tag-1", "name": "Vegetarian"}))

        result = mock_client.update_tag("tag-1", name="Vegetarian")

        assert result["name"] == "Vegetarian"
        assert route.called

    @respx.mock
    def test_delete_tag(self, mock_client):
        """Test delete tag."""
        route = respx.delete(
            "https://test.mealie.example.com/api/organizers/tags/tag-1"
        ).mock(return_value=Response(204))

        mock_client.delete_tag("tag-1")

        assert route.called

    @respx.mock
    def test_update_tool(self, mock_client):
        """Test update tool."""
        route = respx.put(
            "https://test.mealie.example.com/api/organizers/tools/tool-1"
        ).mock(return_value=Response(200, json={"id": "tool-1", "name": "Food Processor"}))

        result = mock_client.update_tool("tool-1", name="Food Processor")

        assert result["name"] == "Food Processor"
        assert route.called

    @respx.mock
    def test_delete_tool(self, mock_client):
        """Test delete tool."""
        route = respx.delete(
            "https://test.mealie.example.com/api/organizers/tools/tool-1"
        ).mock(return_value=Response(204))

        mock_client.delete_tool("tool-1")

        assert route.called


class TestParserAPIs:
    """Test parser APIs."""

    @respx.mock
    def test_parse_ingredient(self, mock_client):
        """Test parse single ingredient."""
        route = respx.post(
            "https://test.mealie.example.com/api/parser/ingredient"
        ).mock(return_value=Response(200, json={
            "input": "2 cups flour",
            "ingredient": {
                "quantity": 2.0,
                "unit": "cup",
                "food": "flour",
                "display": "2 cups flour"
            }
        }))

        result = mock_client.parse_ingredient("2 cups flour")

        assert result["ingredient"]["quantity"] == 2.0
        assert route.called

    @respx.mock
    def test_parse_ingredients_batch(self, mock_client):
        """Test parse multiple ingredients."""
        route = respx.post(
            "https://test.mealie.example.com/api/parser/ingredients"
        ).mock(return_value=Response(200, json=[
            {"input": "2 cups flour", "ingredient": {"quantity": 2.0}},
            {"input": "1 tsp salt", "ingredient": {"quantity": 1.0}}
        ]))

        result = mock_client.parse_ingredients_batch(["2 cups flour", "1 tsp salt"])

        assert len(result) == 2
        assert route.called


class TestIngredientAPIs:
    """Test ingredient-related APIs."""

    @respx.mock
    def test_create_food(self, mock_client):
        """Test create food."""
        route = respx.post(
            "https://test.mealie.example.com/api/foods"
        ).mock(return_value=Response(201, json={"id": "food-new", "name": "quinoa"}))

        result = mock_client.create_food("quinoa")

        assert result["name"] == "quinoa"
        assert route.called

    @respx.mock
    def test_create_unit(self, mock_client):
        """Test create unit."""
        route = respx.post(
            "https://test.mealie.example.com/api/units"
        ).mock(return_value=Response(201, json={"id": "unit-new", "name": "pinch"}))

        result = mock_client.create_unit("pinch")

        assert result["name"] == "pinch"
        assert route.called

    @respx.mock
    def test_update_recipe_ingredients(self, mock_client):
        """Test update recipe ingredients."""
        route = respx.patch(
            "https://test.mealie.example.com/api/recipes/test-recipe"
        ).mock(return_value=Response(200, json={"slug": "test-recipe"}))

        result = mock_client.update_recipe_ingredients("test-recipe", [
            {"quantity": 2.0, "unit": "cup", "food": "flour"}
        ])

        assert route.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
