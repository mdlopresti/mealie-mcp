"""Mock data builders for unit tests.

Provides factory functions to generate realistic test data for Mealie objects.
Each builder accepts **overrides to customize the generated data.

Usage:
    >>> recipe = build_recipe(name="Custom Recipe", slug="custom")
    >>> mealplan = build_mealplan(meal_date="2025-12-25", entry_type="breakfast")
    >>> tag = build_tag(name="Vegan")
"""

from datetime import datetime, UTC
from typing import Dict, Any, List


def build_recipe(
    slug: str = "test-recipe",
    name: str = "Test Recipe",
    **overrides
) -> Dict[str, Any]:
    """Build a mock recipe object.

    Args:
        slug: Recipe URL slug
        name: Recipe name
        **overrides: Additional fields to override

    Returns:
        Dictionary representing a Mealie recipe

    Example:
        >>> recipe = build_recipe(name="Pasta", recipeYield="6 servings")
        >>> recipe["name"]
        'Pasta'
        >>> recipe["recipeYield"]
        '6 servings'
    """
    recipe = {
        "id": f"recipe-{slug}",
        "slug": slug,
        "name": name,
        "description": "A test recipe",
        "recipeYield": "4 servings",
        "totalTime": "30 minutes",
        "prepTime": "10 minutes",
        "cookTime": "20 minutes",
        "recipeIngredient": ["2 cups flour", "1 tsp salt"],
        "recipeInstructions": [
            {"text": "Mix ingredients"},
            {"text": "Bake at 350F"}
        ],
        "tags": [{"id": "tag-1", "name": "Dinner", "slug": "dinner"}],
        "recipeCategory": [{"id": "cat-1", "name": "Main", "slug": "main"}],
        "groupId": "group-123",
        "dateAdded": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "dateUpdated": datetime.now(UTC).isoformat().replace("+00:00", "Z")
    }
    recipe.update(overrides)
    return recipe


def build_mealplan(
    meal_date: str = "2025-12-25",
    entry_type: str = "dinner",
    **overrides
) -> Dict[str, Any]:
    """Build a mock meal plan entry.

    Args:
        meal_date: Date in YYYY-MM-DD format
        entry_type: Type of meal (breakfast, lunch, dinner, side, snack)
        **overrides: Additional fields to override

    Returns:
        Dictionary representing a Mealie meal plan entry

    Example:
        >>> mealplan = build_mealplan(meal_date="2025-12-26", entry_type="breakfast")
        >>> mealplan["date"]
        '2025-12-26'
        >>> mealplan["entryType"]
        'breakfast'
    """
    mealplan = {
        "id": f"mealplan-{meal_date}-{entry_type}",
        "date": meal_date,
        "entryType": entry_type,
        "title": "Test Meal",
        "text": "Test notes",
        "recipeId": None,
        "groupId": "group-123"
    }
    mealplan.update(overrides)
    return mealplan


def build_shopping_list(
    name: str = "Test Shopping List",
    **overrides
) -> Dict[str, Any]:
    """Build a mock shopping list.

    Args:
        name: Shopping list name
        **overrides: Additional fields to override

    Returns:
        Dictionary representing a Mealie shopping list

    Example:
        >>> shopping_list = build_shopping_list(name="Grocery Run")
        >>> shopping_list["name"]
        'Grocery Run'
        >>> shopping_list["listItems"]
        []
    """
    shopping_list = {
        "id": "list-123",
        "name": name,
        "listItems": [],
        "groupId": "group-123"
    }
    shopping_list.update(overrides)
    return shopping_list


def build_shopping_item(
    note: str = "Test item",
    **overrides
) -> Dict[str, Any]:
    """Build a mock shopping list item.

    Args:
        note: Item description/note
        **overrides: Additional fields to override

    Returns:
        Dictionary representing a shopping list item

    Example:
        >>> item = build_shopping_item(note="2 cups flour", checked=True)
        >>> item["note"]
        '2 cups flour'
        >>> item["checked"]
        True
    """
    item = {
        "id": "item-123",
        "note": note,
        "checked": False,
        "quantity": 1.0,
        "unit": {"id": "unit-1", "name": "item"},
        "food": {"id": "food-1", "name": "generic"},
        "shoppingListId": "list-123"
    }
    item.update(overrides)
    return item


def build_tag(
    name: str = "Vegan",
    **overrides
) -> Dict[str, Any]:
    """Build a mock tag.

    Args:
        name: Tag name
        **overrides: Additional fields to override

    Returns:
        Dictionary representing a Mealie tag

    Example:
        >>> tag = build_tag(name="Gluten Free")
        >>> tag["name"]
        'Gluten Free'
        >>> tag["slug"]
        'gluten-free'
    """
    tag = {
        "id": f"tag-{name.lower().replace(' ', '-')}",
        "name": name,
        "slug": name.lower().replace(" ", "-"),
        "groupId": "group-123"
    }
    tag.update(overrides)
    return tag


def build_category(
    name: str = "Dessert",
    **overrides
) -> Dict[str, Any]:
    """Build a mock category.

    Args:
        name: Category name
        **overrides: Additional fields to override

    Returns:
        Dictionary representing a Mealie category

    Example:
        >>> category = build_category(name="Main Dish")
        >>> category["name"]
        'Main Dish'
        >>> category["slug"]
        'main-dish'
    """
    category = {
        "id": f"cat-{name.lower().replace(' ', '-')}",
        "name": name,
        "slug": name.lower().replace(" ", "-"),
        "groupId": "group-123"
    }
    category.update(overrides)
    return category


