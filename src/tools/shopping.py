"""
Shopping List tools for Mealie MCP server.

Provides tools for managing shopping lists - creating lists, adding items,
checking items off, and generating lists from meal plans.
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


def shopping_lists_list() -> str:
    """List all shopping lists.

    Returns:
        JSON string with list of shopping lists and their metadata
    """
    try:
        with MealieClient() as client:
            response = client.get("/api/households/shopping/lists")

            # Handle paginated response
            shopping_lists = []
            if response:
                if isinstance(response, dict) and "items" in response:
                    shopping_lists = response["items"]
                elif isinstance(response, list):
                    shopping_lists = response
                else:
                    shopping_lists = [response]

            # Format output
            lists = []
            for sl in shopping_lists:
                items = sl.get("listItems", [])
                checked_count = sum(1 for item in items if item.get("checked", False))

                lists.append({
                    "id": sl.get("id"),
                    "name": sl.get("name"),
                    "created_at": sl.get("createdAt"),
                    "updated_at": sl.get("updateAt"),
                    "total_items": len(items),
                    "checked_items": checked_count,
                    "unchecked_items": len(items) - checked_count,
                })

            return json.dumps({
                "count": len(lists),
                "lists": lists
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def shopping_lists_get(list_id: str) -> str:
    """Get a specific shopping list with all items.

    Args:
        list_id: The shopping list ID

    Returns:
        JSON string with shopping list details and items
    """
    try:
        with MealieClient() as client:
            response = client.get(f"/api/households/shopping/lists/{list_id}")

            if not response:
                return json.dumps({
                    "error": f"Shopping list '{list_id}' not found"
                }, indent=2)

            # Format items
            items = response.get("listItems", [])
            formatted_items = []

            for item in items:
                unit = item.get("unit")
                food = item.get("food")

                formatted_items.append({
                    "id": item.get("id"),
                    "checked": item.get("checked", False),
                    "quantity": item.get("quantity"),
                    "unit": unit.get("name") if isinstance(unit, dict) else unit,
                    "food": food.get("name") if isinstance(food, dict) else food,
                    "note": item.get("note"),
                    "display": item.get("display"),
                })

            return json.dumps({
                "id": response.get("id"),
                "name": response.get("name"),
                "created_at": response.get("createdAt"),
                "updated_at": response.get("updateAt"),
                "items": formatted_items,
                "total_items": len(formatted_items),
                "checked_count": sum(1 for i in formatted_items if i["checked"]),
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def shopping_lists_create(name: str) -> str:
    """Create a new shopping list.

    Args:
        name: Name for the new shopping list

    Returns:
        JSON string with created shopping list details
    """
    try:
        with MealieClient() as client:
            response = client.post("/api/households/shopping/lists", json={
                "name": name
            })

            return json.dumps({
                "success": True,
                "message": f"Shopping list '{name}' created",
                "list": {
                    "id": response.get("id"),
                    "name": response.get("name"),
                    "created_at": response.get("createdAt"),
                }
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def shopping_lists_delete(list_id: str) -> str:
    """Delete a shopping list.

    Args:
        list_id: The shopping list ID to delete

    Returns:
        JSON string confirming deletion
    """
    try:
        with MealieClient() as client:
            client.delete(f"/api/households/shopping/lists/{list_id}")

            return json.dumps({
                "success": True,
                "message": f"Shopping list '{list_id}' deleted"
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def shopping_items_add(
    list_id: str,
    note: Optional[str] = None,
    quantity: Optional[float] = None,
    unit_id: Optional[str] = None,
    food_id: Optional[str] = None,
    display: Optional[str] = None
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
    try:
        with MealieClient() as client:
            payload = {
                "shoppingListId": list_id,
            }

            if note:
                payload["note"] = note
            if quantity is not None:
                payload["quantity"] = quantity
            if unit_id:
                payload["unitId"] = unit_id
            if food_id:
                payload["foodId"] = food_id
            if display:
                payload["display"] = display

            response = client.post("/api/households/shopping/items", json=payload)

            return json.dumps({
                "success": True,
                "message": "Item added to shopping list",
                "item": response
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def shopping_items_add_bulk(
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
    try:
        with MealieClient() as client:
            added_count = 0
            errors = []

            for item_text in items:
                try:
                    payload = {
                        "shoppingListId": list_id,
                        "note": item_text,
                    }
                    client.post("/api/households/shopping/items", json=payload)
                    added_count += 1
                except Exception as e:
                    errors.append({"item": item_text, "error": str(e)})

            result = {
                "success": True,
                "message": f"Added {added_count} of {len(items)} items",
                "added_count": added_count,
                "total_requested": len(items),
            }

            if errors:
                result["errors"] = errors

            return json.dumps(result, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def shopping_items_check(
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
    try:
        with MealieClient() as client:
            # First get the item to get its current data
            # The shopping item endpoint requires the full object for update
            response = client.put(f"/api/households/shopping/items/{item_id}", json={
                "id": item_id,
                "checked": checked,
            })

            status = "checked" if checked else "unchecked"
            return json.dumps({
                "success": True,
                "message": f"Item '{item_id}' marked as {status}",
                "item": response
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def shopping_items_delete(item_id: str) -> str:
    """Remove an item from a shopping list.

    Args:
        item_id: The shopping list item ID to remove

    Returns:
        JSON string confirming deletion
    """
    try:
        with MealieClient() as client:
            client.delete(f"/api/households/shopping/items/{item_id}")

            return json.dumps({
                "success": True,
                "message": f"Item '{item_id}' removed from shopping list"
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def shopping_items_add_recipe(
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
        JSON string with count of added items
    """
    try:
        with MealieClient() as client:
            # Add recipe ingredients to shopping list
            # The endpoint expects recipeId in the body
            payload = {
                "recipeId": recipe_id,
            }

            # Add scale if not 1.0
            if scale != 1.0:
                payload["recipeIncrementQuantity"] = scale

            response = client.post(
                f"/api/households/shopping/lists/{list_id}/recipe/{recipe_id}",
                json=payload
            )

            return json.dumps({
                "success": True,
                "message": f"Recipe ingredients added to shopping list",
                "list": response
            }, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def shopping_generate_from_mealplan(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    list_name: Optional[str] = None
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
    try:
        with MealieClient() as client:
            # Default to current week if no dates provided
            if not start_date:
                start = date.today()
            else:
                start = date.fromisoformat(start_date)

            if not end_date:
                end = start + timedelta(days=6)
            else:
                end = date.fromisoformat(end_date)

            # Get meal plans for the date range
            mealplan_response = client.get("/api/households/mealplans", params={
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            })

            if not mealplan_response:
                return json.dumps({
                    "error": "No meal plans found for the specified date range",
                    "start_date": start.isoformat(),
                    "end_date": end.isoformat(),
                }, indent=2)

            # Handle paginated response
            mealplan_entries = []
            if isinstance(mealplan_response, dict) and "items" in mealplan_response:
                mealplan_entries = mealplan_response["items"]
            elif isinstance(mealplan_response, list):
                mealplan_entries = mealplan_response
            else:
                mealplan_entries = [mealplan_response]

            if not mealplan_entries:
                return json.dumps({
                    "error": "No meal plans found for the specified date range",
                    "start_date": start.isoformat(),
                    "end_date": end.isoformat(),
                }, indent=2)

            # Collect all recipe IDs
            recipe_ids = []
            for entry in mealplan_entries:
                recipe_id = entry.get("recipeId")
                if recipe_id:
                    recipe_ids.append(recipe_id)

            if not recipe_ids:
                return json.dumps({
                    "error": "No recipes found in meal plan for the specified date range",
                    "start_date": start.isoformat(),
                    "end_date": end.isoformat(),
                }, indent=2)

            # Create the shopping list
            if not list_name:
                list_name = f"Meal Plan - {start.strftime('%b %d')} to {end.strftime('%b %d')}"

            create_response = client.post("/api/households/shopping/lists", json={
                "name": list_name
            })

            if not create_response or "id" not in create_response:
                return json.dumps({
                    "error": "Failed to create shopping list"
                }, indent=2)

            list_id = create_response["id"]

            # Add each recipe's ingredients to the list
            recipes_added = []
            recipes_failed = []

            for recipe_id in recipe_ids:
                try:
                    client.post(
                        f"/api/households/shopping/lists/{list_id}/recipe/{recipe_id}",
                        json={"recipeId": recipe_id}
                    )
                    recipes_added.append(recipe_id)
                except Exception as e:
                    recipes_failed.append({"recipe_id": recipe_id, "error": str(e)})

            # Get the final list with all items
            final_list = client.get(f"/api/households/shopping/lists/{list_id}")
            item_count = len(final_list.get("listItems", [])) if final_list else 0

            result = {
                "success": True,
                "message": f"Shopping list '{list_name}' created with {item_count} items",
                "list_id": list_id,
                "list_name": list_name,
                "date_range": {
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
                "recipes_processed": len(recipes_added),
                "total_items": item_count,
            }

            if recipes_failed:
                result["recipes_failed"] = recipes_failed

            return json.dumps(result, indent=2)

    except MealieAPIError as e:
        return json.dumps({
            "error": str(e),
            "status_code": e.status_code,
            "response_body": e.response_body
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def shopping_lists_clear_checked(list_id: str) -> str:
    """Remove all checked items from a shopping list.

    Args:
        list_id: The shopping list ID

    Returns:
        JSON string with count of removed items
    """
    try:
        with MealieClient() as client:
            # Get the list with all items
            response = client.get(f"/api/households/shopping/lists/{list_id}")

            if not response:
                return json.dumps({
                    "error": f"Shopping list '{list_id}' not found"
                }, indent=2)

            items = response.get("listItems", [])
            checked_items = [item for item in items if item.get("checked", False)]

            if not checked_items:
                return json.dumps({
                    "success": True,
                    "message": "No checked items to remove",
                    "removed_count": 0
                }, indent=2)

            # Delete each checked item
            removed_count = 0
            errors = []

            for item in checked_items:
                item_id = item.get("id")
                if item_id:
                    try:
                        client.delete(f"/api/households/shopping/items/{item_id}")
                        removed_count += 1
                    except Exception as e:
                        errors.append({"item_id": item_id, "error": str(e)})

            result = {
                "success": True,
                "message": f"Removed {removed_count} checked items",
                "removed_count": removed_count,
            }

            if errors:
                result["errors"] = errors

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
    Test the shopping list tools against the live Mealie instance.
    """
    from dotenv import load_dotenv

    print("Testing Mealie Shopping List Tools...")
    print("=" * 60)

    # Load environment variables
    load_dotenv()

    # Test 1: List all shopping lists
    print("\n1. Testing shopping_lists_list...")
    print("-" * 60)
    result = shopping_lists_list()
    print(result)

    # Parse to get a list ID for further tests
    lists_data = json.loads(result)
    test_list_id = None
    if "lists" in lists_data and len(lists_data["lists"]) > 0:
        test_list_id = lists_data["lists"][0]["id"]
        print(f"\nFound test list ID: {test_list_id}")

    # Test 2: Get specific shopping list
    if test_list_id:
        print("\n2. Testing shopping_lists_get...")
        print("-" * 60)
        result = shopping_lists_get(test_list_id)
        print(result)
    else:
        print("\n2. Skipping shopping_lists_get (no list found)")

    # Test 3: Create a new list (will clean up after)
    print("\n3. Testing shopping_lists_create...")
    print("-" * 60)
    result = shopping_lists_create("Test List - Can Delete")
    print(result)

    # Parse to get the new list ID
    create_data = json.loads(result)
    new_list_id = None
    if "list" in create_data and "id" in create_data["list"]:
        new_list_id = create_data["list"]["id"]
        print(f"\nCreated test list ID: {new_list_id}")

    # Test 4: Add item to the new list
    if new_list_id:
        print("\n4. Testing shopping_items_add...")
        print("-" * 60)
        result = shopping_items_add(new_list_id, note="Test item - milk")
        print(result)

    # Test 5: Delete the test list
    if new_list_id:
        print("\n5. Testing shopping_lists_delete...")
        print("-" * 60)
        result = shopping_lists_delete(new_list_id)
        print(result)

    print("\n" + "=" * 60)
    print("All tests completed!")
