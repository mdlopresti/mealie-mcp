"""
Recipe tools for Mealie MCP server.

Provides tools for searching, retrieving, and listing recipes from a Mealie instance.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Optional


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
    org_url: Optional[str] = None,
    image: Optional[str] = None,
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
        tags: New list of tag names (ADDITIVE - adds to existing tags)
        categories: New list of category names (ADDITIVE - adds to existing categories)
        org_url: Original recipe URL
        image: Recipe image identifier

    Returns:
        JSON string with updated recipe details
    """
    try:
        with MealieClient() as client:
            # Get existing recipe
            recipe = client.get(f"/api/recipes/{slug}")

            # Build update payload preserving existing values
            # CRITICAL: We must include ALL required fields for PUT to work
            update_payload = {
                "id": recipe.get("id"),
                "userId": recipe.get("userId"),
                "householdId": recipe.get("householdId"),
                "groupId": recipe.get("groupId"),
                "name": name if name is not None else recipe.get("name"),
                "slug": slug,  # Always use the provided slug, not recipe.get("slug")
                "description": description if description is not None else recipe.get("description"),
                "recipeYield": recipe_yield if recipe_yield is not None else recipe.get("recipeYield"),
                "totalTime": total_time if total_time is not None else recipe.get("totalTime"),
                "prepTime": prep_time if prep_time is not None else recipe.get("prepTime"),
                "cookTime": cook_time if cook_time is not None else recipe.get("cookTime"),
                "orgURL": org_url if org_url is not None else recipe.get("orgURL"),
                "image": image if image is not None else recipe.get("image"),
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

            # Handle tags - ADDITIVE behavior (add to existing tags)
            group_id = recipe.get("groupId")
            existing_tags = recipe.get("tags", [])

            if tags is not None:
                # Get existing tag names
                existing_tag_names = {tag.get("name") for tag in existing_tags if isinstance(tag, dict)}

                # Create tag objects for new tags
                new_tag_objects = []
                for tag in tags:
                    if tag not in existing_tag_names:
                        new_tag_objects.append({
                            "name": tag,
                            "slug": _slugify(tag),
                            "groupId": group_id
                        })

                # Combine existing and new tags
                update_payload["tags"] = existing_tags + new_tag_objects
            else:
                update_payload["tags"] = existing_tags

            # Handle categories - ADDITIVE behavior (add to existing categories)
            existing_categories = recipe.get("recipeCategory", [])

            if categories is not None:
                # Get existing category names
                existing_cat_names = {cat.get("name") for cat in existing_categories if isinstance(cat, dict)}

                # Create category objects for new categories
                new_cat_objects = []
                for cat in categories:
                    if cat not in existing_cat_names:
                        new_cat_objects.append({
                            "name": cat,
                            "slug": _slugify(cat),
                            "groupId": group_id
                        })

                # Combine existing and new categories
                update_payload["recipeCategory"] = existing_categories + new_cat_objects
            else:
                update_payload["recipeCategory"] = existing_categories

            # Update the recipe
            # Use PATCH for tag/category-only updates with full payload to avoid name validation issues
            if (tags is not None or categories is not None) and all(x is None for x in [name, description, recipe_yield, total_time, prep_time, cook_time, ingredients, instructions, org_url, image]):
                # Only updating tags/categories - use PATCH with full payload
                client.patch(f"/api/recipes/{slug}", json=update_payload)
            else:
                # Updating other fields - use PUT with full payload
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
                    "tags": [tag.get("name") for tag in updated_recipe.get("tags", [])],
                    "categories": [cat.get("name") for cat in updated_recipe.get("recipeCategory", [])],
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
            # v1.4.15: Pre-create any missing foods/units
            # This avoids SQLAlchemy auto_init errors when updating recipes
            created_units = {}  # name -> id mapping
            created_foods = {}  # name -> id mapping

            for parsed in parsed_ingredients:
                if isinstance(parsed, dict) and "ingredient" in parsed:
                    ingredient_data = parsed["ingredient"]
                else:
                    ingredient_data = parsed

                # Check if unit needs to be created
                if "unit" in ingredient_data and ingredient_data["unit"]:
                    unit = ingredient_data["unit"]
                    if isinstance(unit, dict):
                        unit_name = unit.get("name")
                        unit_id = unit.get("id")
                        # If unit has no ID, create it
                        if unit_name and not unit_id and unit_name not in created_units:
                            try:
                                new_unit = client.create_unit(unit_name)
                                created_units[unit_name] = new_unit.get("id")
                                # Update the ingredient data with the new ID
                                ingredient_data["unit"]["id"] = new_unit.get("id")
                            except Exception as e:
                                # If creation fails (maybe it exists but parser didn't find it),
                                # we'll try to send as string and let Mealie handle it
                                pass

                # Check if food needs to be created
                if "food" in ingredient_data and ingredient_data["food"]:
                    food = ingredient_data["food"]
                    if isinstance(food, dict):
                        food_name = food.get("name")
                        food_id = food.get("id")
                        # If food has no ID, create it
                        if food_name and not food_id and food_name not in created_foods:
                            try:
                                new_food = client.create_food(food_name)
                                created_foods[food_name] = new_food.get("id")
                                # Update the ingredient data with the new ID
                                ingredient_data["food"]["id"] = new_food.get("id")
                            except Exception as e:
                                # If creation fails, we'll try to send as string
                                pass

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

                # Add unit - v1.4.15: Send with ID if available (after pre-creation)
                if "unit" in ingredient_data and ingredient_data["unit"]:
                    unit = ingredient_data["unit"]
                    if isinstance(unit, dict):
                        unit_id = unit.get("id")
                        unit_name = unit.get("name")
                        if unit_id:
                            # Send as dict with id and name
                            mealie_ingredient["unit"] = {"id": unit_id, "name": unit_name}
                        elif unit_name:
                            # Fall back to string if no ID
                            mealie_ingredient["unit"] = unit_name
                    elif unit:
                        mealie_ingredient["unit"] = str(unit)

                # Add food - v1.4.15: Send with ID if available (after pre-creation)
                if "food" in ingredient_data and ingredient_data["food"]:
                    food = ingredient_data["food"]
                    if isinstance(food, dict):
                        food_id = food.get("id")
                        food_name = food.get("name")
                        if food_id:
                            # Send as dict with id and name
                            mealie_ingredient["food"] = {"id": food_id, "name": food_name}
                        elif food_name:
                            # Fall back to string if no ID
                            mealie_ingredient["food"] = food_name
                    elif food:
                        mealie_ingredient["food"] = str(food)

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

                # Add fields that Mealie expects (set to null if not provided)
                mealie_ingredient["title"] = ingredient_data.get("title", "")
                mealie_ingredient["originalText"] = ingredient_data.get("originalText")
                mealie_ingredient["referencedRecipe"] = ingredient_data.get("referencedRecipe")

                mealie_ingredients.append(mealie_ingredient)

            # DEBUG: Print ingredients being sent
            import sys
            print(f"\n=== DEBUG: Ingredients being sent to Mealie ===", file=sys.stderr)
            print(f"Count: {len(mealie_ingredients)}", file=sys.stderr)
            for i, ing in enumerate(mealie_ingredients):
                print(f"\nIngredient {i+1}:", file=sys.stderr)
                print(f"  quantity: {ing.get('quantity')}", file=sys.stderr)
                print(f"  unit: {ing.get('unit')}", file=sys.stderr)
                print(f"  food: {ing.get('food')}", file=sys.stderr)
                print(f"  display: {ing.get('display')}", file=sys.stderr)
            print(f"=== END DEBUG ===\n", file=sys.stderr)

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
                },
                "debug_ingredients_sent": mealie_ingredients  # v1.4.13: Include debug info
            }
            return json.dumps(result, indent=2)

    except MealieAPIError as e:
        # v1.4.13: Include ingredients in error for debugging
        error_result = {
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body,
            "debug_ingredients_sent": mealie_ingredients if 'mealie_ingredients' in locals() else []
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


def recipes_duplicate(slug: str, new_name: Optional[str] = None) -> str:
    """Duplicate an existing recipe.

    Args:
        slug: The recipe's slug identifier to duplicate
        new_name: Optional new name for the duplicated recipe (defaults to "Copy of {original_name}")

    Returns:
        JSON string with the newly created recipe data
    """
    try:
        with MealieClient() as client:
            recipe = client.duplicate_recipe(slug, new_name)

            result = {
                "success": True,
                "message": f"Recipe duplicated successfully",
                "recipe": {
                    "name": recipe.get("name"),
                    "slug": recipe.get("slug"),
                    "id": recipe.get("id")
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


def recipes_update_last_made(slug: str, timestamp: Optional[str] = None) -> str:
    """Update the last made timestamp for a recipe.

    Args:
        slug: The recipe's slug identifier
        timestamp: Optional ISO 8601 timestamp (defaults to current time on server)

    Returns:
        JSON string with updated recipe data
    """
    try:
        with MealieClient() as client:
            recipe = client.update_recipe_last_made(slug, timestamp)

            result = {
                "success": True,
                "message": f"Recipe '{recipe.get('name')}' last made timestamp updated",
                "last_made": recipe.get("lastMade")
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


def recipes_create_from_urls_bulk(urls: list[str], include_tags: bool = False) -> str:
    """Import multiple recipes from URLs at once.

    Args:
        urls: List of recipe URLs to import
        include_tags: Whether to include tags from scraped recipes (default False)

    Returns:
        JSON string with import results for each URL
    """
    try:
        with MealieClient() as client:
            results = client.create_recipes_from_urls_bulk(urls, include_tags)

            return json.dumps({
                "success": True,
                "message": f"Bulk import initiated for {len(urls)} URLs",
                "results": results
            }, indent=2)

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


def recipes_bulk_tag(recipe_ids: list[str], tags: list[str]) -> str:
    """Add tags to multiple recipes at once.

    Args:
        recipe_ids: List of recipe IDs to tag
        tags: List of tag names to add

    Returns:
        JSON string with bulk action results
    """
    try:
        with MealieClient() as client:
            results = client.bulk_tag_recipes(recipe_ids, tags)

            return json.dumps({
                "success": True,
                "message": f"Tagged {len(recipe_ids)} recipes with {len(tags)} tag(s)",
                "results": results
            }, indent=2)

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


def recipes_bulk_categorize(recipe_ids: list[str], categories: list[str]) -> str:
    """Add categories to multiple recipes at once.

    Args:
        recipe_ids: List of recipe IDs to categorize
        categories: List of category names to add

    Returns:
        JSON string with bulk action results
    """
    try:
        with MealieClient() as client:
            results = client.bulk_categorize_recipes(recipe_ids, categories)

            return json.dumps({
                "success": True,
                "message": f"Categorized {len(recipe_ids)} recipes with {len(categories)} category(ies)",
                "results": results
            }, indent=2)

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


def recipes_bulk_delete(recipe_ids: list[str]) -> str:
    """Delete multiple recipes at once.

    Args:
        recipe_ids: List of recipe IDs to delete

    Returns:
        JSON string with bulk action results
    """
    try:
        with MealieClient() as client:
            results = client.bulk_delete_recipes(recipe_ids)

            return json.dumps({
                "success": True,
                "message": f"Deleted {len(recipe_ids)} recipe(s)",
                "results": results
            }, indent=2)

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


def recipes_bulk_export(recipe_ids: list[str], export_format: str = "json") -> str:
    """Export multiple recipes at once.

    Args:
        recipe_ids: List of recipe IDs to export
        export_format: Export format (json, zip, etc.)

    Returns:
        JSON string with export data
    """
    try:
        with MealieClient() as client:
            results = client.bulk_export_recipes(recipe_ids, export_format)

            return json.dumps({
                "success": True,
                "message": f"Exported {len(recipe_ids)} recipe(s) as {export_format}",
                "data": results
            }, indent=2)

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


def recipes_bulk_update_settings(recipe_ids: list[str], settings: dict[str, Any]) -> str:
    """Update settings for multiple recipes at once.

    Args:
        recipe_ids: List of recipe IDs to update
        settings: Settings to update (e.g., {"public": true, "show_nutrition": false})

    Returns:
        JSON string with bulk action results
    """
    try:
        with MealieClient() as client:
            results = client.bulk_update_settings(recipe_ids, settings)

            return json.dumps({
                "success": True,
                "message": f"Updated settings for {len(recipe_ids)} recipe(s)",
                "results": results
            }, indent=2)

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


def recipes_create_from_image(image_data: str, extension: str = "jpg") -> str:
    """Create a recipe from an image using AI (experimental).

    Args:
        image_data: Base64 encoded image data
        extension: Image file extension (jpg, png, etc.)

    Returns:
        JSON string with created recipe data
    """
    try:
        with MealieClient() as client:
            recipe = client.create_recipe_from_image(image_data, extension)

            result = {
                "success": True,
                "message": "Recipe created from image successfully",
                "recipe": {
                    "name": recipe.get("name"),
                    "slug": recipe.get("slug"),
                    "id": recipe.get("id")
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


def recipes_upload_image_from_url(slug: str, image_url: str) -> str:
    """Upload an image to an existing recipe from a URL.

    Args:
        slug: Recipe slug
        image_url: URL of the image to download and upload

    Returns:
        JSON string with upload confirmation or error details
    """
    try:
        client = MealieClient()
        result = client.upload_recipe_image_from_url(slug, image_url)
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
