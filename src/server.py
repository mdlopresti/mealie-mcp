"""
Mealie MCP Server

FastMCP-based Model Context Protocol server for Mealie integration.
Provides tools and resources for recipe management, meal planning, and shopping lists.
"""

import os
import sys
from pathlib import Path
from typing import Any, Optional

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
    recipes_duplicate,
    recipes_update_last_made,
    recipes_create_from_urls_bulk,
    recipes_bulk_tag,
    recipes_bulk_categorize,
    recipes_bulk_delete,
    recipes_bulk_export,
    recipes_bulk_update_settings,
    recipes_create_from_image,
    recipes_upload_image_from_url,
)
from tools.timeline import (
    timeline_list,
    timeline_get,
    timeline_create,
    timeline_update,
    timeline_delete,
    timeline_update_image,
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
    mealplans_search,
    mealplans_delete_range,
    mealplans_update_batch,
    mealplan_rules_list,
    mealplan_rules_get,
    mealplan_rules_create,
    mealplan_rules_update,
    mealplan_rules_delete,
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
    shopping_delete_recipe_from_list,
)
from tools.parser import (
    parser_ingredient,
    parser_ingredients_batch,
)
from tools.foods import (
    foods_list,
    foods_create,
    foods_get,
    foods_update,
    foods_delete,
    foods_merge,
    units_list,
    units_create,
    units_get,
    units_update,
    units_delete,
    units_merge,
)
from tools.organizers import (
    categories_list,
    categories_create,
    categories_get,
    categories_update,
    categories_delete,
    tags_list,
    tags_create,
    tags_get,
    tags_update,
    tags_delete,
    tools_list,
    tools_create,
    tools_get,
    tools_update,
    tools_delete,
)
from tools.cookbooks import (
    cookbooks_list,
    cookbooks_create,
    cookbooks_get,
    cookbooks_update,
    cookbooks_delete,
)
from tools.comments import (
    comments_get_recipe,
    comments_create,
    comments_get,
    comments_update,
    comments_delete,
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


@mcp.tool()
def mealie_recipes_duplicate(slug: str, new_name: str | None = None) -> str:
    """Duplicate an existing recipe.

    Args:
        slug: The recipe's slug identifier to duplicate
        new_name: Optional new name for the duplicated recipe (defaults to "Copy of {original_name}")

    Returns:
        JSON string with the newly created recipe data
    """
    return recipes_duplicate(slug=slug, new_name=new_name)


@mcp.tool()
def mealie_recipes_update_last_made(slug: str, timestamp: str | None = None) -> str:
    """Update the last made timestamp for a recipe.

    Args:
        slug: The recipe's slug identifier
        timestamp: Optional ISO 8601 timestamp (defaults to current time on server)

    Returns:
        JSON string with updated recipe data
    """
    return recipes_update_last_made(slug=slug, timestamp=timestamp)


@mcp.tool()
def mealie_recipes_create_from_urls_bulk(urls: list[str], include_tags: bool = False) -> str:
    """Import multiple recipes from URLs at once.

    Args:
        urls: List of recipe URLs to import
        include_tags: Whether to include tags from scraped recipes (default False)

    Returns:
        JSON string with import results for each URL
    """
    return recipes_create_from_urls_bulk(urls=urls, include_tags=include_tags)


@mcp.tool()
def mealie_recipes_bulk_tag(recipe_ids: list[str], tags: list[str]) -> str:
    """Add tags to multiple recipes at once.

    Args:
        recipe_ids: List of recipe IDs to tag
        tags: List of tag names to add

    Returns:
        JSON string with bulk action results
    """
    return recipes_bulk_tag(recipe_ids=recipe_ids, tags=tags)


@mcp.tool()
def mealie_recipes_bulk_categorize(recipe_ids: list[str], categories: list[str]) -> str:
    """Add categories to multiple recipes at once.

    Args:
        recipe_ids: List of recipe IDs to categorize
        categories: List of category names to add

    Returns:
        JSON string with bulk action results
    """
    return recipes_bulk_categorize(recipe_ids=recipe_ids, categories=categories)


@mcp.tool()
def mealie_recipes_bulk_delete(recipe_ids: list[str]) -> str:
    """Delete multiple recipes at once.

    Args:
        recipe_ids: List of recipe IDs to delete

    Returns:
        JSON string with bulk action results
    """
    return recipes_bulk_delete(recipe_ids=recipe_ids)


@mcp.tool()
def mealie_recipes_bulk_export(recipe_ids: list[str], export_format: str = "json") -> str:
    """Export multiple recipes at once.

    Args:
        recipe_ids: List of recipe IDs to export
        export_format: Export format (json, zip, etc.)

    Returns:
        JSON string with export data
    """
    return recipes_bulk_export(recipe_ids=recipe_ids, export_format=export_format)


@mcp.tool()
def mealie_recipes_bulk_update_settings(recipe_ids: list[str], settings: dict[str, Any]) -> str:
    """Update settings for multiple recipes at once.

    Args:
        recipe_ids: List of recipe IDs to update
        settings: Settings to update (e.g., {"public": true, "show_nutrition": false})

    Returns:
        JSON string with bulk action results
    """
    return recipes_bulk_update_settings(recipe_ids=recipe_ids, settings=settings)


@mcp.tool()
def mealie_recipes_create_from_image(image_data: str, extension: str = "jpg") -> str:
    """Create a recipe from an image using AI (experimental).

    Args:
        image_data: Base64 encoded image data
        extension: Image file extension (jpg, png, etc.)

    Returns:
        JSON string with created recipe data
    """
    return recipes_create_from_image(image_data=image_data, extension=extension)


@mcp.tool()
def mealie_recipes_upload_image_from_url(slug: str, image_url: str) -> str:
    """Upload an image to an existing recipe from a URL.

    Downloads an image from the provided URL and uploads it to the specified recipe.
    The image will be automatically resized and optimized by Mealie.

    Args:
        slug: Recipe slug identifier
        image_url: Full URL of the image to download and upload

    Returns:
        JSON string with upload confirmation or error details

    Example:
        mealie_recipes_upload_image_from_url(
            slug="sous-vide-salmon",
            image_url="https://images.anovaculinary.com/sous-vide-salmon-2/header/sous-vide-salmon-2-header-centered.jpg"
        )
    """
    return recipes_upload_image_from_url(slug=slug, image_url=image_url)


@mcp.tool()
def mealie_recipes_set_rating(slug: str, rating: float, is_favorite: bool | None = None) -> str:
    """Set a rating (1-5 stars) for a recipe.

    Allows users to rate recipes on a 1-5 star scale. Ratings help track favorite recipes
    and inform meal planning decisions.

    Args:
        slug: Recipe slug identifier
        rating: Rating value (0-5 stars, can be decimal like 4.5). Use 0 to clear rating.
        is_favorite: Optional flag to mark as favorite (default: None)

    Returns:
        JSON string with updated rating data

    Example:
        mealie_recipes_set_rating(slug="chicken-parmesan", rating=5.0)
        mealie_recipes_set_rating(slug="chicken-parmesan", rating=4.5, is_favorite=True)
    """
    return set_recipe_rating(slug=slug, rating=rating, is_favorite=is_favorite)


@mcp.tool()
def mealie_recipes_get_ratings() -> str:
    """Get all ratings for the current user.

    Returns a list of all recipes the user has rated, including the rating value
    and favorite status for each recipe.

    Returns:
        JSON string with list of rated recipes and their ratings

    Example:
        mealie_recipes_get_ratings()
    """
    return get_user_ratings()


@mcp.tool()
def mealie_recipes_get_rating(recipe_id: str) -> str:
    """Get rating for a specific recipe.

    Retrieves the current user's rating for a specific recipe by its ID.

    Args:
        recipe_id: Recipe ID (UUID)

    Returns:
        JSON string with recipe rating data

    Example:
        mealie_recipes_get_rating(recipe_id="550e8400-e29b-41d4-a716-446655440000")
    """
    return get_recipe_rating(recipe_id=recipe_id)


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
        recipe_id: New recipe ID. Pass "__CLEAR__" to remove recipe association.
        title: New title. Pass "__CLEAR__" to clear the title.
        text: New note. Pass "__CLEAR__" to clear the note.

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


@mcp.tool()
def mealie_mealplans_search(
    query: str,
    start_date: str | None = None,
    end_date: str | None = None
) -> str:
    """Search meal plans by recipe name, title, or text content.

    This tool searches through meal plans in a date range and returns
    entries matching the search query. The search is case-insensitive
    and matches against:
    - Recipe names (if a recipe is assigned)
    - Entry titles
    - Entry text/notes

    Args:
        query: Search term to filter meal plans (case-insensitive)
        start_date: Start date in YYYY-MM-DD format (defaults to today)
        end_date: End date in YYYY-MM-DD format (defaults to 7 days from start)

    Returns:
        JSON string with matching meal plan entries

    Examples:
        # Find all meal plans with "pork" in recipe name/title/notes
        mealie_mealplans_search("pork")

        # Search within specific date range
        mealie_mealplans_search("freezer meal", "2025-01-01", "2025-01-31")
    """
    return mealplans_search(query=query, start_date=start_date, end_date=end_date)


@mcp.tool()
def mealie_mealplans_delete_range(
    start_date: str | None = None,
    end_date: str | None = None
) -> str:
    """Delete all meal plans in a date range.

    This tool retrieves all meal plans in the specified date range and deletes
    them one by one. Useful for clearing out old or incorrect meal plans.

    Args:
        start_date: Start date in YYYY-MM-DD format (defaults to today)
        end_date: End date in YYYY-MM-DD format (defaults to 7 days from start)

    Returns:
        JSON string with deletion results

    Example:
        # Delete all meal plans for January 2025
        mealie_mealplans_delete_range("2025-01-01", "2025-01-31")
    """
    return mealplans_delete_range(start_date=start_date, end_date=end_date)


@mcp.tool()
def mealie_mealplans_update_batch(updates: list[dict]) -> str:
    """Update multiple meal plans at once.

    This tool updates multiple meal plan entries in a single call. Each update
    should specify the meal plan ID and the fields to update.

    Args:
        updates: List of update dictionaries, each containing:
            - mealplan_id (required): The meal plan entry ID to update
            - meal_date (optional): New date in YYYY-MM-DD format
            - entry_type (optional): New meal type (breakfast, lunch, dinner, side, snack)
            - recipe_id (optional): New recipe ID or "__CLEAR__" to remove
            - title (optional): New title or "__CLEAR__" to clear
            - text (optional): New note or "__CLEAR__" to clear

    Returns:
        JSON string with batch update results

    Examples:
        # Update two meal plans at once
        updates = [
            {"mealplan_id": "meal-1", "meal_date": "2025-01-21"},
            {"mealplan_id": "meal-2", "entry_type": "lunch", "text": "Updated note"}
        ]
        mealie_mealplans_update_batch(updates)

        # Clear recipe from a meal plan
        updates = [{"mealplan_id": "meal-1", "recipe_id": "__CLEAR__"}]
        mealie_mealplans_update_batch(updates)
    """
    return mealplans_update_batch(updates=updates)


@mcp.tool()
def mealie_mealplan_rules_list() -> str:
    """List all meal plan rules.

    Returns:
        JSON string with list of meal plan rules
    """
    return mealplan_rules_list()


@mcp.tool()
def mealie_mealplan_rules_get(rule_id: str) -> str:
    """Get a specific meal plan rule by ID.

    Args:
        rule_id: The meal plan rule ID

    Returns:
        JSON string with rule details
    """
    return mealplan_rules_get(rule_id=rule_id)


@mcp.tool()
def mealie_mealplan_rules_create(
    name: str,
    entry_type: str,
    tags: list[str] | None = None,
    categories: list[str] | None = None
) -> str:
    """Create a new meal plan rule.

    Args:
        name: Rule name
        entry_type: Entry type (breakfast, lunch, dinner, side, snack)
        tags: List of tag names to filter by
        categories: List of category names to filter by

    Returns:
        JSON string with created rule details
    """
    return mealplan_rules_create(name=name, entry_type=entry_type, tags=tags, categories=categories)


@mcp.tool()
def mealie_mealplan_rules_update(
    rule_id: str,
    name: str | None = None,
    entry_type: str | None = None,
    tags: list[str] | None = None,
    categories: list[str] | None = None
) -> str:
    """Update an existing meal plan rule.

    Args:
        rule_id: The meal plan rule ID
        name: New rule name
        entry_type: New entry type (breakfast, lunch, dinner, side, snack)
        tags: New list of tag names to filter by
        categories: New list of category names to filter by

    Returns:
        JSON string with updated rule details
    """
    return mealplan_rules_update(
        rule_id=rule_id,
        name=name,
        entry_type=entry_type,
        tags=tags,
        categories=categories
    )


@mcp.tool()
def mealie_mealplan_rules_delete(rule_id: str) -> str:
    """Delete a meal plan rule.

    Args:
        rule_id: The meal plan rule ID to delete

    Returns:
        JSON string confirming deletion
    """
    return mealplan_rules_delete(rule_id=rule_id)


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


@mcp.tool()
def mealie_shopping_delete_recipe_from_list(item_id: str, recipe_id: str) -> str:
    """Remove recipe ingredients from a shopping list.

    Args:
        item_id: The shopping list item ID
        recipe_id: The recipe ID whose ingredients to remove

    Returns:
        JSON string with removal results
    """
    return shopping_delete_recipe_from_list(item_id=item_id, recipe_id=recipe_id)


# -----------------------------------------------------------------------------
# Foods & Units Management Tools
# -----------------------------------------------------------------------------

@mcp.tool()
def mealie_foods_list(page: int = 1, per_page: int = 50) -> str:
    """List all foods with pagination.

    Args:
        page: Page number (1-indexed)
        per_page: Number of foods per page

    Returns:
        JSON string with paginated food list
    """
    return foods_list(page=page, per_page=per_page)


@mcp.tool()
def mealie_foods_create(
    name: str,
    description: str = None,
    label_id: str = None
) -> str:
    """Create a new food.

    Args:
        name: Name for the new food
        description: Optional description
        label_id: Optional label ID (UUID) to assign

    Returns:
        JSON string with created food details
    """
    return foods_create(name=name, description=description, label_id=label_id)


@mcp.tool()
def mealie_foods_get(food_id: str) -> str:
    """Get a specific food by ID.

    Args:
        food_id: The food's ID

    Returns:
        JSON string with food details
    """
    return foods_get(food_id=food_id)


@mcp.tool()
def mealie_foods_update(
    food_id: str,
    name: str | None = None,
    description: str | None = None,
    label_id: str | None = None
) -> str:
    """Update an existing food.

    Args:
        food_id: The food's ID
        name: New name for the food
        description: New description
        label_id: Label ID (UUID) to assign to the food

    Returns:
        JSON string with updated food details
    """
    return foods_update(food_id=food_id, name=name, description=description, label_id=label_id)


@mcp.tool()
def mealie_foods_delete(food_id: str) -> str:
    """Delete a food.

    Args:
        food_id: The food's ID to delete

    Returns:
        JSON string confirming deletion
    """
    return foods_delete(food_id=food_id)


@mcp.tool()
def mealie_foods_merge(from_food_id: str, to_food_id: str) -> str:
    """Merge one food into another (combines usage across recipes).

    Args:
        from_food_id: Source food ID (will be deleted)
        to_food_id: Target food ID (will absorb all references)

    Returns:
        JSON string with merge results
    """
    return foods_merge(from_food_id=from_food_id, to_food_id=to_food_id)


@mcp.tool()
def mealie_units_list(page: int = 1, per_page: int = 50) -> str:
    """List all units with pagination.

    Args:
        page: Page number (1-indexed)
        per_page: Number of units per page

    Returns:
        JSON string with paginated unit list
    """
    return units_list(page=page, per_page=per_page)


@mcp.tool()
def mealie_units_create(
    name: str,
    description: str = None,
    abbreviation: str = None
) -> str:
    """Create a new unit.

    Args:
        name: Name for the new unit
        description: Optional description
        abbreviation: Optional abbreviation (e.g., "tsp", "oz")

    Returns:
        JSON string with created unit details
    """
    return units_create(name=name, description=description, abbreviation=abbreviation)


@mcp.tool()
def mealie_units_get(unit_id: str) -> str:
    """Get a specific unit by ID.

    Args:
        unit_id: The unit's ID

    Returns:
        JSON string with unit details
    """
    return units_get(unit_id=unit_id)


@mcp.tool()
def mealie_units_update(
    unit_id: str,
    name: str | None = None,
    description: str | None = None,
    abbreviation: str | None = None
) -> str:
    """Update an existing unit.

    Args:
        unit_id: The unit's ID
        name: New name for the unit
        description: New description
        abbreviation: New abbreviation

    Returns:
        JSON string with updated unit details
    """
    return units_update(unit_id=unit_id, name=name, description=description, abbreviation=abbreviation)


@mcp.tool()
def mealie_units_delete(unit_id: str) -> str:
    """Delete a unit.

    Args:
        unit_id: The unit's ID to delete

    Returns:
        JSON string confirming deletion
    """
    return units_delete(unit_id=unit_id)


@mcp.tool()
def mealie_units_merge(from_unit_id: str, to_unit_id: str) -> str:
    """Merge one unit into another (combines usage across recipes).

    Args:
        from_unit_id: Source unit ID (will be deleted)
        to_unit_id: Target unit ID (will absorb all references)

    Returns:
        JSON string with merge results
    """
    return units_merge(from_unit_id=from_unit_id, to_unit_id=to_unit_id)


# -----------------------------------------------------------------------------
# Organizers Management Tools (Categories, Tags, Tools)
# -----------------------------------------------------------------------------

@mcp.tool()
def mealie_categories_list() -> str:
    """List all categories.

    Returns:
        JSON string with list of categories
    """
    return categories_list()


@mcp.tool()
def mealie_categories_create(name: str) -> str:
    """Create a new category.

    Args:
        name: Name for the new category

    Returns:
        JSON string with created category details
    """
    return categories_create(name=name)


@mcp.tool()
def mealie_categories_get(category_id: str) -> str:
    """Get a category by ID.

    Args:
        category_id: The category's ID

    Returns:
        JSON string with category details
    """
    return categories_get(category_id=category_id)


@mcp.tool()
def mealie_categories_update(
    category_id: str,
    name: str | None = None,
    slug: str | None = None
) -> str:
    """Update a category.

    Args:
        category_id: The category's ID
        name: New name for the category
        slug: New slug for the category

    Returns:
        JSON string with updated category details
    """
    return categories_update(category_id=category_id, name=name, slug=slug)


@mcp.tool()
def mealie_categories_delete(category_id: str) -> str:
    """Delete a category.

    Args:
        category_id: The category's ID to delete

    Returns:
        JSON string confirming deletion
    """
    return categories_delete(category_id=category_id)


@mcp.tool()
def mealie_tags_list() -> str:
    """List all tags.

    Returns:
        JSON string with list of tags
    """
    return tags_list()


@mcp.tool()
def mealie_tags_create(name: str) -> str:
    """Create a new tag.

    Args:
        name: Name for the new tag

    Returns:
        JSON string with created tag details
    """
    return tags_create(name=name)


@mcp.tool()
def mealie_tags_get(tag_id: str) -> str:
    """Get a tag by ID.

    Args:
        tag_id: The tag's ID

    Returns:
        JSON string with tag details
    """
    return tags_get(tag_id=tag_id)


@mcp.tool()
def mealie_tags_update(
    tag_id: str,
    name: str | None = None,
    slug: str | None = None
) -> str:
    """Update a tag.

    Args:
        tag_id: The tag's ID
        name: New name for the tag
        slug: New slug for the tag

    Returns:
        JSON string with updated tag details
    """
    return tags_update(tag_id=tag_id, name=name, slug=slug)


@mcp.tool()
def mealie_tags_delete(tag_id: str) -> str:
    """Delete a tag.

    Args:
        tag_id: The tag's ID to delete

    Returns:
        JSON string confirming deletion
    """
    return tags_delete(tag_id=tag_id)


@mcp.tool()
def mealie_tools_list() -> str:
    """List all kitchen tools.

    Returns:
        JSON string with list of tools
    """
    return tools_list()


@mcp.tool()
def mealie_tools_create(name: str) -> str:
    """Create a new kitchen tool.

    Args:
        name: Name for the new tool

    Returns:
        JSON string with created tool details
    """
    return tools_create(name=name)


@mcp.tool()
def mealie_tools_get(tool_id: str) -> str:
    """Get a kitchen tool by ID.

    Args:
        tool_id: The tool's ID

    Returns:
        JSON string with tool details
    """
    return tools_get(tool_id=tool_id)


@mcp.tool()
def mealie_tools_update(
    tool_id: str,
    name: str | None = None,
    slug: str | None = None
) -> str:
    """Update a tool.

    Args:
        tool_id: The tool's ID
        name: New name for the tool
        slug: New slug for the tool

    Returns:
        JSON string with updated tool details
    """
    return tools_update(tool_id=tool_id, name=name, slug=slug)


@mcp.tool()
def mealie_tools_delete(tool_id: str) -> str:
    """Delete a tool.

    Args:
        tool_id: The tool's ID to delete

    Returns:
        JSON string confirming deletion
    """
    return tools_delete(tool_id=tool_id)


# -----------------------------------------------------------------------------
# Cookbooks Management Tools
# -----------------------------------------------------------------------------

@mcp.tool()
def mealie_cookbooks_list() -> str:
    """List all cookbooks.

    Returns:
        JSON string with list of cookbooks
    """
    return cookbooks_list()


@mcp.tool()
def mealie_cookbooks_create(
    name: str,
    description: str = None,
    slug: str = None,
    public: bool = False
) -> str:
    """Create a new cookbook.

    Args:
        name: Name for the new cookbook
        description: Optional description
        slug: Optional URL slug
        public: Whether the cookbook is public (default: False)

    Returns:
        JSON string with created cookbook details
    """
    return cookbooks_create(name=name, description=description, slug=slug, public=public)


@mcp.tool()
def mealie_cookbooks_get(cookbook_id: str) -> str:
    """Get a cookbook by ID.

    Args:
        cookbook_id: The cookbook's ID

    Returns:
        JSON string with cookbook details
    """
    return cookbooks_get(cookbook_id=cookbook_id)


@mcp.tool()
def mealie_cookbooks_update(
    cookbook_id: str,
    name: str = None,
    description: str = None,
    slug: str = None,
    public: bool = None
) -> str:
    """Update a cookbook.

    Args:
        cookbook_id: The cookbook's ID
        name: New name for the cookbook
        description: New description
        slug: New URL slug
        public: Whether the cookbook is public

    Returns:
        JSON string with updated cookbook details
    """
    return cookbooks_update(
        cookbook_id=cookbook_id,
        name=name,
        description=description,
        slug=slug,
        public=public
    )


@mcp.tool()
def mealie_cookbooks_delete(cookbook_id: str) -> str:
    """Delete a cookbook.

    Args:
        cookbook_id: The cookbook's ID to delete

    Returns:
        JSON string confirming deletion
    """
    return cookbooks_delete(cookbook_id=cookbook_id)


# -----------------------------------------------------------------------------
# Recipe Comments Management Tools
# -----------------------------------------------------------------------------

@mcp.tool()
def mealie_comments_get_recipe(recipe_slug: str) -> str:
    """Get all comments for a recipe.

    Args:
        recipe_slug: Recipe slug identifier

    Returns:
        JSON string with list of comments
    """
    return comments_get_recipe(recipe_slug=recipe_slug)


@mcp.tool()
def mealie_comments_create(recipe_id: str, text: str) -> str:
    """Create a comment on a recipe.

    Args:
        recipe_id: Recipe ID
        text: Comment text

    Returns:
        JSON string with created comment
    """
    return comments_create(recipe_id=recipe_id, text=text)


@mcp.tool()
def mealie_comments_get(comment_id: str) -> str:
    """Get a comment by ID.

    Args:
        comment_id: Comment ID

    Returns:
        JSON string with comment details
    """
    return comments_get(comment_id=comment_id)


@mcp.tool()
def mealie_comments_update(comment_id: str, text: str) -> str:
    """Update a comment.

    Args:
        comment_id: Comment ID
        text: New comment text

    Returns:
        JSON string with updated comment
    """
    return comments_update(comment_id=comment_id, text=text)


@mcp.tool()
def mealie_comments_delete(comment_id: str) -> str:
    """Delete a comment.

    Args:
        comment_id: Comment ID to delete

    Returns:
        JSON string confirming deletion
    """
    return comments_delete(comment_id=comment_id)


# -----------------------------------------------------------------------------
# Parser Tools (Phase 5)
# -----------------------------------------------------------------------------

# =============================================================================
# Recipe Timeline Events
# =============================================================================

@mcp.tool()
def mealie_timeline_list(
    page: int = 1,
    per_page: int = 50,
    order_by: Optional[str] = None,
    order_direction: Optional[str] = None,
    query_filter: Optional[str] = None,
) -> str:
    """List all recipe timeline events with pagination.

    Timeline events track when recipes were made and build cooking history analytics.

    Args:
        page: Page number (1-indexed)
        per_page: Number of events per page
        order_by: Field to order by
        order_direction: "asc" or "desc"
        query_filter: Filter query string

    Returns:
        JSON string with paginated timeline events data
    """
    return timeline_list(
        page=page,
        per_page=per_page,
        order_by=order_by,
        order_direction=order_direction,
        query_filter=query_filter,
    )


@mcp.tool()
def mealie_timeline_get(event_id: str) -> str:
    """Get a specific timeline event by ID.

    Args:
        event_id: Timeline event ID (UUID)

    Returns:
        JSON string with timeline event details
    """
    return timeline_get(event_id)


@mcp.tool()
def mealie_timeline_create(
    recipe_id: str,
    subject: str,
    event_type: str = "info",
    event_message: Optional[str] = None,
    user_id: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> str:
    """Create a new timeline event for a recipe.

    Use this to track when recipes were made or add notes to recipe history.

    Args:
        recipe_id: Recipe ID (UUID)
        subject: Event subject/title
        event_type: Event type - "system", "info", or "comment" (default: "info")
        event_message: Optional event message/description
        user_id: Optional user ID (UUID)
        timestamp: Optional ISO 8601 timestamp (defaults to current time)

    Returns:
        JSON string with created timeline event data
    """
    return timeline_create(
        recipe_id=recipe_id,
        subject=subject,
        event_type=event_type,
        event_message=event_message,
        user_id=user_id,
        timestamp=timestamp,
    )


@mcp.tool()
def mealie_timeline_update(
    event_id: str,
    subject: Optional[str] = None,
    event_type: Optional[str] = None,
    event_message: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> str:
    """Update an existing timeline event.

    Args:
        event_id: Timeline event ID (UUID)
        subject: New subject/title
        event_type: New event type - "system", "info", or "comment"
        event_message: New event message/description
        timestamp: New ISO 8601 timestamp

    Returns:
        JSON string with updated timeline event data
    """
    return timeline_update(
        event_id=event_id,
        subject=subject,
        event_type=event_type,
        event_message=event_message,
        timestamp=timestamp,
    )


@mcp.tool()
def mealie_timeline_delete(event_id: str) -> str:
    """Delete a timeline event.

    Args:
        event_id: Timeline event ID (UUID)

    Returns:
        JSON string confirming deletion
    """
    return timeline_delete(event_id)


@mcp.tool()
def mealie_timeline_update_image(event_id: str, image_url: str) -> str:
    """Upload or update an image for a timeline event from a URL.

    Downloads an image from the provided URL and uploads it to the specified
    timeline event. The image will be automatically resized and optimized by Mealie.

    Args:
        event_id: Timeline event ID (UUID)
        image_url: Full URL of the image to download and upload

    Returns:
        JSON string with upload confirmation or error details

    Example:
        mealie_timeline_update_image(
            event_id="550e8400-e29b-41d4-a716-446655440000",
            image_url="https://example.com/my-dish.jpg"
        )
    """
    return timeline_update_image(event_id=event_id, image_url=image_url)


# =============================================================================
# Ingredient Parser
# =============================================================================

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