def build_tool(
    name: str = "Blender",
    **overrides
) -> Dict[str, Any]:
    """Build a mock kitchen tool.

    Args:
        name: Tool name
        **overrides: Additional fields to override

    Returns:
        Dictionary representing a Mealie tool

    Example:
        >>> tool = build_tool(name="Stand Mixer")
        >>> tool["name"]
        'Stand Mixer'
    """
    tool = {
        "id": f"tool-{name.lower().replace(' ', '-')}",
        "name": name,
        "slug": name.lower().replace(" ", "-"),
        "groupId": "group-123"
    }
    tool.update(overrides)
    return tool


def build_food(
    name: str = "Flour",
    **overrides
) -> Dict[str, Any]:
    """Build a mock food.

    Args:
        name: Food name
        **overrides: Additional fields to override

    Returns:
        Dictionary representing a Mealie food

    Example:
        >>> food = build_food(name="All Purpose Flour")
        >>> food["name"]
        'All Purpose Flour'
    """
    food = {
        "id": f"food-{name.lower().replace(' ', '-')}",
        "name": name,
        "description": f"Test {name}",
        "groupId": "group-123",
        "labelId": None
    }
    food.update(overrides)
    return food


def build_unit(
    name: str = "cup",
    abbreviation: str = "c",
    **overrides
) -> Dict[str, Any]:
    """Build a mock unit.

    Args:
        name: Unit name
        abbreviation: Unit abbreviation
        **overrides: Additional fields to override

    Returns:
        Dictionary representing a Mealie unit

    Example:
        >>> unit = build_unit(name="tablespoon", abbreviation="tbsp")
        >>> unit["name"]
        'tablespoon'
        >>> unit["abbreviation"]
        'tbsp'
    """
    unit = {
        "id": f"unit-{name.lower()}",
        "name": name,
        "abbreviation": abbreviation,
        "description": f"Test {name}",
        "groupId": "group-123"
    }
    unit.update(overrides)
    return unit


def build_cookbook(
    name: str = "Test Cookbook",
    **overrides
) -> Dict[str, Any]:
    """Build a mock cookbook.

    Args:
        name: Cookbook name
        **overrides: Additional fields to override

    Returns:
        Dictionary representing a Mealie cookbook

    Example:
        >>> cookbook = build_cookbook(name="Holiday Recipes", public=True)
        >>> cookbook["name"]
        'Holiday Recipes'
        >>> cookbook["public"]
        True
    """
    cookbook = {
        "id": f"cookbook-{name.lower().replace(' ', '-')}",
        "name": name,
        "slug": name.lower().replace(" ", "-"),
        "description": "A test cookbook",
        "public": False,
        "groupId": "group-123",
        "recipes": []
    }
    cookbook.update(overrides)
    return cookbook


def build_comment(
    recipe_id: str = "recipe-123",
    text: str = "Great recipe!",
    **overrides
) -> Dict[str, Any]:
    """Build a mock recipe comment.

    Args:
        recipe_id: Recipe ID the comment belongs to
        text: Comment text
        **overrides: Additional fields to override

    Returns:
        Dictionary representing a Mealie comment

    Example:
        >>> comment = build_comment(text="This was delicious!")
        >>> comment["text"]
        'This was delicious!'
    """
    comment = {
        "id": "comment-123",
        "recipeId": recipe_id,
        "text": text,
        "userId": "user-123",
        "createdAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "updatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z")
    }
    comment.update(overrides)
    return comment


def build_timeline_event(
    recipe_id: str = "recipe-123",
    subject: str = "Recipe made",
    **overrides
) -> Dict[str, Any]:
    """Build a mock timeline event.

    Args:
        recipe_id: Recipe ID the event belongs to
        subject: Event subject/title
        **overrides: Additional fields to override

    Returns:
        Dictionary representing a Mealie timeline event

    Example:
        >>> event = build_timeline_event(subject="Made for dinner party")
        >>> event["subject"]
        'Made for dinner party'
    """
    event = {
        "id": "event-123",
        "recipeId": recipe_id,
        "subject": subject,
        "eventType": "info",
        "eventMessage": "Test event message",
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "userId": "user-123"
    }
    event.update(overrides)
    return event


def build_parsed_ingredient(
    input_text: str = "2 cups flour",
    quantity: float = 2.0,
    unit: str = "cup",
    food: str = "flour",
    **overrides
) -> Dict[str, Any]:
    """Build a mock parsed ingredient.

    Args:
        input_text: Original ingredient text
        quantity: Parsed quantity
        unit: Parsed unit
        food: Parsed food name
        **overrides: Additional fields to override

    Returns:
        Dictionary representing a parsed ingredient from Mealie parser

    Example:
        >>> ingredient = build_parsed_ingredient("1 tsp salt", 1.0, "teaspoon", "salt")
        >>> ingredient["ingredient"]["quantity"]
        1.0
    """
    parsed = {
        "input": input_text,
        "confidence": {
            "quantity": 0.95,
            "unit": 0.90,
            "food": 0.85,
            "average": 0.90
        },
        "ingredient": {
            "quantity": quantity,
            "unit": {"name": unit} if unit else None,
            "food": {"name": food} if food else None,
            "note": "",
            "display": input_text
        }
    }
    parsed.update(overrides)
    return parsed
