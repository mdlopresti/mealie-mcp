"""
Smoke tests for client methods to ensure they exist and have correct signatures.

Tests method signatures without making real HTTP calls.
"""

import pytest
from inspect import signature
from src.client import MealieClient


class TestClientMethodSignatures:
    """Test that all client methods exist with correct signatures."""

    def test_duplicate_recipe_signature(self):
        """Test duplicate_recipe method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'duplicate_recipe')
        sig = signature(client.duplicate_recipe)
        assert 'slug' in sig.parameters
        assert 'new_name' in sig.parameters

    def test_update_recipe_last_made_signature(self):
        """Test update_recipe_last_made method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'update_recipe_last_made')
        sig = signature(client.update_recipe_last_made)
        assert 'slug' in sig.parameters
        assert 'timestamp' in sig.parameters

    def test_create_recipes_from_urls_bulk_signature(self):
        """Test create_recipes_from_urls_bulk method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'create_recipes_from_urls_bulk')
        sig = signature(client.create_recipes_from_urls_bulk)
        assert 'urls' in sig.parameters

    def test_bulk_tag_recipes_signature(self):
        """Test bulk_tag_recipes method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'bulk_tag_recipes')
        sig = signature(client.bulk_tag_recipes)
        assert 'recipe_ids' in sig.parameters
        assert 'tags' in sig.parameters

    def test_bulk_categorize_recipes_signature(self):
        """Test bulk_categorize_recipes method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'bulk_categorize_recipes')
        sig = signature(client.bulk_categorize_recipes)
        assert 'recipe_ids' in sig.parameters
        assert 'categories' in sig.parameters

    def test_bulk_delete_recipes_signature(self):
        """Test bulk_delete_recipes method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'bulk_delete_recipes')
        sig = signature(client.bulk_delete_recipes)
        assert 'recipe_ids' in sig.parameters

    def test_bulk_export_recipes_signature(self):
        """Test bulk_export_recipes method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'bulk_export_recipes')
        sig = signature(client.bulk_export_recipes)
        assert 'recipe_ids' in sig.parameters
        assert 'export_format' in sig.parameters

    def test_bulk_update_settings_signature(self):
        """Test bulk_update_settings method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'bulk_update_settings')
        sig = signature(client.bulk_update_settings)
        assert 'recipe_ids' in sig.parameters
        assert 'settings' in sig.parameters

    def test_upload_recipe_image_from_url_signature(self):
        """Test upload_recipe_image_from_url method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'upload_recipe_image_from_url')
        sig = signature(client.upload_recipe_image_from_url)
        assert 'slug' in sig.parameters
        assert 'image_url' in sig.parameters

    def test_list_mealplan_rules_signature(self):
        """Test list_mealplan_rules method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'list_mealplan_rules')

    def test_get_mealplan_rule_signature(self):
        """Test get_mealplan_rule method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'get_mealplan_rule')
        sig = signature(client.get_mealplan_rule)
        assert 'rule_id' in sig.parameters

    def test_create_mealplan_rule_signature(self):
        """Test create_mealplan_rule method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'create_mealplan_rule')
        sig = signature(client.create_mealplan_rule)
        assert 'name' in sig.parameters
        assert 'entry_type' in sig.parameters

    def test_update_mealplan_rule_signature(self):
        """Test update_mealplan_rule method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'update_mealplan_rule')
        sig = signature(client.update_mealplan_rule)
        assert 'rule_id' in sig.parameters

    def test_delete_mealplan_rule_signature(self):
        """Test delete_mealplan_rule method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'delete_mealplan_rule')
        sig = signature(client.delete_mealplan_rule)
        assert 'rule_id' in sig.parameters

    def test_delete_recipe_from_shopping_list_signature(self):
        """Test delete_recipe_from_shopping_list method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'delete_recipe_from_shopping_list')
        sig = signature(client.delete_recipe_from_shopping_list)
        assert 'item_id' in sig.parameters
        assert 'recipe_id' in sig.parameters

    def test_list_foods_signature(self):
        """Test list_foods method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'list_foods')
        sig = signature(client.list_foods)
        assert 'page' in sig.parameters
        assert 'per_page' in sig.parameters

    def test_get_food_signature(self):
        """Test get_food method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'get_food')
        sig = signature(client.get_food)
        assert 'food_id' in sig.parameters

    def test_update_food_signature(self):
        """Test update_food method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'update_food')
        sig = signature(client.update_food)
        assert 'food_id' in sig.parameters

    def test_delete_food_signature(self):
        """Test delete_food method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'delete_food')
        sig = signature(client.delete_food)
        assert 'food_id' in sig.parameters

    def test_merge_foods_signature(self):
        """Test merge_foods method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'merge_foods')
        sig = signature(client.merge_foods)
        assert 'from_food_id' in sig.parameters
        assert 'to_food_id' in sig.parameters

    def test_list_units_signature(self):
        """Test list_units method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'list_units')
        sig = signature(client.list_units)
        assert 'page' in sig.parameters
        assert 'per_page' in sig.parameters

    def test_get_unit_signature(self):
        """Test get_unit method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'get_unit')
        sig = signature(client.get_unit)
        assert 'unit_id' in sig.parameters

    def test_update_unit_signature(self):
        """Test update_unit method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'update_unit')
        sig = signature(client.update_unit)
        assert 'unit_id' in sig.parameters

    def test_delete_unit_signature(self):
        """Test delete_unit method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'delete_unit')
        sig = signature(client.delete_unit)
        assert 'unit_id' in sig.parameters

    def test_merge_units_signature(self):
        """Test merge_units method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'merge_units')
        sig = signature(client.merge_units)
        assert 'from_unit_id' in sig.parameters
        assert 'to_unit_id' in sig.parameters

    def test_list_categories_signature(self):
        """Test list_categories method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'list_categories')

    def test_list_tags_signature(self):
        """Test list_tags method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'list_tags')

    def test_list_tools_signature(self):
        """Test list_tools method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'list_tools')

    def test_create_category_signature(self):
        """Test create_category method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'create_category')
        sig = signature(client.create_category)
        assert 'name' in sig.parameters

    def test_create_tag_signature(self):
        """Test create_tag method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'create_tag')
        sig = signature(client.create_tag)
        assert 'name' in sig.parameters

    def test_update_category_signature(self):
        """Test update_category method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'update_category')
        sig = signature(client.update_category)
        assert 'category_id' in sig.parameters

    def test_delete_category_signature(self):
        """Test delete_category method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'delete_category')
        sig = signature(client.delete_category)
        assert 'category_id' in sig.parameters

    def test_update_tag_signature(self):
        """Test update_tag method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'update_tag')
        sig = signature(client.update_tag)
        assert 'tag_id' in sig.parameters

    def test_delete_tag_signature(self):
        """Test delete_tag method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'delete_tag')
        sig = signature(client.delete_tag)
        assert 'tag_id' in sig.parameters

    def test_update_tool_signature(self):
        """Test update_tool method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'update_tool')
        sig = signature(client.update_tool)
        assert 'tool_id' in sig.parameters

    def test_delete_tool_signature(self):
        """Test delete_tool method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'delete_tool')
        sig = signature(client.delete_tool)
        assert 'tool_id' in sig.parameters

    def test_parse_ingredient_signature(self):
        """Test parse_ingredient method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'parse_ingredient')
        sig = signature(client.parse_ingredient)
        assert 'ingredient' in sig.parameters

    def test_parse_ingredients_batch_signature(self):
        """Test parse_ingredients_batch method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'parse_ingredients_batch')
        sig = signature(client.parse_ingredients_batch)
        assert 'ingredients' in sig.parameters

    def test_create_food_signature(self):
        """Test create_food method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'create_food')
        sig = signature(client.create_food)
        assert 'name' in sig.parameters

    def test_create_unit_signature(self):
        """Test create_unit method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'create_unit')
        sig = signature(client.create_unit)
        assert 'name' in sig.parameters

    def test_update_recipe_ingredients_signature(self):
        """Test update_recipe_ingredients method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'update_recipe_ingredients')
        sig = signature(client.update_recipe_ingredients)
        assert 'slug' in sig.parameters
        assert 'ingredients' in sig.parameters

    def test_set_recipe_rating_signature(self):
        """Test set_recipe_rating method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'set_recipe_rating')
        sig = signature(client.set_recipe_rating)
        assert 'slug' in sig.parameters
        assert 'rating' in sig.parameters
        assert 'is_favorite' in sig.parameters

    def test_get_user_ratings_signature(self):
        """Test get_user_ratings method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'get_user_ratings')

    def test_get_recipe_rating_signature(self):
        """Test get_recipe_rating method exists."""
        client = MealieClient(base_url="https://test.com", api_token="token")
        assert hasattr(client, 'get_recipe_rating')
        sig = signature(client.get_recipe_rating)
        assert 'recipe_id' in sig.parameters


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
