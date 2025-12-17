"""
Meal Plan tools for Mealie MCP server.

Provides tools for managing meal plans - listing, creating, updating, and deleting
meal plan entries, plus generation helpers.
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

# Handle imports for both module usage and standalone execution
try:
    from ..client import MealieClient, MealieAPIError
except ImportError:
    # Add parent directory to path for standalone execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from client import MealieClient, MealieAPIError


def mealplans_list(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """List meal plans for a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format (defaults to today)
        end_date: End date in YYYY-MM-DD format (defaults to 7 days from start)

    Returns:
        JSON string with list of meal plan entries
    """
    try:
        with MealieClient() as client:
            # Default to current week if no dates provided
            if not start_date:
                start = date.today()
            else:
                start = date.fromisoformat(start_date)

            if not end_date:
                end = start + timedelta(days=7)
            else:
                end = date.fromisoformat(end_date)

            params = {
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            }

            response = client.get("/api/households/mealplans", params=params)

            # Format response
            if isinstance(response, list):
                entries = []
                for entry in response:
                    recipe = entry.get("recipe")
                    entries.append({
                        "id": entry.get("id"),
                        "date": entry.get("date"),
                        "entry_type": entry.get("entryType"),
                        "title": entry.get("title"),
                        "text": entry.get("text"),
                        "recipe_id": entry.get("recipeId"),
                        "recipe_name": recipe.get("name") if isinstance(recipe, dict) else None,
                        "recipe_slug": recipe.get("slug") if isinstance(recipe, dict) else None,
                    })

                result = {
                    "start_date": start.isoformat(),
                    "end_date": end.isoformat(),
                    "count": len(entries),
                    "entries": entries
                }
                return json.dumps(result, indent=2)

            return json.dumps(response, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def mealplans_today() -> str:
    """Get today's meal plan entries.

    Returns:
        JSON string with today's meals organized by entry type
    """
    try:
        with MealieClient() as client:
            response = client.get("/api/households/mealplans/today")

            if not response:
                return json.dumps({
                    "date": date.today().isoformat(),
                    "count": 0,
                    "meals": {}
                }, indent=2)

            # Ensure response is a list
            if not isinstance(response, list):
                response = [response]

            # Organize by entry type
            meals_by_type = {}
            for entry in response:
                entry_type = entry.get("entryType", "meal").lower()
                if entry_type not in meals_by_type:
                    meals_by_type[entry_type] = []

                recipe = entry.get("recipe")
                meals_by_type[entry_type].append({
                    "id": entry.get("id"),
                    "title": entry.get("title"),
                    "text": entry.get("text"),
                    "recipe_id": entry.get("recipeId"),
                    "recipe_name": recipe.get("name") if isinstance(recipe, dict) else None,
                    "recipe_slug": recipe.get("slug") if isinstance(recipe, dict) else None,
                })

            result = {
                "date": date.today().isoformat(),
                "count": len(response),
                "meals": meals_by_type
            }
            return json.dumps(result, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def mealplans_get(mealplan_id: str) -> str:
    """Get a specific meal plan entry by ID.

    Args:
        mealplan_id: The meal plan entry ID

    Returns:
        JSON string with meal plan entry details
    """
    try:
        with MealieClient() as client:
            response = client.get(f"/api/households/mealplans/{mealplan_id}")
            return json.dumps(response, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def mealplans_create(
    meal_date: str,
    entry_type: str,
    recipe_id: Optional[str] = None,
    title: Optional[str] = None,
    text: Optional[str] = None
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
    try:
        # Validate entry type
        valid_types = ["breakfast", "lunch", "dinner", "side", "snack"]
        if entry_type.lower() not in valid_types:
            return json.dumps({
                "error": f"Invalid entry_type '{entry_type}'. Must be one of: {', '.join(valid_types)}"
            }, indent=2)

        with MealieClient() as client:
            payload = {
                "date": meal_date,
                "entryType": entry_type.lower(),
            }

            if recipe_id:
                payload["recipeId"] = recipe_id

            if title:
                payload["title"] = title

            if text:
                payload["text"] = text

            response = client.post("/api/households/mealplans", json=payload)

            return json.dumps({
                "success": True,
                "message": f"Meal plan entry created for {meal_date}",
                "entry": response
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def mealplans_update(
    mealplan_id: str,
    meal_date: Optional[str] = None,
    entry_type: Optional[str] = None,
    recipe_id: Optional[str] = None,
    title: Optional[str] = None,
    text: Optional[str] = None
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
    try:
        # Validate entry type if provided
        if entry_type:
            valid_types = ["breakfast", "lunch", "dinner", "side", "snack"]
            if entry_type.lower() not in valid_types:
                return json.dumps({
                    "error": f"Invalid entry_type '{entry_type}'. Must be one of: {', '.join(valid_types)}"
                }, indent=2)

        with MealieClient() as client:
            # First get the existing entry
            existing = client.get(f"/api/households/mealplans/{mealplan_id}")

            if not existing:
                return json.dumps({
                    "error": f"Meal plan entry '{mealplan_id}' not found"
                }, indent=2)

            # Build update payload
            payload = {
                "id": mealplan_id,
                "date": meal_date or existing.get("date"),
                "entryType": (entry_type.lower() if entry_type else existing.get("entryType")),
            }

            # Handle optional fields
            if recipe_id is not None:
                payload["recipeId"] = recipe_id
            elif "recipeId" in existing:
                payload["recipeId"] = existing["recipeId"]

            if title is not None:
                payload["title"] = title
            elif "title" in existing:
                payload["title"] = existing["title"]

            if text is not None:
                payload["text"] = text
            elif "text" in existing:
                payload["text"] = existing["text"]

            response = client.put(f"/api/households/mealplans/{mealplan_id}", json=payload)

            return json.dumps({
                "success": True,
                "message": f"Meal plan entry '{mealplan_id}' updated",
                "entry": response
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def mealplans_delete(mealplan_id: str) -> str:
    """Delete a meal plan entry.

    Args:
        mealplan_id: The meal plan entry ID to delete

    Returns:
        JSON string confirming deletion
    """
    try:
        with MealieClient() as client:
            client.delete(f"/api/households/mealplans/{mealplan_id}")

            return json.dumps({
                "success": True,
                "message": f"Meal plan entry '{mealplan_id}' deleted"
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def mealplans_random(
    entry_type: Optional[str] = None
) -> str:
    """Get a random meal suggestion from Mealie.

    Args:
        entry_type: Optional meal type filter - breakfast, lunch, dinner, side, or snack

    Returns:
        JSON string with suggested recipe
    """
    try:
        with MealieClient() as client:
            # Use random endpoint
            response = client.post("/api/households/mealplans/random", json={})

            if not response:
                return json.dumps({
                    "error": "No random meal suggestion available"
                }, indent=2)

            # Extract relevant info
            recipe = response.get("recipe") if isinstance(response, dict) else response
            if isinstance(recipe, dict):
                return json.dumps({
                    "success": True,
                    "suggestion": {
                        "recipe_id": recipe.get("id"),
                        "name": recipe.get("name"),
                        "slug": recipe.get("slug"),
                        "description": recipe.get("description"),
                        "total_time": recipe.get("totalTime"),
                        "tags": [tag.get("name") for tag in recipe.get("tags", [])],
                    }
                }, indent=2)

            return json.dumps({
                "success": True,
                "suggestion": response
            }, indent=2)

    except MealieAPIError as e:
        # If random endpoint doesn't exist, fall back to getting a random recipe
        try:
            with MealieClient() as client:
                # Get recipes and pick one
                import random
                response = client.get("/api/recipes", params={"perPage": 100, "page": 1})

                if isinstance(response, dict) and "items" in response:
                    recipes = response["items"]
                    if recipes:
                        recipe = random.choice(recipes)
                        return json.dumps({
                            "success": True,
                            "suggestion": {
                                "recipe_id": recipe.get("id"),
                                "name": recipe.get("name"),
                                "slug": recipe.get("slug"),
                                "description": recipe.get("description"),
                                "total_time": recipe.get("totalTime"),
                                "tags": [tag.get("name") for tag in recipe.get("tags", [])],
                            }
                        }, indent=2)

                return json.dumps({
                    "error": "No recipes available for suggestion"
                }, indent=2)

        except Exception as fallback_error:
            return json.dumps({
                "error": str(e),
                "status_code": e.status_code,
                "response_body": e.response_body
            }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def mealplans_get_by_date(meal_date: str) -> str:
    """Get all meal plan entries for a specific date.

    Args:
        meal_date: Date in YYYY-MM-DD format

    Returns:
        JSON string with all meals for that date
    """
    try:
        with MealieClient() as client:
            params = {
                "start_date": meal_date,
                "end_date": meal_date,
            }

            response = client.get("/api/households/mealplans", params=params)

            if not response:
                return json.dumps({
                    "date": meal_date,
                    "count": 0,
                    "meals": {}
                }, indent=2)

            # Ensure response is a list
            if not isinstance(response, list):
                response = [response]

            # Organize by entry type
            meals_by_type = {}
            for entry in response:
                entry_type = entry.get("entryType", "meal").lower()
                if entry_type not in meals_by_type:
                    meals_by_type[entry_type] = []

                recipe = entry.get("recipe")
                meals_by_type[entry_type].append({
                    "id": entry.get("id"),
                    "title": entry.get("title"),
                    "text": entry.get("text"),
                    "recipe_id": entry.get("recipeId"),
                    "recipe_name": recipe.get("name") if isinstance(recipe, dict) else None,
                    "recipe_slug": recipe.get("slug") if isinstance(recipe, dict) else None,
                })

            result = {
                "date": meal_date,
                "count": len(response),
                "meals": meals_by_type
            }
            return json.dumps(result, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


if __name__ == "__main__":
    """
    Test the meal plan tools against the live Mealie instance.
    """
    from dotenv import load_dotenv

    print("Testing Mealie Meal Plan Tools...")
    print("=" * 60)

    # Load environment variables
    load_dotenv()

    # Test 1: List meal plans for current week
    print("\n1. Testing mealplans_list (current week)...")
    print("-" * 60)
    result = mealplans_list()
    print(result)

    # Test 2: Get today's meals
    print("\n2. Testing mealplans_today...")
    print("-" * 60)
    result = mealplans_today()
    print(result)

    # Test 3: Get random meal suggestion
    print("\n3. Testing mealplans_random...")
    print("-" * 60)
    result = mealplans_random()
    print(result)

    # Test 4: Get meals for specific date
    print("\n4. Testing mealplans_get_by_date...")
    print("-" * 60)
    result = mealplans_get_by_date(date.today().isoformat())
    print(result)

    print("\n" + "=" * 60)
    print("All tests completed!")
