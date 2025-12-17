"""
MCP Resources for Mealie

This module contains resource implementations that provide context
to AI agents about the current state of Mealie.
"""

from .recipes import get_recipes_list, get_recipe_detail
from .mealplans import get_current_mealplan, get_today_meals
from .shopping import get_shopping_lists

__all__ = [
    "get_recipes_list",
    "get_recipe_detail",
    "get_current_mealplan",
    "get_today_meals",
    "get_shopping_lists",
]
