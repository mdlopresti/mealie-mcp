"""
Mealie MCP Server

FastMCP-based Model Context Protocol server for Mealie integration.
Provides tools and resources for recipe management, meal planning, and shopping lists.
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Ensure the src directory is in the path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Import tools
from tools.recipes import (
    recipes_search,
    recipes_get,
    recipes_list,
    recipes_create,
    recipes_create_from_url,
    recipes_update,
    recipes_update_structured_ingredients,
    recipes_delete,
)
from tools.mealplans import (
    mealplans_list,
    mealplans_today,
    mealplans_get,
    mealplans_create,
    mealplans_update,
    mealplans_delete,
    mealplans_random,
    mealplans_get_by_date,
)
from tools.shopping import (
    shopping_lists_list,
    shopping_lists_get,
    shopping_lists_create,
    shopping_lists_delete,
    shopping_items_add,
    shopping_items_add_bulk,
    shopping_items_check,
    shopping_items_delete,
    shopping_items_add_recipe,
    shopping_generate_from_mealplan,
    shopping_lists_clear_checked,
)
from tools.parser import (
    parser_ingredient,
    parser_ingredients_batch,
)

# Import resources
from resources.recipes import get_recipes_list, get_recipe_detail
from resources.mealplans import get_current_mealplan, get_today_meals
from resources.shopping import get_shopping_lists, get_shopping_list_detail

# Create MCP server
mcp = FastMCP("mealie")


# =============================================================================
# Tools - Actions the AI can perform
# =============================================================================

# -----------------------------------------------------------------------------
# Utility Tools
# -----------------------------------------------------------------------------

@mcp.tool()
def ping() -> str:
    """Test connectivity to the MCP server and Mealie instance."""
    from client import MealieClient, MealieAPIError

    try:
        with MealieClient() as client:
            if client.test_connection():
                return "pong - Mealie MCP server is running and connected to Mealie"
    except MealieAPIError as e:
        return f"MCP server running but Mealie connection failed: {e}"
    except Exception as e:
        return f"MCP server running but error occurred: {e}"


# -----------------------------------------------------------------------------
# Recipe Tools (Phase 1)
# -----------------------------------------------------------------------------

@mcp.tool()
def mealie_recipes_search(
    query: str = "",
    tags: list[str] | None = None,
    categories: list[str] | None = None,
    limit: int = 10
) -> str:
    """Search for recipes in Mealie.

    Args:
        query: Search term to filter recipes by name/description
        tags: List of tag names to filter by
        categories: List of category names to filter by
        limit: Maximum number of results (default 10)

    Returns:
        JSON string with list of matching recipes (name, slug, description, tags)
    """
    return recipes_search(query=query, tags=tags, categories=categories, limit=limit)


@mcp.tool()
def mealie_recipes_get(slug: str) -> str:
    """Get complete details for a specific recipe.

    Args:
        slug: The recipe's URL slug identifier

    Returns:
        JSON string with full recipe details including ingredients, instructions, nutrition
    """
    return recipes_get(slug=slug)


@mcp.tool()
def mealie_recipes_list(page: int = 1, per_page: int = 20) -> str:
    """List all recipes with pagination.

    Args:
        page: Page number (1-indexed)
        per_page: Number of recipes per page (default 20)

    Returns:
        JSON string with paginated recipe list and metadata
    """
    return recipes_list(page=page, per_page=per_page)


# -----------------------------------------------------------------------------
# Recipe CRUD Tools (Phase 4)
# -----------------------------------------------------------------------------

@mcp.tool()
def mealie_recipes_create(
    name: str,
    description: str = "",
    recipe_yield: str = "",
    total_time: str = "",
    prep_time: str = "",
    cook_time: str = "",
    ingredients: list[str] | None = None,
    instructions: list[str] | None = None,
    tags: list[str] | None = None,
    categories: list[str] | None = None,
) -> str:
    """Create a new recipe in Mealie.

    Args:
        name: Recipe name (required)
        description: Recipe description
        recipe_yield: Yield/servings (e.g., "4 servings")
        total_time: Total time (e.g., "1 hour 30 minutes")
        prep_time: Prep time (e.g., "20 minutes")
        cook_time: Cook time (e.g., "1 hour")
        ingredients: List of ingredient strings (e.g., ["2 cups flour", "1 tsp salt"])
        instructions: List of instruction strings (e.g., ["Preheat oven", "Mix ingredients"])
        tags: List of tag names to apply
        categories: List of category names to apply

    Returns:
        JSON string with created recipe details
    """
    return recipes_create(
        name=name,
        description=description,
        recipe_yield=recipe_yield,
        total_time=total_time,
        prep_time=prep_time,
        cook_time=cook_time,
        ingredients=ingredients,
        instructions=instructions,
        tags=tags,
        categories=categories,
    )


@mcp.tool()
def mealie_recipes_create_from_url(url: str, include_tags: bool = False) -> str:
    """Import a recipe from a URL by scraping it.

    Args:
        url: URL of the recipe to import
        include_tags: Whether to include tags from the scraped recipe (default False)

    Returns:
        JSON string with imported recipe details
    """
    return recipes_create_from_url(url=url, include_tags=include_tags)


@mcp.tool()
def mealie_recipes_update(
    slug: str,
    name: str | None = None,
    description: str | None = None,
    recipe_yield: str | None = None,
    total_time: str | None = None,
    prep_time: str | None = None,
    cook_time: str | None = None,
    ingredients: list[str] | None = None,
    instructions: list[str] | None = None,
    tags: list[str] | None = None,
    categories: list[str] | None = None,
    org_url: str | None = None,
    image: str | None = None,
) -> str:
    """Update an existing recipe in Mealie.

    Args:
        slug: The recipe's slug identifier (required)
        name: New recipe name
        description: New description
        recipe_yield: New yield/servings
        total_time: New total time
        prep_time: New prep time
        cook_time: New cook time
        ingredients: New list of ingredient strings (replaces existing)
        instructions: New list of instruction strings (replaces existing)
        tags: New list of tag names (replaces existing)
        categories: New list of category names (replaces existing)
        org_url: Original recipe URL
        image: Recipe image identifier

    Returns:
        JSON string with updated recipe details
    """
    return recipes_update(
        slug=slug,
        name=name,
        description=description,
        recipe_yield=recipe_yield,
        total_time=total_time,
        prep_time=prep_time,
        cook_time=cook_time,
        ingredients=ingredients,
        instructions=instructions,
        tags=tags,
        categories=categories,
        org_url=org_url,
        image=image,
    )


@mcp.tool()
def mealie_recipes_update_structured_ingredients(
    slug: str,
    parsed_ingredients: list[dict]
) -> str:
    """Update a recipe with structured ingredients from parser output.

    This tool bridges the gap between ingredient parsing and recipe updates by accepting
    parsed ingredient data and updating a recipe with fully structured ingredients
    (quantity, unit, food fields populated).

    Args:
        slug: The recipe's slug identifier (required)
        parsed_ingredients: List of parsed ingredient dicts from mealie_parser_ingredients_batch.
            Each dict should have an 'ingredient' field with structured data containing:
            - quantity: number (e.g., 2.0)
            - unit: string or dict with name (e.g., "cup" or {"name": "cup"})
            - food: string or dict with name (e.g., "flour" or {"name": "flour"})
            - note: optional string (e.g., "sifted")
            - display: optional string for human-readable format

    Returns:
        JSON string with updated recipe details

    Example workflow:
        1. Parse ingredients:
           parsed = mealie_parser_ingredients_batch(["2 cups flour", "1 tsp salt"])

        2. Update recipe with parsed data:
           mealie_recipes_update_structured_ingredients(
               slug="my-recipe",
               parsed_ingredients=parsed['parsed_ingredients']
           )

        3. Recipe now has structured ingredients with quantity, unit, and food fields populated

    Use cases:
        - Convert text-only ingredients to structured format for better data management
        - Import recipes with structured ingredient data
        - Enable recipe scaling and unit conversions
        - Improve shopping list generation with structured data
    """
    return recipes_update_structured_ingredients(
        slug=slug,
        parsed_ingredients=parsed_ingredients
    )


@mcp.tool()
def mealie_recipes_delete(slug: str) -> str:
    """Delete a recipe from Mealie.

    Args:
        slug: The recipe's slug identifier

    Returns:
        JSON string confirming deletion
    """
    return recipes_delete(slug=slug)


# -----------------------------------------------------------------------------
# Meal Plan Tools (Phase 2)
# -----------------------------------------------------------------------------

@mcp.tool()
def mealie_mealplans_list(
    start_date: str | None = None,
    end_date: str | None = None
) -> str:
    """List meal plans for a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format (defaults to today)
        end_date: End date in YYYY-MM-DD format (defaults to 7 days from start)

    Returns:
        JSON string with list of meal plan entries
    """
    return mealplans_list(start_date=start_date, end_date=end_date)


@mcp.tool()
def mealie_mealplans_today() -> str:
    """Get today's meal plan entries.

    Returns:
        JSON string with today's meals organized by entry type (breakfast, lunch, dinner, etc.)
    """
    return mealplans_today()


@mcp.tool()
def mealie_mealplans_get(mealplan_id: str) -> str:
    """Get a specific meal plan entry by ID.

    Args:
        mealplan_id: The meal plan entry ID

    Returns:
        JSON string with meal plan entry details
    """
    return mealplans_get(mealplan_id=mealplan_id)


@mcp.tool()
def mealie_mealplans_get_date(meal_date: str) -> str:
    """Get all meal plan entries for a specific date.

    Args:
        meal_date: Date in YYYY-MM-DD format

    Returns:
        JSON string with all meals for that date organized by type
    """
    return mealplans_get_by_date(meal_date=meal_date)


@mcp.tool()
def mealie_mealplans_create(
    meal_date: str,
    entry_type: str,
    recipe_id: str | None = None,
    title: str | None = None,
    text: str | None = None
) -> str:
    """Create a new meal plan entry.

    Args:
        meal_date: Date for the meal in YYYY-MM-DD format
        entry_type: Type of meal - breakfast, lunch, dinner, side, or snack
        recipe_id: Optional recipe ID to associate with this entry
        title: Optional title for the entry (used if no recipe)
        text: Optional note or description

    Returns:
        JSON string with created meal plan entry
    """
    return mealplans_create(
        meal_date=meal_date,
        entry_type=entry_type,
        recipe_id=recipe_id,
        title=title,
        text=text
    )


@mcp.tool()
def mealie_mealplans_update(
    mealplan_id: str,
    meal_date: str | None = None,
    entry_type: str | None = None,
    recipe_id: str | None = None,
    title: str | None = None,
    text: str | None = None
) -> str:
    """Update an existing meal plan entry.

    Args:
        mealplan_id: The meal plan entry ID to update
        meal_date: Optional new date in YYYY-MM-DD format
        entry_type: Optional new meal type - breakfast, lunch, dinner, side, or snack
        recipe_id: Optional new recipe ID
        title: Optional new title
        text: Optional new note or description

    Returns:
        JSON string with updated meal plan entry
    """
    return mealplans_update(
        mealplan_id=mealplan_id,
        meal_date=meal_date,
        entry_type=entry_type,
        recipe_id=recipe_id,
        title=title,
        text=text
    )


@mcp.tool()
def mealie_mealplans_delete(mealplan_id: str) -> str:
    """Delete a meal plan entry.

    Args:
        mealplan_id: The meal plan entry ID to delete

    Returns:
        JSON string confirming deletion
    """
    return mealplans_delete(mealplan_id=mealplan_id)


@mcp.tool()
def mealie_mealplans_random() -> str:
    """Get a random meal suggestion from available recipes.

    Returns:
        JSON string with a suggested recipe for meal planning
    """
    return mealplans_random()


# -----------------------------------------------------------------------------
# Shopping List Tools (Phase 3)
# -----------------------------------------------------------------------------

@mcp.tool()
def mealie_shopping_lists_list() -> str:
    """List all shopping lists.

    Returns:
        JSON string with list of shopping lists and their metadata
    """
    return shopping_lists_list()


@mcp.tool()
def mealie_shopping_lists_get(list_id: str) -> str:
    """Get a specific shopping list with all items.

    Args:
        list_id: The shopping list ID

    Returns:
        JSON string with shopping list details and items
    """
    return shopping_lists_get(list_id=list_id)


@mcp.tool()
def mealie_shopping_lists_create(name: str) -> str:
    """Create a new shopping list.

    Args:
        name: Name for the new shopping list

    Returns:
        JSON string with created shopping list details
    """
    return shopping_lists_create(name=name)


@mcp.tool()
def mealie_shopping_lists_delete(list_id: str) -> str:
    """Delete a shopping list.

    Args:
        list_id: The shopping list ID to delete

    Returns:
        JSON string confirming deletion
    """
    return shopping_lists_delete(list_id=list_id)


@mcp.tool()
def mealie_shopping_items_add(
    list_id: str,
    note: str | None = None,
    quantity: float | None = None,
    unit_id: str | None = None,
    food_id: str | None = None,
    display: str | None = None
) -> str:
    """Add an item to a shopping list.

    Args:
        list_id: The shopping list ID to add the item to
        note: Text description of the item (simplest way to add items)
        quantity: Quantity of the item
        unit_id: ID of the unit (e.g., cups, pounds)
        food_id: ID of the food from Mealie's food database
        display: Display text for the item

    Returns:
        JSON string with the added item
    """
    return shopping_items_add(
        list_id=list_id,
        note=note,
        quantity=quantity,
        unit_id=unit_id,
        food_id=food_id,
        display=display
    )


@mcp.tool()
def mealie_shopping_items_add_bulk(
    list_id: str,
    items: list[str]
) -> str:
    """Add multiple items to a shopping list at once.

    Args:
        list_id: The shopping list ID to add items to
        items: List of item descriptions (text notes)

    Returns:
        JSON string with count of added items
    """
    return shopping_items_add_bulk(list_id=list_id, items=items)


@mcp.tool()
def mealie_shopping_items_check(
    item_id: str,
    checked: bool = True
) -> str:
    """Mark a shopping list item as checked or unchecked.

    Args:
        item_id: The shopping list item ID
        checked: True to mark as checked/purchased, False to uncheck

    Returns:
        JSON string confirming the update
    """
    return shopping_items_check(item_id=item_id, checked=checked)


@mcp.tool()
def mealie_shopping_items_delete(item_id: str) -> str:
    """Remove an item from a shopping list.

    Args:
        item_id: The shopping list item ID to remove

    Returns:
        JSON string confirming deletion
    """
    return shopping_items_delete(item_id=item_id)


@mcp.tool()
def mealie_shopping_add_recipe(
    list_id: str,
    recipe_id: str,
    scale: float = 1.0
) -> str:
    """Add all ingredients from a recipe to a shopping list.

    Args:
        list_id: The shopping list ID to add ingredients to
        recipe_id: The recipe ID to get ingredients from
        scale: Scale factor for ingredient quantities (default 1.0)

    Returns:
        JSON string with updated shopping list
    """
    return shopping_items_add_recipe(list_id=list_id, recipe_id=recipe_id, scale=scale)


@mcp.tool()
def mealie_shopping_generate_from_mealplan(
    start_date: str | None = None,
    end_date: str | None = None,
    list_name: str | None = None
) -> str:
    """Generate a shopping list from meal plan entries.

    This is the highest-value tool for household workflow - it reads the meal plan
    for a date range and creates a shopping list with all required ingredients.

    Args:
        start_date: Start date in YYYY-MM-DD format (defaults to today)
        end_date: End date in YYYY-MM-DD format (defaults to 7 days from start)
        list_name: Optional name for the shopping list (defaults to "Meal Plan - {date range}")

    Returns:
        JSON string with created shopping list details
    """
    return shopping_generate_from_mealplan(
        start_date=start_date,
        end_date=end_date,
        list_name=list_name
    )


@mcp.tool()
def mealie_shopping_clear_checked(list_id: str) -> str:
    """Remove all checked items from a shopping list.

    Args:
        list_id: The shopping list ID

    Returns:
        JSON string with count of removed items
    """
    return shopping_lists_clear_checked(list_id=list_id)


# -----------------------------------------------------------------------------
# Parser Tools (Phase 5)
# -----------------------------------------------------------------------------

@mcp.tool()
def mealie_parser_ingredient(ingredient: str, parser: str = "nlp") -> str:
    """Parse a single ingredient string to structured format.

    This tool uses Mealie's ingredient parser to extract structured data from
    natural language ingredient descriptions. The parsed result includes:
    - Quantity (e.g., 2.0)
    - Unit (e.g., "cups", "tsp", "oz")
    - Food name (e.g., "flour", "salt", "butter")
    - Confidence scores for each component

    Args:
        ingredient: Ingredient string to parse (e.g., "2 cups flour", "1 tsp salt")
        parser: Parser type - "nlp" (default, best for most cases), "brute", or "openai"

    Returns:
        JSON string with parsed ingredient structure:
        - input: Original ingredient text
        - confidence: Confidence scores for parsed components
        - ingredient: Structured data with quantity, unit, food, display

    Examples:
        "2 cups flour" -> quantity: 2.0, unit: "cup", food: "flour"
        "1 tsp salt" -> quantity: 1.0, unit: "teaspoon", food: "salt"
        "1/2 cup butter" -> quantity: 0.5, unit: "cup", food: "butter"
    """
    return parser_ingredient(ingredient=ingredient, parser=parser)


@mcp.tool()
def mealie_parser_ingredients_batch(ingredients: list[str], parser: str = "nlp") -> str:
    """Parse multiple ingredient strings to structured format.

    Batch version of mealie_parser_ingredient that efficiently parses multiple
    ingredients at once. Useful when processing full recipe ingredient lists.

    Args:
        ingredients: List of ingredient strings to parse
        parser: Parser type - "nlp" (default, best for most cases), "brute", or "openai"

    Returns:
        JSON string with array of parsed ingredients, each containing:
        - input: Original ingredient text
        - confidence: Confidence scores
        - ingredient: Structured data with quantity, unit, food, display

    Example:
        ingredients: ["2 cups flour", "1 tsp salt", "1/2 cup butter"]
        Returns array with 3 parsed ingredient objects
    """
    return parser_ingredients_batch(ingredients=ingredients, parser=parser)


# =============================================================================
# Resources - Context the AI can read
# =============================================================================

@mcp.resource("recipes://list")
def resource_recipes_list() -> str:
    """Browse all recipes in Mealie organized by category."""
    return get_recipes_list()


@mcp.resource("recipes://{slug}")
def resource_recipe_detail(slug: str) -> str:
    """Get detailed information about a specific recipe."""
    return get_recipe_detail(slug)


@mcp.resource("mealplans://current")
def resource_current_mealplan() -> str:
    """View the current week's meal plan (Monday-Sunday)."""
    return get_current_mealplan()


