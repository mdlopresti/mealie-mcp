"""
Recipe tools for Mealie MCP server.

Provides tools for searching, retrieving, and listing recipes from a Mealie instance.
"""

import json
import sys
from pathlib import Path
from typing import Optional

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
