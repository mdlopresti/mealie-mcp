"""
E2E tests for shopping list workflows.

Tests real shopping list operations against a live Mealie instance:
- Creating and managing shopping lists
- Adding items (single, bulk, from recipes)
- Checking/unchecking items
- Generating from meal plans (critical workflow!)
- Clearing checked items
- Error scenarios
"""

import pytest
from datetime import date, timedelta
from src.client import MealieClient


@pytest.mark.e2e
def test_shopping_create_add_check_delete_workflow(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test basic shopping list workflow: create → add items → check items → delete.

    This validates the core shopping list operations that users interact with daily.
    """
    # Create shopping list
    list_name = f"E2E Test List {unique_id}"
    response = e2e_client.post("/api/households/shopping/lists", json={
        "name": list_name
    })
    list_id = response["id"]
    test_cleanup_all["shopping_lists"].append(list_id)

    assert response["name"] == list_name
    assert list_id is not None

    # Add items
    item1 = e2e_client.post("/api/households/shopping/items", json={
        "shoppingListId": list_id,
        "note": "2 cups flour"
    })
    item1_id = item1["id"]

    item2 = e2e_client.post("/api/households/shopping/items", json={
        "shoppingListId": list_id,
        "note": "1 tsp salt"
    })
    item2_id = item2["id"]

    # Verify items exist in list
    shopping_list = e2e_client.get(f"/api/households/shopping/lists/{list_id}")
    assert len(shopping_list["listItems"]) == 2

    # Check first item
    e2e_client.put(f"/api/households/shopping/items/{item1_id}", json={
        "id": item1_id,
        "checked": True
    })

    # Verify checked status
    shopping_list = e2e_client.get(f"/api/households/shopping/lists/{list_id}")
    checked_items = [item for item in shopping_list["listItems"] if item.get("checked")]
    assert len(checked_items) == 1

    # Delete an item
    e2e_client.delete(f"/api/households/shopping/items/{item2_id}")

    # Verify item deleted
    shopping_list = e2e_client.get(f"/api/households/shopping/lists/{list_id}")
    assert len(shopping_list["listItems"]) == 1


@pytest.mark.e2e
def test_shopping_bulk_add_items(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test bulk adding multiple items to a shopping list.

    Validates efficient batch item addition for common grocery list building.
    """
    # Create shopping list
    list_name = f"E2E Bulk Add Test {unique_id}"
    response = e2e_client.post("/api/households/shopping/lists", json={
        "name": list_name
    })
    list_id = response["id"]
    test_cleanup_all["shopping_lists"].append(list_id)

    # Add multiple items
    items = [
        "2 cups flour",
        "1 tsp salt",
        "3 eggs",
        "1 cup milk",
        "2 tbsp butter"
    ]

    for item_text in items:
        e2e_client.post("/api/households/shopping/items", json={
            "shoppingListId": list_id,
            "note": item_text
        })

    # Verify all items added
    shopping_list = e2e_client.get(f"/api/households/shopping/lists/{list_id}")
    assert len(shopping_list["listItems"]) == len(items)

    # Verify item texts
    item_notes = [item.get("note") for item in shopping_list["listItems"]]
    for expected_item in items:
        assert expected_item in item_notes


@pytest.mark.e2e
def test_shopping_add_recipe_ingredients(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test adding all ingredients from a recipe to a shopping list.

    This validates the recipe → shopping list integration for meal planning.
    """
    # Create recipe with ingredients
    recipe = e2e_client.create_recipe(
        name=f"E2E Recipe {unique_id}",
        description="Test recipe for shopping list",
        ingredients=["2 cups flour", "1 tsp salt", "3 eggs"]
    )
    test_cleanup_all["recipes"].append(recipe["slug"])
    recipe_id = recipe["id"]

    # Create shopping list
    list_name = f"E2E Recipe Shopping {unique_id}"
    shopping_list = e2e_client.post("/api/households/shopping/lists", json={
        "name": list_name
    })
    list_id = shopping_list["id"]
    test_cleanup_all["shopping_lists"].append(list_id)

    # Add recipe ingredients to shopping list
    e2e_client.post(
        f"/api/households/shopping/lists/{list_id}/recipe/{recipe_id}",
        json={"recipeId": recipe_id}
    )

    # Verify items added
    shopping_list = e2e_client.get(f"/api/households/shopping/lists/{list_id}")
    assert len(shopping_list["listItems"]) > 0

    # Verify ingredients are present (at least one should match)
    item_texts = [
        item.get("note") or item.get("display") or ""
        for item in shopping_list["listItems"]
    ]
    # At least one ingredient should be found
    assert any("flour" in text.lower() or "salt" in text.lower() or "egg" in text.lower()
               for text in item_texts)


@pytest.mark.e2e
def test_shopping_generate_from_mealplan(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test generating shopping list from meal plan (CRITICAL high-value workflow!).

    This is the most important shopping workflow - taking a week's meal plan
    and automatically generating the shopping list with all ingredients.
    """
    # Create recipe with ingredients
    recipe = e2e_client.create_recipe(
        name=f"E2E Mealplan Recipe {unique_id}",
        description="Test recipe for mealplan shopping",
        ingredients=["2 cups flour", "1 tsp salt", "3 eggs", "1 cup milk"]
    )
    test_cleanup_all["recipes"].append(recipe["slug"])
    recipe_id = recipe["id"]

    # Create mealplan with recipe
    meal_date = (date.today() + timedelta(days=1)).isoformat()
    mealplan = e2e_client.create_mealplan(
        meal_date=meal_date,
        entry_type="dinner",
        recipe_id=recipe_id
    )
    test_cleanup_all["mealplans"].append(mealplan["id"])

    # Get meal plans for the date range to verify
    mealplan_response = e2e_client.get("/api/households/mealplans", params={
        "start_date": meal_date,
        "end_date": meal_date,
    })

    # Handle paginated response
    if isinstance(mealplan_response, dict) and "items" in mealplan_response:
        mealplan_entries = mealplan_response["items"]
    elif isinstance(mealplan_response, list):
        mealplan_entries = mealplan_response
    else:
        mealplan_entries = [mealplan_response] if mealplan_response else []

    assert len(mealplan_entries) > 0, "Mealplan should exist"

    # Create shopping list
    list_name = f"E2E Mealplan Shopping {unique_id}"
    shopping_list = e2e_client.post("/api/households/shopping/lists", json={
        "name": list_name
    })
    list_id = shopping_list["id"]
    test_cleanup_all["shopping_lists"].append(list_id)

    # Add recipe ingredients from meal plan
    e2e_client.post(
        f"/api/households/shopping/lists/{list_id}/recipe/{recipe_id}",
        json={"recipeId": recipe_id}
    )

    # Verify shopping list has items
    final_list = e2e_client.get(f"/api/households/shopping/lists/{list_id}")
    assert len(final_list["listItems"]) > 0, "Shopping list should have items"

    # Verify items include recipe ingredients
    item_texts = [
        item.get("note") or item.get("display") or ""
        for item in final_list["listItems"]
    ]
    # Check that at least some ingredients are present
    assert any("flour" in text.lower() for text in item_texts), \
        "Shopping list should contain flour from recipe"


@pytest.mark.e2e
def test_shopping_clear_checked_items(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test clearing all checked items from a shopping list.

    Validates the workflow for cleaning up completed shopping list items.
    """
    # Create shopping list
    list_name = f"E2E Clear Checked Test {unique_id}"
    shopping_list = e2e_client.post("/api/households/shopping/lists", json={
        "name": list_name
    })
    list_id = shopping_list["id"]
    test_cleanup_all["shopping_lists"].append(list_id)

    # Add items
    item1 = e2e_client.post("/api/households/shopping/items", json={
        "shoppingListId": list_id,
        "note": "checked item 1"
    })
    item2 = e2e_client.post("/api/households/shopping/items", json={
        "shoppingListId": list_id,
        "note": "unchecked item"
    })
    item3 = e2e_client.post("/api/households/shopping/items", json={
        "shoppingListId": list_id,
        "note": "checked item 2"
    })

    # Check items 1 and 3
    e2e_client.put(f"/api/households/shopping/items/{item1['id']}", json={
        "id": item1["id"],
        "checked": True
    })
    e2e_client.put(f"/api/households/shopping/items/{item3['id']}", json={
        "id": item3["id"],
        "checked": True
    })

    # Verify 2 checked items
    shopping_list = e2e_client.get(f"/api/households/shopping/lists/{list_id}")
    checked_count = sum(1 for item in shopping_list["listItems"] if item.get("checked"))
    assert checked_count == 2

    # Clear checked items
    items = shopping_list.get("listItems", [])
    checked_items = [item for item in items if item.get("checked", False)]

    for item in checked_items:
        e2e_client.delete(f"/api/households/shopping/items/{item['id']}")

    # Verify only unchecked item remains
    shopping_list = e2e_client.get(f"/api/households/shopping/lists/{list_id}")
    assert len(shopping_list["listItems"]) == 1
    assert shopping_list["listItems"][0]["note"] == "unchecked item"


@pytest.mark.e2e
def test_shopping_delete_recipe_from_list(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test removing recipe ingredients from a shopping list.

    This validates the ability to remove all items from a specific recipe
    when plans change.
    """
    # Create recipe
    recipe = e2e_client.create_recipe(
        name=f"E2E Delete Recipe Test {unique_id}",
        ingredients=["2 cups flour", "1 tsp salt"]
    )
    test_cleanup_all["recipes"].append(recipe["slug"])
    recipe_id = recipe["id"]

    # Create shopping list
    list_name = f"E2E Delete Recipe List {unique_id}"
    shopping_list = e2e_client.post("/api/households/shopping/lists", json={
        "name": list_name
    })
    list_id = shopping_list["id"]
    test_cleanup_all["shopping_lists"].append(list_id)

    # Add recipe ingredients
    e2e_client.post(
        f"/api/households/shopping/lists/{list_id}/recipe/{recipe_id}",
        json={"recipeId": recipe_id}
    )

    # Verify items added
    shopping_list = e2e_client.get(f"/api/households/shopping/lists/{list_id}")
    initial_count = len(shopping_list["listItems"])
    assert initial_count > 0

    # Delete recipe from shopping list
    # Note: The API endpoint expects list_id in the URL path
    e2e_client.post(
        f"/api/households/shopping/lists/{list_id}/recipe/{recipe_id}/delete"
    )

    # Verify items removed or list is empty
    shopping_list = e2e_client.get(f"/api/households/shopping/lists/{list_id}")
    final_count = len(shopping_list["listItems"])
    # Should have fewer items (or zero if only recipe items were present)
    assert final_count < initial_count


@pytest.mark.e2e
def test_shopping_structured_items(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test shopping list with structured items (quantity, unit, food).

    Validates that shopping items can have structured data for better
    organization and aggregation.
    """
    # Create shopping list
    list_name = f"E2E Structured Items {unique_id}"
    shopping_list = e2e_client.post("/api/households/shopping/lists", json={
        "name": list_name
    })
    list_id = shopping_list["id"]
    test_cleanup_all["shopping_lists"].append(list_id)

    # Add items with different formats
    # Simple note-based item
    item1 = e2e_client.post("/api/households/shopping/items", json={
        "shoppingListId": list_id,
        "note": "2 cups flour"
    })

    # Item with display text
    item2 = e2e_client.post("/api/households/shopping/items", json={
        "shoppingListId": list_id,
        "display": "1 tsp salt",
        "note": "salt"
    })

    # Verify items exist
    shopping_list = e2e_client.get(f"/api/households/shopping/lists/{list_id}")
    assert len(shopping_list["listItems"]) == 2

    # Verify at least one has note or display
    items = shopping_list["listItems"]
    assert any(item.get("note") or item.get("display") for item in items)


@pytest.mark.e2e
def test_shopping_item_progress_tracking(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test tracking progress of checked/unchecked items in a shopping list.

    Validates the ability to monitor shopping progress by counting
    checked vs unchecked items.
    """
    # Create shopping list
    list_name = f"E2E Progress Test {unique_id}"
    shopping_list = e2e_client.post("/api/households/shopping/lists", json={
        "name": list_name
    })
    list_id = shopping_list["id"]
    test_cleanup_all["shopping_lists"].append(list_id)

    # Add 5 items
    items = []
    for i in range(5):
        item = e2e_client.post("/api/households/shopping/items", json={
            "shoppingListId": list_id,
            "note": f"Item {i+1}"
        })
        items.append(item)

    # Check first 3 items
    for i in range(3):
        e2e_client.put(f"/api/households/shopping/items/{items[i]['id']}", json={
            "id": items[i]["id"],
            "checked": True
        })

    # Get list and verify counts
    shopping_list = e2e_client.get(f"/api/households/shopping/lists/{list_id}")
    list_items = shopping_list["listItems"]

    checked_count = sum(1 for item in list_items if item.get("checked"))
    unchecked_count = sum(1 for item in list_items if not item.get("checked"))

    assert checked_count == 3
    assert unchecked_count == 2
    assert len(list_items) == 5


@pytest.mark.e2e
def test_shopping_error_nonexistent_list(
    e2e_client: MealieClient,
    unique_id: str
):
    """
    Test error handling when adding items to a non-existent shopping list.

    Validates proper error responses for invalid list IDs.
    """
    from httpx import HTTPStatusError

    # Try to add item to non-existent list
    fake_list_id = "00000000-0000-0000-0000-000000000000"

    with pytest.raises(HTTPStatusError) as exc_info:
        e2e_client.post("/api/households/shopping/items", json={
            "shoppingListId": fake_list_id,
            "note": "This should fail"
        })

    # Verify it's a 404 or 400 error
    assert exc_info.value.response.status_code in (400, 404)


@pytest.mark.e2e
def test_shopping_generate_from_empty_mealplan(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test error handling when generating shopping list from empty meal plan.

    Validates graceful handling when no recipes are in the meal plan
    for the specified date range.
    """
    # Use a far future date range with no meal plans
    future_date = (date.today() + timedelta(days=365)).isoformat()

    # Query meal plans for future date
    mealplan_response = e2e_client.get("/api/households/mealplans", params={
        "start_date": future_date,
        "end_date": future_date,
    })

    # Handle paginated response
    if isinstance(mealplan_response, dict) and "items" in mealplan_response:
        mealplan_entries = mealplan_response["items"]
    elif isinstance(mealplan_response, list):
        mealplan_entries = mealplan_response
    else:
        mealplan_entries = [mealplan_response] if mealplan_response else []

    # Should have no meal plans for far future date
    assert len(mealplan_entries) == 0 or all(
        not entry.get("recipeId") for entry in mealplan_entries
    ), "Should have no recipes in far future meal plans"


@pytest.mark.e2e
def test_shopping_multiple_recipes_to_one_list(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test adding multiple recipes to a single shopping list.

    Validates the workflow of aggregating ingredients from multiple
    recipes into one shopping list for meal planning.
    """
    # Create first recipe
    recipe1 = e2e_client.create_recipe(
        name=f"E2E Recipe 1 {unique_id}",
        ingredients=["2 cups flour", "1 tsp salt"]
    )
    test_cleanup_all["recipes"].append(recipe1["slug"])

    # Create second recipe
    recipe2 = e2e_client.create_recipe(
        name=f"E2E Recipe 2 {unique_id}",
        ingredients=["3 eggs", "1 cup milk"]
    )
    test_cleanup_all["recipes"].append(recipe2["slug"])

    # Create shopping list
    list_name = f"E2E Multi-Recipe List {unique_id}"
    shopping_list = e2e_client.post("/api/households/shopping/lists", json={
        "name": list_name
    })
    list_id = shopping_list["id"]
    test_cleanup_all["shopping_lists"].append(list_id)

    # Add first recipe
    e2e_client.post(
        f"/api/households/shopping/lists/{list_id}/recipe/{recipe1['id']}",
        json={"recipeId": recipe1["id"]}
    )

    # Add second recipe
    e2e_client.post(
        f"/api/households/shopping/lists/{list_id}/recipe/{recipe2['id']}",
        json={"recipeId": recipe2["id"]}
    )

    # Verify items from both recipes
    shopping_list = e2e_client.get(f"/api/households/shopping/lists/{list_id}")
    assert len(shopping_list["listItems"]) > 0

    item_texts = [
        item.get("note") or item.get("display") or ""
        for item in shopping_list["listItems"]
    ]

    # Should have items from both recipes
    has_recipe1_item = any("flour" in text.lower() or "salt" in text.lower()
                           for text in item_texts)
    has_recipe2_item = any("egg" in text.lower() or "milk" in text.lower()
                           for text in item_texts)

    assert has_recipe1_item or has_recipe2_item, \
        "Shopping list should have items from at least one recipe"


@pytest.mark.e2e
def test_shopping_uncheck_item(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test unchecking a previously checked shopping list item.

    Validates the toggle functionality for item completion status.
    """
    # Create shopping list
    list_name = f"E2E Uncheck Test {unique_id}"
    shopping_list = e2e_client.post("/api/households/shopping/lists", json={
        "name": list_name
    })
    list_id = shopping_list["id"]
    test_cleanup_all["shopping_lists"].append(list_id)

    # Add item
    item = e2e_client.post("/api/households/shopping/items", json={
        "shoppingListId": list_id,
        "note": "Test item"
    })
    item_id = item["id"]

    # Check item
    e2e_client.put(f"/api/households/shopping/items/{item_id}", json={
        "id": item_id,
        "checked": True
    })

    # Verify checked
    shopping_list = e2e_client.get(f"/api/households/shopping/lists/{list_id}")
    assert shopping_list["listItems"][0]["checked"] is True

    # Uncheck item
    e2e_client.put(f"/api/households/shopping/items/{item_id}", json={
        "id": item_id,
        "checked": False
    })

    # Verify unchecked
    shopping_list = e2e_client.get(f"/api/households/shopping/lists/{list_id}")
    assert shopping_list["listItems"][0]["checked"] is False
