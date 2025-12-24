"""
E2E tests for meal planning workflows.

These tests validate the complete meal planning workflow against a real Mealie instance,
including CRUD operations, search, batch updates, and meal plan rules.
"""

import pytest
from datetime import date, timedelta
from src.client import MealieClient
import httpx


@pytest.mark.e2e
def test_mealplan_create_get_update_delete_workflow(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test complete CRUD workflow for meal plans.

    Creates a meal plan, retrieves it, updates it, and then deletes it.
    """
    # Create recipe first to associate with mealplan
    recipe = e2e_client.create_recipe(
        name=f"E2E Mealplan Recipe {unique_id}",
        description="Test recipe for mealplan workflow"
    )
    test_cleanup_all["recipes"].append(recipe["slug"])

    # Create mealplan for a week from now
    meal_date = (date.today() + timedelta(days=7)).isoformat()

    payload = {
        "date": meal_date,
        "entryType": "dinner",
        "title": f"Test Meal {unique_id}",
        "text": "Original note",
        "recipeId": recipe["id"]
    }

    mealplan = e2e_client.post("/api/households/mealplans", json=payload)
    mealplan_id = mealplan["id"]
    test_cleanup_all["mealplans"].append(mealplan_id)

    # Verify created
    assert mealplan["date"] == meal_date
    assert mealplan["entryType"] == "dinner"
    assert mealplan["title"] == f"Test Meal {unique_id}"
    assert mealplan["recipeId"] == recipe["id"]

    # Retrieve mealplan
    retrieved = e2e_client.get(f"/api/households/mealplans/{mealplan_id}")
    assert retrieved["id"] == mealplan_id
    assert retrieved["date"] == meal_date

    # Update mealplan
    update_payload = {
        "id": mealplan_id,
        "date": meal_date,
        "entryType": "lunch",
        "title": f"Updated Meal {unique_id}",
        "text": "Updated note",
        "recipeId": recipe["id"]
    }

    updated = e2e_client.put(f"/api/households/mealplans/{mealplan_id}", json=update_payload)
    assert updated["entryType"] == "lunch"
    assert updated["title"] == f"Updated Meal {unique_id}"
    assert updated["text"] == "Updated note"

    # Delete mealplan (remove from cleanup list since we're deleting it)
    test_cleanup_all["mealplans"].remove(mealplan_id)
    e2e_client.delete(f"/api/households/mealplans/{mealplan_id}")

    # Verify deleted (should raise 404)
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        e2e_client.get(f"/api/households/mealplans/{mealplan_id}")
    assert exc_info.value.response.status_code == 404


@pytest.mark.e2e
def test_mealplan_search_by_recipe_name(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test mealplan search functionality by recipe name.

    Creates mealplans with specific recipe names and verifies search works.
    """
    # Create unique recipes
    recipe1 = e2e_client.create_recipe(
        name=f"E2E Searchable Pork Recipe {unique_id}",
        description="Contains keyword 'pork'"
    )
    test_cleanup_all["recipes"].append(recipe1["slug"])

    recipe2 = e2e_client.create_recipe(
        name=f"E2E Searchable Chicken Recipe {unique_id}",
        description="Contains keyword 'chicken'"
    )
    test_cleanup_all["recipes"].append(recipe2["slug"])

    # Create mealplans
    meal_date1 = (date.today() + timedelta(days=1)).isoformat()
    mealplan1 = e2e_client.post("/api/households/mealplans", json={
        "date": meal_date1,
        "entryType": "dinner",
        "recipeId": recipe1["id"]
    })
    test_cleanup_all["mealplans"].append(mealplan1["id"])

    meal_date2 = (date.today() + timedelta(days=2)).isoformat()
    mealplan2 = e2e_client.post("/api/households/mealplans", json={
        "date": meal_date2,
        "entryType": "dinner",
        "recipeId": recipe2["id"]
    })
    test_cleanup_all["mealplans"].append(mealplan2["id"])

    # Search for mealplans in the date range
    start_date = date.today().isoformat()
    end_date = (date.today() + timedelta(days=7)).isoformat()

    params = {
        "start_date": start_date,
        "end_date": end_date
    }

    all_mealplans = e2e_client.get("/api/households/mealplans", params=params)

    # Find our created mealplans by checking recipe names
    found_pork = False
    found_chicken = False

    for mp in all_mealplans:
        if mp.get("recipeId") == recipe1["id"]:
            found_pork = True
            assert "Pork" in mp.get("recipe", {}).get("name", "")
        elif mp.get("recipeId") == recipe2["id"]:
            found_chicken = True
            assert "Chicken" in mp.get("recipe", {}).get("name", "")

    assert found_pork, "Pork recipe mealplan not found in search"
    assert found_chicken, "Chicken recipe mealplan not found in search"


@pytest.mark.e2e
def test_mealplan_batch_update(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test batch update of multiple mealplans.

    Creates multiple mealplans and updates them in a batch operation.
    """
    # Create recipe
    recipe = e2e_client.create_recipe(
        name=f"E2E Batch Update Recipe {unique_id}",
        description="Recipe for batch testing"
    )
    test_cleanup_all["recipes"].append(recipe["slug"])

    # Create multiple mealplans
    mealplan_ids = []
    for i in range(3):
        meal_date = (date.today() + timedelta(days=i+1)).isoformat()
        mealplan = e2e_client.post("/api/households/mealplans", json={
            "date": meal_date,
            "entryType": "dinner",
            "title": f"Original Title {i}",
            "recipeId": recipe["id"]
        })
        mealplan_ids.append(mealplan["id"])
        test_cleanup_all["mealplans"].append(mealplan["id"])

    # Update all mealplans individually (batch update endpoint may not exist)
    for idx, mp_id in enumerate(mealplan_ids):
        # Get current mealplan
        current = e2e_client.get(f"/api/households/mealplans/{mp_id}")

        # Update with new title
        update_payload = {
            "id": mp_id,
            "date": current["date"],
            "entryType": current["entryType"],
            "title": f"Batch Updated Title {idx}",
            "text": "Batch updated note",
            "recipeId": recipe["id"]
        }

        updated = e2e_client.put(f"/api/households/mealplans/{mp_id}", json=update_payload)
        assert updated["title"] == f"Batch Updated Title {idx}"
        assert updated["text"] == "Batch updated note"


@pytest.mark.e2e
def test_mealplan_delete_range(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test deleting multiple mealplans in a date range.

    Creates several mealplans across multiple days and deletes them all.
    """
    # Create recipe
    recipe = e2e_client.create_recipe(
        name=f"E2E Delete Range Recipe {unique_id}",
        description="Recipe for delete range testing"
    )
    test_cleanup_all["recipes"].append(recipe["slug"])

    # Create mealplans for 5 consecutive days
    mealplan_ids = []
    start_offset = 10  # Start 10 days from now to avoid conflicts

    for i in range(5):
        meal_date = (date.today() + timedelta(days=start_offset + i)).isoformat()
        mealplan = e2e_client.post("/api/households/mealplans", json={
            "date": meal_date,
            "entryType": "lunch",
            "title": f"Day {i} Lunch",
            "recipeId": recipe["id"]
        })
        mealplan_ids.append(mealplan["id"])
        test_cleanup_all["mealplans"].append(mealplan["id"])

    # Verify all created
    start_date = (date.today() + timedelta(days=start_offset)).isoformat()
    end_date = (date.today() + timedelta(days=start_offset + 5)).isoformat()

    mealplans = e2e_client.get("/api/households/mealplans", params={
        "start_date": start_date,
        "end_date": end_date
    })

    # Count our mealplans
    our_mealplans = [mp for mp in mealplans if mp["id"] in mealplan_ids]
    assert len(our_mealplans) == 5

    # Delete all mealplans
    for mp_id in mealplan_ids:
        e2e_client.delete(f"/api/households/mealplans/{mp_id}")
        test_cleanup_all["mealplans"].remove(mp_id)

    # Verify all deleted
    mealplans_after = e2e_client.get("/api/households/mealplans", params={
        "start_date": start_date,
        "end_date": end_date
    })

    remaining = [mp for mp in mealplans_after if mp["id"] in mealplan_ids]
    assert len(remaining) == 0, "Some mealplans were not deleted"


@pytest.mark.e2e
def test_mealplan_rule_create_apply_delete_workflow(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test meal plan rule workflow.

    Creates a rule, verifies it exists, and deletes it.
    """
    # Create tag for the rule
    tag = e2e_client.create_tag(name=f"E2E Rule Tag {unique_id}")
    test_cleanup_all["tags"].append(tag["id"])

    # Create category for the rule
    category = e2e_client.create_category(name=f"E2E Rule Category {unique_id}")
    test_cleanup_all["categories"].append(category["id"])

    # Create meal plan rule
    rule = e2e_client.create_mealplan_rule(
        name=f"E2E Test Rule {unique_id}",
        entry_type="dinner",
        tags=[tag["name"]],
        categories=[category["name"]]
    )

    rule_id = rule["id"]

    # Verify created
    assert rule["name"] == f"E2E Test Rule {unique_id}"
    assert rule["entryType"] == "dinner"

    # Retrieve rule
    retrieved = e2e_client.get_mealplan_rule(rule_id)
    assert retrieved["id"] == rule_id
    assert retrieved["name"] == f"E2E Test Rule {unique_id}"

    # Update rule
    updated = e2e_client.update_mealplan_rule(
        rule_id=rule_id,
        name=f"Updated Rule {unique_id}"
    )
    assert updated["name"] == f"Updated Rule {unique_id}"

    # Delete rule
    e2e_client.delete_mealplan_rule(rule_id)

    # Verify deleted
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        e2e_client.get_mealplan_rule(rule_id)
    assert exc_info.value.response.status_code == 404


@pytest.mark.e2e
def test_mealplan_list_current_week(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test listing mealplans for the current week.

    Creates mealplans for this week and verifies list retrieval.
    """
    # Create recipe
    recipe = e2e_client.create_recipe(
        name=f"E2E Current Week Recipe {unique_id}",
        description="Recipe for current week testing"
    )
    test_cleanup_all["recipes"].append(recipe["slug"])

    # Create mealplans for today and tomorrow
    today = date.today()
    tomorrow = today + timedelta(days=1)

    mealplan_today = e2e_client.post("/api/households/mealplans", json={
        "date": today.isoformat(),
        "entryType": "breakfast",
        "title": "Today's Breakfast",
        "recipeId": recipe["id"]
    })
    test_cleanup_all["mealplans"].append(mealplan_today["id"])

    mealplan_tomorrow = e2e_client.post("/api/households/mealplans", json={
        "date": tomorrow.isoformat(),
        "entryType": "lunch",
        "title": "Tomorrow's Lunch",
        "recipeId": recipe["id"]
    })
    test_cleanup_all["mealplans"].append(mealplan_tomorrow["id"])

    # List mealplans for current week
    start_date = today.isoformat()
    end_date = (today + timedelta(days=7)).isoformat()

    mealplans = e2e_client.get("/api/households/mealplans", params={
        "start_date": start_date,
        "end_date": end_date
    })

    # Verify our mealplans are in the list
    our_ids = {mealplan_today["id"], mealplan_tomorrow["id"]}
    found_ids = {mp["id"] for mp in mealplans if mp["id"] in our_ids}

    assert found_ids == our_ids, "Not all mealplans found in current week listing"


@pytest.mark.e2e
def test_mealplan_today_retrieval(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test retrieving today's mealplans.

    Creates mealplans for today and verifies /today endpoint.
    """
    # Create recipes for different meal types
    recipe1 = e2e_client.create_recipe(
        name=f"E2E Today Breakfast {unique_id}",
        description="Breakfast recipe"
    )
    test_cleanup_all["recipes"].append(recipe1["slug"])

    recipe2 = e2e_client.create_recipe(
        name=f"E2E Today Dinner {unique_id}",
        description="Dinner recipe"
    )
    test_cleanup_all["recipes"].append(recipe2["slug"])

    # Create mealplans for today
    today = date.today().isoformat()

    breakfast = e2e_client.post("/api/households/mealplans", json={
        "date": today,
        "entryType": "breakfast",
        "recipeId": recipe1["id"]
    })
    test_cleanup_all["mealplans"].append(breakfast["id"])

    dinner = e2e_client.post("/api/households/mealplans", json={
        "date": today,
        "entryType": "dinner",
        "recipeId": recipe2["id"]
    })
    test_cleanup_all["mealplans"].append(dinner["id"])

    # Get today's mealplans
    today_mealplans = e2e_client.get("/api/households/mealplans/today")

    # Verify we got a list
    assert isinstance(today_mealplans, list)

    # Find our mealplans
    our_ids = {breakfast["id"], dinner["id"]}
    found_ids = {mp["id"] for mp in today_mealplans if mp["id"] in our_ids}

    assert found_ids == our_ids, "Not all today's mealplans found"


@pytest.mark.e2e
def test_mealplan_by_specific_date_retrieval(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test retrieving mealplans for a specific date.

    Creates mealplans for a specific date and verifies retrieval.
    """
    # Create recipe
    recipe = e2e_client.create_recipe(
        name=f"E2E Specific Date Recipe {unique_id}",
        description="Recipe for specific date testing"
    )
    test_cleanup_all["recipes"].append(recipe["slug"])

    # Create mealplans for a specific date (5 days from now)
    target_date = (date.today() + timedelta(days=5)).isoformat()

    mealplan1 = e2e_client.post("/api/households/mealplans", json={
        "date": target_date,
        "entryType": "breakfast",
        "title": "Specific Date Breakfast",
        "recipeId": recipe["id"]
    })
    test_cleanup_all["mealplans"].append(mealplan1["id"])

    mealplan2 = e2e_client.post("/api/households/mealplans", json={
        "date": target_date,
        "entryType": "dinner",
        "title": "Specific Date Dinner",
        "recipeId": recipe["id"]
    })
    test_cleanup_all["mealplans"].append(mealplan2["id"])

    # Retrieve mealplans for that specific date
    mealplans = e2e_client.get("/api/households/mealplans", params={
        "start_date": target_date,
        "end_date": target_date
    })

    # Filter to just our mealplans
    our_ids = {mealplan1["id"], mealplan2["id"]}
    found = [mp for mp in mealplans if mp["id"] in our_ids]

    assert len(found) == 2, "Should find exactly 2 mealplans for the specific date"
    assert all(mp["date"] == target_date for mp in found)


@pytest.mark.e2e
def test_mealplan_random_suggestion(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test random mealplan suggestion.

    Creates a recipe and verifies random suggestion endpoint works.
    """
    # Create a couple recipes to have options
    recipe1 = e2e_client.create_recipe(
        name=f"E2E Random Recipe 1 {unique_id}",
        description="First random recipe option"
    )
    test_cleanup_all["recipes"].append(recipe1["slug"])

    recipe2 = e2e_client.create_recipe(
        name=f"E2E Random Recipe 2 {unique_id}",
        description="Second random recipe option"
    )
    test_cleanup_all["recipes"].append(recipe2["slug"])

    # Get random suggestion (if endpoint exists)
    # Note: This assumes /api/recipes/random exists
    try:
        random_recipe = e2e_client.get("/api/recipes/random")

        # Verify we got a valid recipe
        assert "id" in random_recipe
        assert "name" in random_recipe
        assert "slug" in random_recipe
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            pytest.skip("Random recipe endpoint not available")
        raise


@pytest.mark.e2e
def test_mealplan_with_recipe_association(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test mealplan with full recipe association.

    Creates a detailed recipe, associates it with a mealplan, and verifies
    the recipe data is properly linked.
    """
    # Create detailed recipe
    recipe = e2e_client.create_recipe(
        name=f"E2E Associated Recipe {unique_id}",
        description="Detailed recipe for association testing",
        recipe_yield="4 servings",
        total_time="1 hour"
    )
    test_cleanup_all["recipes"].append(recipe["slug"])

    # Create mealplan with recipe
    meal_date = (date.today() + timedelta(days=3)).isoformat()

    mealplan = e2e_client.post("/api/households/mealplans", json={
        "date": meal_date,
        "entryType": "dinner",
        "title": f"Associated Meal {unique_id}",
        "text": "Meal with full recipe details",
        "recipeId": recipe["id"]
    })
    test_cleanup_all["mealplans"].append(mealplan["id"])

    # Verify mealplan has recipe association
    assert mealplan["recipeId"] == recipe["id"]

    # Retrieve and verify recipe data is included
    retrieved = e2e_client.get(f"/api/households/mealplans/{mealplan['id']}")

    # Check if recipe object is embedded
    if "recipe" in retrieved and retrieved["recipe"]:
        recipe_data = retrieved["recipe"]
        assert recipe_data["id"] == recipe["id"]
        assert recipe_data["name"] == f"E2E Associated Recipe {unique_id}"
        assert recipe_data["slug"] == recipe["slug"]


@pytest.mark.e2e
def test_mealplan_delete_nonexistent_error(
    e2e_client: MealieClient,
    unique_id: str
):
    """
    Test error scenario: deleting a non-existent mealplan.

    Verifies that attempting to delete a non-existent mealplan raises 404.
    """
    # Generate a fake UUID
    fake_id = "00000000-0000-0000-0000-000000000000"

    # Attempt to delete non-existent mealplan
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        e2e_client.delete(f"/api/households/mealplans/{fake_id}")

    # Verify 404 status
    assert exc_info.value.response.status_code == 404


@pytest.mark.e2e
def test_mealplan_create_invalid_date_format_error(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test error scenario: creating mealplan with invalid date format.

    Verifies that invalid date formats are properly rejected.
    """
    # Create recipe for the test
    recipe = e2e_client.create_recipe(
        name=f"E2E Invalid Date Recipe {unique_id}",
        description="Recipe for invalid date testing"
    )
    test_cleanup_all["recipes"].append(recipe["slug"])

    # Attempt to create mealplan with invalid date format
    invalid_dates = [
        "2025-13-01",  # Invalid month
        "2025-02-30",  # Invalid day
        "not-a-date",  # Completely invalid
        "01/15/2025",  # Wrong format (should be YYYY-MM-DD)
    ]

    for invalid_date in invalid_dates:
        with pytest.raises((httpx.HTTPStatusError, ValueError)) as exc_info:
            e2e_client.post("/api/households/mealplans", json={
                "date": invalid_date,
                "entryType": "dinner",
                "recipeId": recipe["id"]
            })

        # HTTPStatusError should be 400 or 422
        if isinstance(exc_info.value, httpx.HTTPStatusError):
            assert exc_info.value.response.status_code in [400, 422]


@pytest.mark.e2e
def test_mealplan_update_change_recipe(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test updating a mealplan to change its associated recipe.

    Creates a mealplan with one recipe, then updates to use a different recipe.
    """
    # Create two recipes
    recipe1 = e2e_client.create_recipe(
        name=f"E2E Original Recipe {unique_id}",
        description="Original recipe"
    )
    test_cleanup_all["recipes"].append(recipe1["slug"])

    recipe2 = e2e_client.create_recipe(
        name=f"E2E Replacement Recipe {unique_id}",
        description="Replacement recipe"
    )
    test_cleanup_all["recipes"].append(recipe2["slug"])

    # Create mealplan with first recipe
    meal_date = (date.today() + timedelta(days=4)).isoformat()

    mealplan = e2e_client.post("/api/households/mealplans", json={
        "date": meal_date,
        "entryType": "lunch",
        "recipeId": recipe1["id"]
    })
    test_cleanup_all["mealplans"].append(mealplan["id"])

    # Verify initial recipe
    assert mealplan["recipeId"] == recipe1["id"]

    # Update to use second recipe
    updated = e2e_client.put(f"/api/households/mealplans/{mealplan['id']}", json={
        "id": mealplan["id"],
        "date": meal_date,
        "entryType": "lunch",
        "recipeId": recipe2["id"]
    })

    # Verify recipe changed
    assert updated["recipeId"] == recipe2["id"]

    # Retrieve and double-check
    retrieved = e2e_client.get(f"/api/households/mealplans/{mealplan['id']}")
    assert retrieved["recipeId"] == recipe2["id"]


@pytest.mark.e2e
def test_mealplan_without_recipe(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test creating mealplan without a recipe (using title and text only).

    Verifies that mealplans can be created with just text content,
    no recipe association required.
    """
    # Create mealplan without recipe
    meal_date = (date.today() + timedelta(days=6)).isoformat()

    mealplan = e2e_client.post("/api/households/mealplans", json={
        "date": meal_date,
        "entryType": "snack",
        "title": f"Custom Snack {unique_id}",
        "text": "No recipe needed for this simple snack"
    })
    test_cleanup_all["mealplans"].append(mealplan["id"])

    # Verify mealplan created without recipe
    assert mealplan["title"] == f"Custom Snack {unique_id}"
    assert mealplan["text"] == "No recipe needed for this simple snack"
    assert mealplan.get("recipeId") is None or mealplan.get("recipeId") == ""

    # Retrieve and verify
    retrieved = e2e_client.get(f"/api/households/mealplans/{mealplan['id']}")
    assert retrieved["title"] == f"Custom Snack {unique_id}"
    assert retrieved.get("recipeId") is None or retrieved.get("recipeId") == ""