@mcp.resource("mealplans://today")
def resource_today_meals() -> str:
    """View today's planned meals."""
    return get_today_meals()


@mcp.resource("mealplans://{date}")
def resource_mealplan_date(date: str) -> str:
    """View meals planned for a specific date (YYYY-MM-DD format)."""
    from resources.mealplans import get_current_mealplan
    # Reuse the mealplans_get_by_date tool but format as markdown
    result = mealplans_get_by_date(date)
    import json
    data = json.loads(result)

    if "error" in data:
        return f"Error: {data['error']}"

    output = [f"# Meals for {data['date']}", ""]

    if data["count"] == 0:
        output.append("*No meals planned for this date*")
        return "\n".join(output)

    meals = data.get("meals", {})
    for meal_type in ["breakfast", "lunch", "dinner", "side", "snack"]:
        if meal_type in meals:
            output.append(f"## {meal_type.capitalize()}")
            output.append("")
            for meal in meals[meal_type]:
                name = meal.get("recipe_name") or meal.get("title") or "Untitled"
                slug = meal.get("recipe_slug")
                output.append(f"- **{name}**" + (f" (`{slug}`)" if slug else ""))
                if meal.get("text"):
                    output.append(f"  - *Note: {meal['text']}*")
            output.append("")

    return "\n".join(output)


@mcp.resource("shopping://lists")
def resource_shopping_lists() -> str:
    """View all shopping lists with item counts."""
    return get_shopping_lists()


@mcp.resource("shopping://{list_id}")
def resource_shopping_list_detail(list_id: str) -> str:
    """View a specific shopping list with all items."""
    return get_shopping_list_detail(list_id)


# =============================================================================
# Server entry point
# =============================================================================

if __name__ == "__main__":
    mcp.run()
