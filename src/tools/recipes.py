"""
Recipe tools for Mealie MCP server.

Provides tools for searching, retrieving, and listing recipes from a Mealie instance.
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional


def _slugify(text: str) -> str:
    """Convert text to a slug (lowercase, hyphens for spaces, no special chars)."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text

# Handle imports for both module usage and standalone execution
try:
    from ..client import MealieClient, MealieAPIError
except ImportError:
    # Add parent directory to path for standalone execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from client import MealieClient, MealieAPIError


def recipes_search(
    query: str = "",
    tags: Optional[list[str]] = None,
    categories: Optional[list[str]] = None,
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
    try:
        with MealieClient() as client:
            # Build query parameters
            params = {
                "perPage": limit,
                "page": 1,
            }

            if query:
                params["search"] = query

            if tags:
                params["tags"] = tags

            if categories:
                params["categories"] = categories

            # Make API request
            response = client.get("/api/recipes", params=params)

            # Extract relevant fields for readability
            if isinstance(response, dict) and "items" in response:
                recipes = []
                for recipe in response["items"]:
                    recipes.append({
                        "name": recipe.get("name"),
                        "slug": recipe.get("slug"),
                        "description": recipe.get("description"),
                        "rating": recipe.get("rating"),
                        "tags": [tag.get("name") for tag in recipe.get("tags", [])],
                        "categories": [cat.get("name") for cat in recipe.get("recipeCategory", [])],
                    })

                result = {
                    "total": response.get("total", len(recipes)),
                    "count": len(recipes),
                    "recipes": recipes
                }
                return json.dumps(result, indent=2)

            # If response doesn't match expected format, return as-is
            return json.dumps(response, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def recipes_get(slug: str) -> str:
    """Get complete details for a specific recipe.

    Args:
        slug: The recipe's URL slug identifier

    Returns:
        JSON string with full recipe details including ingredients, instructions, nutrition
    """
    try:
        with MealieClient() as client:
            # Make API request
            response = client.get(f"/api/recipes/{slug}")

            # Return full recipe data
            return json.dumps(response, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def recipes_list(page: int = 1, per_page: int = 20) -> str:
    """List all recipes with pagination.

    Args:
        page: Page number (1-indexed)
        per_page: Number of recipes per page (default 20)

    Returns:
        JSON string with paginated recipe list and metadata
    """
    try:
        with MealieClient() as client:
            # Build query parameters
            params = {
                "page": page,
                "perPage": per_page,
            }

            # Make API request
            response = client.get("/api/recipes", params=params)

            # Extract pagination metadata
            if isinstance(response, dict):
                result = {
                    "page": response.get("page", page),
                    "per_page": response.get("perPage", per_page),
                    "total": response.get("total", 0),
                    "total_pages": response.get("totalPages", 0),
                    "items": response.get("items", [])
                }
                return json.dumps(result, indent=2)

            # If response doesn't match expected format, return as-is
            return json.dumps(response, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def recipes_create(
    name: str,
    description: str = "",
    recipe_yield: str = "",
    total_time: str = "",
    prep_time: str = "",
    cook_time: str = "",
    ingredients: Optional[list[str]] = None,
    instructions: Optional[list[str]] = None,
    tags: Optional[list[str]] = None,
    categories: Optional[list[str]] = None,
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
    try:
        with MealieClient() as client:
            # Step 1: Create the recipe stub with just the name
            create_response = client.post("/api/recipes", json={"name": name})

            # The response should be a string (the slug)
            if isinstance(create_response, str):
                slug = create_response
            elif isinstance(create_response, dict):
                slug = create_response.get("slug") or create_response.get("id")
            else:
                slug = str(create_response)

            # Remove surrounding quotes if present
            slug = slug.strip('"')

            # Step 2: If we have additional fields, update the recipe
            has_updates = any([
                description, recipe_yield, total_time, prep_time, cook_time,
                ingredients, instructions, tags, categories
            ])

            if has_updates:
                # Get the created recipe to get its full structure
                recipe = client.get(f"/api/recipes/{slug}")

                # Build update payload
                update_payload = {
                    "id": recipe.get("id"),
                    "userId": recipe.get("userId"),
                    "householdId": recipe.get("householdId"),
                    "groupId": recipe.get("groupId"),
                    "name": name,
                    "slug": slug,
                }

                if description:
                    update_payload["description"] = description
                if recipe_yield:
                    update_payload["recipeYield"] = recipe_yield
                if total_time:
                    update_payload["totalTime"] = total_time
                if prep_time:
                    update_payload["prepTime"] = prep_time
                if cook_time:
                    update_payload["cookTime"] = cook_time

                # Convert simple ingredient strings to Mealie format
                if ingredients:
                    update_payload["recipeIngredient"] = [
                        {"note": ing, "display": ing} for ing in ingredients
                    ]

                # Convert simple instruction strings to Mealie format
                if instructions:
                    update_payload["recipeInstructions"] = [
                        {"text": inst} for inst in instructions
                    ]

                # Handle tags - include groupId for proper tag creation
                group_id = recipe.get("groupId")
                if tags:
                    update_payload["tags"] = [
                        {"name": tag, "slug": _slugify(tag), "groupId": group_id}
                        for tag in tags
                    ]

                # Handle categories - include groupId for proper category creation
                if categories:
                    update_payload["recipeCategory"] = [
                        {"name": cat, "slug": _slugify(cat), "groupId": group_id}
                        for cat in categories
                    ]

                # Update the recipe
                client.put(f"/api/recipes/{slug}", json=update_payload)

            # Get the final recipe to return
            final_recipe = client.get(f"/api/recipes/{slug}")

            result = {
                "success": True,
                "message": f"Recipe '{name}' created",
                "recipe": {
                    "name": final_recipe.get("name"),
                    "slug": final_recipe.get("slug"),
                    "id": final_recipe.get("id"),
                    "description": final_recipe.get("description"),
                }
            }
            return json.dumps(result, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def recipes_create_from_url(url: str, include_tags: bool = False) -> str:
    """Import a recipe from a URL by scraping it.

    Args:
        url: URL of the recipe to import
        include_tags: Whether to include tags from the scraped recipe (default False)

    Returns:
        JSON string with imported recipe details
    """
    try:
        with MealieClient() as client:
            # Scrape the recipe from URL
            response = client.post(
                "/api/recipes/create/url",
                json={"url": url, "includeTags": include_tags}
            )

            # The response should be a string (the slug)
            if isinstance(response, str):
                slug = response.strip('"')
            elif isinstance(response, dict):
                slug = response.get("slug") or response.get("id", "")
            else:
                slug = str(response).strip('"')

            # Get the created recipe
            recipe = client.get(f"/api/recipes/{slug}")

            result = {
                "success": True,
                "message": f"Recipe imported from URL",
                "recipe": {
                    "name": recipe.get("name"),
                    "slug": recipe.get("slug"),
                    "id": recipe.get("id"),
                    "description": recipe.get("description"),
                    "orgURL": recipe.get("orgURL"),
                }
            }
            return json.dumps(result, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def recipes_update(
    slug: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    recipe_yield: Optional[str] = None,
    total_time: Optional[str] = None,
    prep_time: Optional[str] = None,
    cook_time: Optional[str] = None,
    ingredients: Optional[list[str]] = None,
    instructions: Optional[list[str]] = None,
    tags: Optional[list[str]] = None,
    categories: Optional[list[str]] = None,
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

    Returns:
        JSON string with updated recipe details
    """
    try:
        with MealieClient() as client:
            # Get existing recipe
            recipe = client.get(f"/api/recipes/{slug}")

            # Build update payload preserving existing values
            update_payload = {
                "id": recipe.get("id"),
                "userId": recipe.get("userId"),
                "householdId": recipe.get("householdId"),
                "groupId": recipe.get("groupId"),
                "name": name if name is not None else recipe.get("name"),
                "slug": recipe.get("slug"),
                "description": description if description is not None else recipe.get("description"),
                "recipeYield": recipe_yield if recipe_yield is not None else recipe.get("recipeYield"),
                "totalTime": total_time if total_time is not None else recipe.get("totalTime"),
                "prepTime": prep_time if prep_time is not None else recipe.get("prepTime"),
                "cookTime": cook_time if cook_time is not None else recipe.get("cookTime"),
            }

            # Handle ingredients - replace if provided, keep existing otherwise
            if ingredients is not None:
                update_payload["recipeIngredient"] = [
                    {"note": ing, "display": ing} for ing in ingredients
                ]
            else:
                update_payload["recipeIngredient"] = recipe.get("recipeIngredient", [])

            # Handle instructions - replace if provided, keep existing otherwise
            if instructions is not None:
                update_payload["recipeInstructions"] = [
                    {"text": inst} for inst in instructions
                ]
            else:
                update_payload["recipeInstructions"] = recipe.get("recipeInstructions", [])

            # Handle tags - include groupId for proper tag creation
            group_id = recipe.get("groupId")
            if tags is not None:
                update_payload["tags"] = [
                    {"name": tag, "slug": _slugify(tag), "groupId": group_id}
                    for tag in tags
                ]
            else:
                update_payload["tags"] = recipe.get("tags", [])

            # Handle categories - include groupId for proper category creation
            if categories is not None:
                update_payload["recipeCategory"] = [
                    {"name": cat, "slug": _slugify(cat), "groupId": group_id}
                    for cat in categories
                ]
            else:
                update_payload["recipeCategory"] = recipe.get("recipeCategory", [])

            # Update the recipe
            client.put(f"/api/recipes/{slug}", json=update_payload)

            # Get the updated recipe
            updated_recipe = client.get(f"/api/recipes/{slug}")

            result = {
                "success": True,
                "message": f"Recipe '{updated_recipe.get('name')}' updated",
                "recipe": {
                    "name": updated_recipe.get("name"),
                    "slug": updated_recipe.get("slug"),
                    "id": updated_recipe.get("id"),
                    "description": updated_recipe.get("description"),
                }
            }
            return json.dumps(result, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def recipes_update_structured_ingredients(
    slug: str,
    parsed_ingredients: list[dict]
) -> str:
    """Update a recipe with structured ingredients from parser output.

    This tool accepts the output from mealie_parser_ingredients_batch and updates
    a recipe with fully structured ingredients including quantity, unit, and food.

    Args:
        slug: The recipe's slug identifier
        parsed_ingredients: List of parsed ingredient dicts from parser tools.
            Each dict should have an 'ingredient' field with structured data.

    Returns:
        JSON string with updated recipe details

    Example:
        # First parse ingredients
        parsed = mealie_parser_ingredients_batch(["2 cups flour", "1 tsp salt"])

        # Then update recipe with parsed data
        mealie_recipes_update_structured_ingredients(
            slug="my-recipe",
            parsed_ingredients=parsed['parsed_ingredients']
        )
    """
    try:
        with MealieClient() as client:
            # Convert parser output format to Mealie ingredient format
            mealie_ingredients = []

            for parsed in parsed_ingredients:
                # Parser output has structure: {input, confidence, ingredient}
                # We need the 'ingredient' field
                if isinstance(parsed, dict) and "ingredient" in parsed:
                    ingredient_data = parsed["ingredient"]
                else:
                    # If it's already in the right format, use as-is
                    ingredient_data = parsed

                # Build the ingredient dict for Mealie
                mealie_ingredient = {}

                # Add quantity
                if "quantity" in ingredient_data:
                    mealie_ingredient["quantity"] = ingredient_data["quantity"]

                # Add unit - can be dict or string
                # Clean unit dict to only include writable fields
                if "unit" in ingredient_data and ingredient_data["unit"]:
                    unit = ingredient_data["unit"]
                    if isinstance(unit, dict):
                        # Only include writable fields, exclude read-only timestamps
                        clean_unit = {
                            "id": unit.get("id"),
                            "name": unit.get("name"),
                            "description": unit.get("description", ""),
                            "fraction": unit.get("fraction", True),
                            "abbreviation": unit.get("abbreviation", ""),
                            "useAbbreviation": unit.get("useAbbreviation", False),
                        }
                        # Optional fields
                        if "pluralName" in unit and unit["pluralName"]:
                            clean_unit["pluralName"] = unit["pluralName"]
                        if "pluralAbbreviation" in unit and unit["pluralAbbreviation"]:
                            clean_unit["pluralAbbreviation"] = unit["pluralAbbreviation"]
                        if "aliases" in unit and unit["aliases"]:
                            clean_unit["aliases"] = unit["aliases"]
                        mealie_ingredient["unit"] = clean_unit
                    elif unit:
                        # If it's just a string, create a dict with name
                        mealie_ingredient["unit"] = {"name": str(unit)}

                # Add food - can be dict or string
                # Clean food dict to only include writable fields
                if "food" in ingredient_data and ingredient_data["food"]:
                    food = ingredient_data["food"]
                    if isinstance(food, dict):
                        # Only include writable fields, exclude read-only timestamps
                        clean_food = {
                            "id": food.get("id"),
                            "name": food.get("name"),
                            "description": food.get("description", ""),
                        }
                        # Optional fields
                        if "pluralName" in food and food["pluralName"]:
                            clean_food["pluralName"] = food["pluralName"]
                        if "labelId" in food and food["labelId"]:
                            clean_food["labelId"] = food["labelId"]
                        if "aliases" in food and food["aliases"]:
                            clean_food["aliases"] = food["aliases"]
                        if "householdsWithIngredientFood" in food and food["householdsWithIngredientFood"]:
                            clean_food["householdsWithIngredientFood"] = food["householdsWithIngredientFood"]
                        mealie_ingredient["food"] = clean_food
                    elif food:
                        # If it's just a string, create a dict with name
                        mealie_ingredient["food"] = {"name": str(food)}

                # Add note
                if "note" in ingredient_data and ingredient_data["note"]:
                    mealie_ingredient["note"] = ingredient_data["note"]

                # Add display (required for human-readable format)
                if "display" in ingredient_data:
                    mealie_ingredient["display"] = ingredient_data["display"]
                else:
                    # Construct display from parsed data if not provided
                    parts = []
                    if "quantity" in mealie_ingredient:
                        parts.append(str(mealie_ingredient["quantity"]))
                    if "unit" in mealie_ingredient:
                        unit_name = mealie_ingredient["unit"].get("name", "") if isinstance(mealie_ingredient["unit"], dict) else str(mealie_ingredient["unit"])
                        if unit_name:
                            parts.append(unit_name)
                    if "food" in mealie_ingredient:
                        food_name = mealie_ingredient["food"].get("name", "") if isinstance(mealie_ingredient["food"], dict) else str(mealie_ingredient["food"])
                        if food_name:
                            parts.append(food_name)
                    if "note" in mealie_ingredient:
                        parts.append(f"({mealie_ingredient['note']})")
                    mealie_ingredient["display"] = " ".join(parts)

                # Add referenceId (REQUIRED field)
                if "referenceId" in ingredient_data:
                    mealie_ingredient["referenceId"] = ingredient_data["referenceId"]
                else:
                    # Generate a new UUID if not provided
                    import uuid
                    mealie_ingredient["referenceId"] = str(uuid.uuid4())

                mealie_ingredients.append(mealie_ingredient)

            # Update the recipe with structured ingredients
            updated_recipe = client.update_recipe_ingredients(slug, mealie_ingredients)

            result = {
                "success": True,
                "message": f"Recipe '{updated_recipe.get('name', slug)}' updated with {len(mealie_ingredients)} structured ingredients",
                "recipe": {
                    "name": updated_recipe.get("name"),
                    "slug": updated_recipe.get("slug"),
                    "id": updated_recipe.get("id"),
                    "ingredient_count": len(mealie_ingredients),
                }
            }
            return json.dumps(result, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


def recipes_delete(slug: str) -> str:
    """Delete a recipe from Mealie.

    Args:
        slug: The recipe's slug identifier

    Returns:
        JSON string confirming deletion
    """
    try:
        with MealieClient() as client:
            # Get recipe name before deleting for the message
            try:
                recipe = client.get(f"/api/recipes/{slug}")
                recipe_name = recipe.get("name", slug)
            except Exception:
                recipe_name = slug

            # Delete the recipe
            client.delete(f"/api/recipes/{slug}")

            result = {
                "success": True,
                "message": f"Recipe '{recipe_name}' deleted"
            }
            return json.dumps(result, indent=2)

    except MealieAPIError as e:
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)


if __name__ == "__main__":
    """
    Test the recipe tools against the live Mealie instance.
    """
    from dotenv import load_dotenv

    print("Testing Mealie Recipe Tools...")
    print("=" * 60)

    # Load environment variables
    load_dotenv()

    # Test 1: Search for recipes (no filters)
    print("\n1. Testing recipes_search with no parameters...")
    print("-" * 60)
    search_result = recipes_search(limit=5)
    print(search_result)

    # Extract a slug from search results for next test
    search_data = json.loads(search_result)
    test_slug = None
    if "recipes" in search_data and len(search_data["recipes"]) > 0:
        test_slug = search_data["recipes"][0].get("slug")
        print(f"\nFound test slug: {test_slug}")

    # Test 2: Get a specific recipe
    if test_slug:
        print("\n2. Testing recipes_get with slug:", test_slug)
        print("-" * 60)
        get_result = recipes_get(test_slug)
        print(get_result)
    else:
        print("\n2. Skipping recipes_get test (no slug found)")

    # Test 3: List recipes with pagination
    print("\n3. Testing recipes_list with pagination...")
    print("-" * 60)
    list_result = recipes_list(page=1, per_page=3)
    print(list_result)

    print("\n" + "=" * 60)
    print("All tests completed!")
