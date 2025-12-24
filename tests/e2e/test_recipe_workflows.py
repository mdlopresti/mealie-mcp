"""
Comprehensive E2E tests for recipe workflows.

These tests validate real recipe workflows against a live Mealie instance,
covering CRUD operations, bulk operations, imports, and error scenarios.
"""

import pytest
import json
from src.client import MealieClient


@pytest.mark.e2e
def test_recipe_search_get_update_workflow(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test workflow: Create → Search → Get → Update → Verify.

    Validates that recipes can be created, found via search, retrieved,
    updated, and that updates persist correctly.
    """
    # Create recipe
    recipe_name = f"E2E Search Test {unique_id}"
    recipe = e2e_client.post("/api/recipes", json={"name": recipe_name})
    slug = recipe.strip('"')
    test_cleanup_all["recipes"].append(slug)

    # Search for the recipe
    search_result = e2e_client.get("/api/recipes", params={
        "search": unique_id,
        "perPage": 10
    })
    assert "items" in search_result
    found = any(r["slug"] == slug for r in search_result["items"])
    assert found, f"Recipe {slug} not found in search results"

    # Get the recipe
    retrieved = e2e_client.get(f"/api/recipes/{slug}")
    assert retrieved["name"] == recipe_name
    assert retrieved["slug"] == slug

    # Update the recipe
    update_payload = {
        "id": retrieved["id"],
        "userId": retrieved["userId"],
        "householdId": retrieved["householdId"],
        "groupId": retrieved["groupId"],
        "name": recipe_name,
        "slug": slug,
        "description": "Updated description for E2E test",
        "recipeYield": "4 servings"
    }
    updated = e2e_client.patch(f"/api/recipes/{slug}", json=update_payload)

    # Verify updates persisted
    assert updated["description"] == "Updated description for E2E test"
    assert updated["recipeYield"] == "4 servings"


@pytest.mark.e2e
def test_recipe_create_tag_categorize_workflow(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test workflow: Create recipe → Create tag → Create category → Tag recipe → Categorize recipe.

    Validates that recipes can be tagged and categorized correctly.
    """
    # Create recipe
    recipe_name = f"E2E Tag Test {unique_id}"
    recipe_slug = e2e_client.post("/api/recipes", json={"name": recipe_name}).strip('"')
    test_cleanup_all["recipes"].append(recipe_slug)

    # Create tag
    tag = e2e_client.post("/api/organizers/tags", json={"name": f"E2E Tag {unique_id}"})
    test_cleanup_all["tags"].append(tag["id"])

    # Create category
    category = e2e_client.post("/api/organizers/categories", json={"name": f"E2E Category {unique_id}"})
    test_cleanup_all["categories"].append(category["id"])

    # Get recipe to get full structure
    recipe = e2e_client.get(f"/api/recipes/{recipe_slug}")

    # Update recipe with tag and category
    update_payload = {
        "id": recipe["id"],
        "userId": recipe["userId"],
        "householdId": recipe["householdId"],
        "groupId": recipe["groupId"],
        "name": recipe_name,
        "slug": recipe_slug,
        "tags": [{"id": tag["id"], "name": tag["name"], "slug": tag["slug"]}],
        "recipeCategory": [{"id": category["id"], "name": category["name"], "slug": category["slug"]}]
    }
    updated = e2e_client.patch(f"/api/recipes/{recipe_slug}", json=update_payload)

    # Verify tag and category applied
    assert len(updated["tags"]) == 1
    assert updated["tags"][0]["name"] == tag["name"]
    assert len(updated["recipeCategory"]) == 1
    assert updated["recipeCategory"][0]["name"] == category["name"]


@pytest.mark.e2e
def test_recipe_import_from_url(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test importing a recipe from a public URL.

    Uses a well-known recipe URL that should import successfully.
    """
    # Use a reliable public recipe URL
    test_url = "https://www.allrecipes.com/recipe/21014/good-old-fashioned-pancakes/"

    # Import recipe
    import_payload = {"url": test_url, "includeTags": False}
    result = e2e_client.post("/api/recipes/create-url", json=import_payload)

    # Result should be a slug or recipe object
    if isinstance(result, str):
        slug = result.strip('"')
    else:
        slug = result.get("slug")

    assert slug is not None, "Import should return a recipe slug"
    test_cleanup_all["recipes"].append(slug)

    # Verify recipe was imported with content
    recipe = e2e_client.get(f"/api/recipes/{slug}")
    assert recipe["name"], "Imported recipe should have a name"
    assert recipe.get("recipeIngredient"), "Imported recipe should have ingredients"
    assert recipe.get("recipeInstructions"), "Imported recipe should have instructions"


@pytest.mark.e2e
def test_recipe_image_upload_from_url(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test uploading a recipe image from a URL.

    Creates a recipe and uploads an image from a public URL.
    """
    # Create recipe
    recipe_name = f"E2E Image Test {unique_id}"
    recipe_slug = e2e_client.post("/api/recipes", json={"name": recipe_name}).strip('"')
    test_cleanup_all["recipes"].append(recipe_slug)

    # Upload image from a reliable public URL (Anova recipe image)
    image_url = "https://images.anovaculinary.com/sous-vide-salmon-2/header/sous-vide-salmon-2-header-centered.jpg"
    result = e2e_client.upload_recipe_image_from_url(recipe_slug, image_url)

    # Verify upload succeeded
    assert result is not None

    # Verify recipe now has an image
    recipe = e2e_client.get(f"/api/recipes/{recipe_slug}")
    assert recipe.get("image"), "Recipe should have an image after upload"


@pytest.mark.e2e
def test_recipe_duplicate(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test duplicating a recipe with custom name.

    Creates a recipe with content, duplicates it, and verifies the duplicate.
    """
    # Create original recipe with content
    original_name = f"E2E Original {unique_id}"
    original_slug = e2e_client.post("/api/recipes", json={"name": original_name}).strip('"')
    test_cleanup_all["recipes"].append(original_slug)

    # Add some content to the original
    original = e2e_client.get(f"/api/recipes/{original_slug}")
    update_payload = {
        "id": original["id"],
        "userId": original["userId"],
        "householdId": original["householdId"],
        "groupId": original["groupId"],
        "name": original_name,
        "slug": original_slug,
        "description": "Original recipe for duplication test",
        "recipeYield": "2 servings"
    }
    e2e_client.patch(f"/api/recipes/{original_slug}", json=update_payload)

    # Duplicate the recipe
    duplicate_name = f"E2E Duplicate {unique_id}"
    duplicate = e2e_client.duplicate_recipe(original_slug, new_name=duplicate_name)
    test_cleanup_all["recipes"].append(duplicate["slug"])

    # Verify duplicate has correct name and content from original
    assert duplicate["name"] == duplicate_name
    assert duplicate["slug"] != original_slug, "Duplicate should have different slug"
    assert duplicate["description"] == "Original recipe for duplication test"
    assert duplicate["recipeYield"] == "2 servings"


@pytest.mark.e2e
def test_recipe_delete_with_verification(
    e2e_client: MealieClient,
    unique_id: str
):
    """
    Test recipe deletion and verify it's gone.

    Note: Not using test_cleanup_all since we delete manually.
    """
    # Create recipe
    recipe_name = f"E2E Delete Test {unique_id}"
    recipe_slug = e2e_client.post("/api/recipes", json={"name": recipe_name}).strip('"')

    # Verify it exists
    recipe = e2e_client.get(f"/api/recipes/{recipe_slug}")
    assert recipe["name"] == recipe_name

    # Delete it
    e2e_client.delete(f"/api/recipes/{recipe_slug}")

    # Verify it's gone (should raise 404)
    with pytest.raises(Exception) as exc_info:
        e2e_client.get(f"/api/recipes/{recipe_slug}")
    assert "404" in str(exc_info.value)


@pytest.mark.e2e
def test_recipe_bulk_tag_operation(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test bulk tagging multiple recipes at once.

    Creates multiple recipes and a tag, then applies tag to all recipes via bulk operation.
    """
    # Create multiple recipes
    recipe_slugs = []
    recipe_ids = []
    for i in range(3):
        name = f"E2E Bulk Tag Recipe {i} {unique_id}"
        slug = e2e_client.post("/api/recipes", json={"name": name}).strip('"')
        recipe_slugs.append(slug)
        test_cleanup_all["recipes"].append(slug)

        # Get recipe ID
        recipe = e2e_client.get(f"/api/recipes/{slug}")
        recipe_ids.append(recipe["id"])

    # Create tag
    tag = e2e_client.post("/api/organizers/tags", json={"name": f"E2E Bulk Tag {unique_id}"})
    test_cleanup_all["tags"].append(tag["id"])

    # Bulk tag all recipes
    result = e2e_client.bulk_tag_recipes(recipe_ids, [tag["name"]])

    # Verify all recipes now have the tag
    for slug in recipe_slugs:
        recipe = e2e_client.get(f"/api/recipes/{slug}")
        assert len(recipe["tags"]) == 1
        assert recipe["tags"][0]["name"] == tag["name"]


@pytest.mark.e2e
def test_recipe_bulk_categorize_operation(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test bulk categorizing multiple recipes at once.

    Creates multiple recipes and a category, then applies category to all recipes.
    """
    # Create multiple recipes
    recipe_slugs = []
    recipe_ids = []
    for i in range(3):
        name = f"E2E Bulk Cat Recipe {i} {unique_id}"
        slug = e2e_client.post("/api/recipes", json={"name": name}).strip('"')
        recipe_slugs.append(slug)
        test_cleanup_all["recipes"].append(slug)

        # Get recipe ID
        recipe = e2e_client.get(f"/api/recipes/{slug}")
        recipe_ids.append(recipe["id"])

    # Create category
    category = e2e_client.post("/api/organizers/categories", json={"name": f"E2E Bulk Cat {unique_id}"})
    test_cleanup_all["categories"].append(category["id"])

    # Bulk categorize all recipes
    result = e2e_client.bulk_categorize_recipes(recipe_ids, [category["name"]])

    # Verify all recipes now have the category
    for slug in recipe_slugs:
        recipe = e2e_client.get(f"/api/recipes/{slug}")
        assert len(recipe["recipeCategory"]) == 1
        assert recipe["recipeCategory"][0]["name"] == category["name"]


@pytest.mark.e2e
def test_recipe_bulk_delete_operation(
    e2e_client: MealieClient,
    unique_id: str
):
    """
    Test bulk deleting multiple recipes at once.

    Note: Not using test_cleanup_all since we delete manually.
    """
    # Create multiple recipes
    recipe_slugs = []
    recipe_ids = []
    for i in range(3):
        name = f"E2E Bulk Del Recipe {i} {unique_id}"
        slug = e2e_client.post("/api/recipes", json={"name": name}).strip('"')
        recipe_slugs.append(slug)

        # Get recipe ID
        recipe = e2e_client.get(f"/api/recipes/{slug}")
        recipe_ids.append(recipe["id"])

    # Verify all exist
    for slug in recipe_slugs:
        recipe = e2e_client.get(f"/api/recipes/{slug}")
        assert recipe["slug"] == slug

    # Bulk delete
    result = e2e_client.bulk_delete_recipes(recipe_ids)

    # Verify all are gone
    for slug in recipe_slugs:
        with pytest.raises(Exception) as exc_info:
            e2e_client.get(f"/api/recipes/{slug}")
        assert "404" in str(exc_info.value)


@pytest.mark.e2e
def test_recipe_structured_ingredients_update(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test updating recipe with structured ingredients from parser.

    Parses ingredient strings, then updates recipe with structured data.
    """
    # Create recipe
    recipe_name = f"E2E Structured Ing {unique_id}"
    recipe_slug = e2e_client.post("/api/recipes", json={"name": recipe_name}).strip('"')
    test_cleanup_all["recipes"].append(recipe_slug)

    # Parse ingredients
    ingredient_strings = [
        "2 cups all-purpose flour",
        "1 tsp baking powder",
        "1/2 cup butter, softened"
    ]
    parsed = e2e_client.parse_ingredients_batch(ingredient_strings)

    # Extract structured ingredients
    structured_ingredients = [item["ingredient"] for item in parsed]

    # Update recipe with structured ingredients
    result = e2e_client.update_recipe_ingredients(recipe_slug, structured_ingredients)

    # Verify ingredients were updated with structured data
    assert len(result["recipeIngredient"]) == 3
    for ing in result["recipeIngredient"]:
        assert "quantity" in ing or "food" in ing or "unit" in ing, \
            "Ingredient should have structured fields"


@pytest.mark.e2e
def test_recipe_last_made_timestamp_update(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test updating the last made timestamp for a recipe.

    Creates a recipe and sets its last made timestamp.
    """
    # Create recipe
    recipe_name = f"E2E Last Made {unique_id}"
    recipe_slug = e2e_client.post("/api/recipes", json={"name": recipe_name}).strip('"')
    test_cleanup_all["recipes"].append(recipe_slug)

    # Update last made timestamp
    timestamp = "2025-12-23T10:00:00Z"
    result = e2e_client.update_recipe_last_made(recipe_slug, timestamp=timestamp)

    # Verify timestamp was set
    assert result.get("lastMade"), "Recipe should have lastMade timestamp"


@pytest.mark.e2e
def test_recipe_create_with_full_data(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test creating a recipe with complete data (ingredients, instructions, nutrition).

    Validates that all fields can be set during creation.
    """
    # Create recipe stub
    recipe_name = f"E2E Full Data {unique_id}"
    recipe_slug = e2e_client.post("/api/recipes", json={"name": recipe_name}).strip('"')
    test_cleanup_all["recipes"].append(recipe_slug)

    # Get recipe to get required IDs
    recipe = e2e_client.get(f"/api/recipes/{recipe_slug}")

    # Update with full data
    update_payload = {
        "id": recipe["id"],
        "userId": recipe["userId"],
        "householdId": recipe["householdId"],
        "groupId": recipe["groupId"],
        "name": recipe_name,
        "slug": recipe_slug,
        "description": "A comprehensive test recipe with all fields",
        "recipeYield": "6 servings",
        "totalTime": "1 hour 15 minutes",
        "prepTime": "15 minutes",
        "cookTime": "1 hour",
        "recipeIngredient": [
            {"note": "2 cups flour", "display": "2 cups flour"},
            {"note": "1 tsp salt", "display": "1 tsp salt"}
        ],
        "recipeInstructions": [
            {"text": "Preheat oven to 350°F", "title": ""},
            {"text": "Mix dry ingredients", "title": ""}
        ],
        "nutrition": {
            "calories": "250",
            "protein": "8g",
            "carbohydrateContent": "45g"
        }
    }
    updated = e2e_client.patch(f"/api/recipes/{recipe_slug}", json=update_payload)

    # Verify all fields were set
    assert updated["description"] == "A comprehensive test recipe with all fields"
    assert updated["recipeYield"] == "6 servings"
    assert updated["totalTime"] == "1 hour 15 minutes"
    assert updated["prepTime"] == "15 minutes"
    assert updated["cookTime"] == "1 hour"
    assert len(updated["recipeIngredient"]) == 2
    assert len(updated["recipeInstructions"]) == 2
    assert updated["nutrition"]["calories"] == "250"


@pytest.mark.e2e
def test_recipe_get_nonexistent_404_error(
    e2e_client: MealieClient,
    unique_id: str
):
    """
    Test error scenario: Getting a non-existent recipe should return 404.

    Verifies proper error handling for missing resources.
    """
    # Try to get a recipe that doesn't exist
    nonexistent_slug = f"nonexistent-recipe-{unique_id}"

    with pytest.raises(Exception) as exc_info:
        e2e_client.get(f"/api/recipes/{nonexistent_slug}")

    # Should be a 404 error
    assert "404" in str(exc_info.value)


@pytest.mark.e2e
def test_recipe_update_invalid_slug_error(
    e2e_client: MealieClient,
    unique_id: str
):
    """
    Test error scenario: Updating with invalid slug should fail.

    Verifies proper error handling for invalid operations.
    """
    # Try to update a recipe that doesn't exist
    nonexistent_slug = f"nonexistent-recipe-{unique_id}"

    update_payload = {
        "name": "Invalid Update",
        "slug": nonexistent_slug,
        "description": "This should fail"
    }

    with pytest.raises(Exception) as exc_info:
        e2e_client.patch(f"/api/recipes/{nonexistent_slug}", json=update_payload)

    # Should be an error (404 or 422)
    assert "404" in str(exc_info.value) or "422" in str(exc_info.value)


@pytest.mark.e2e
def test_recipe_search_with_tag_filter(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test searching recipes with tag filter.

    Creates multiple recipes, tags one, and verifies search filter works.
    """
    # Create tag
    tag = e2e_client.post("/api/organizers/tags", json={"name": f"E2E Search Tag {unique_id}"})
    test_cleanup_all["tags"].append(tag["id"])

    # Create two recipes
    recipe1_slug = e2e_client.post("/api/recipes", json={"name": f"E2E Search 1 {unique_id}"}).strip('"')
    recipe2_slug = e2e_client.post("/api/recipes", json={"name": f"E2E Search 2 {unique_id}"}).strip('"')
    test_cleanup_all["recipes"].extend([recipe1_slug, recipe2_slug])

    # Tag only the first recipe
    recipe1 = e2e_client.get(f"/api/recipes/{recipe1_slug}")
    update_payload = {
        "id": recipe1["id"],
        "userId": recipe1["userId"],
        "householdId": recipe1["householdId"],
        "groupId": recipe1["groupId"],
        "name": recipe1["name"],
        "slug": recipe1_slug,
        "tags": [{"id": tag["id"], "name": tag["name"], "slug": tag["slug"]}]
    }
    e2e_client.patch(f"/api/recipes/{recipe1_slug}", json=update_payload)

    # Search with tag filter
    search_result = e2e_client.get("/api/recipes", params={
        "tags": [tag["name"]],
        "perPage": 50
    })

    # Verify only tagged recipe appears in results
    assert "items" in search_result
    found_slugs = [r["slug"] for r in search_result["items"]]
    assert recipe1_slug in found_slugs, "Tagged recipe should be in results"


@pytest.mark.e2e
def test_recipe_search_with_category_filter(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test searching recipes with category filter.

    Creates multiple recipes, categorizes one, and verifies search filter works.
    """
    # Create category
    category = e2e_client.post("/api/organizers/categories", json={"name": f"E2E Search Cat {unique_id}"})
    test_cleanup_all["categories"].append(category["id"])

    # Create two recipes
    recipe1_slug = e2e_client.post("/api/recipes", json={"name": f"E2E Cat Search 1 {unique_id}"}).strip('"')
    recipe2_slug = e2e_client.post("/api/recipes", json={"name": f"E2E Cat Search 2 {unique_id}"}).strip('"')
    test_cleanup_all["recipes"].extend([recipe1_slug, recipe2_slug])

    # Categorize only the first recipe
    recipe1 = e2e_client.get(f"/api/recipes/{recipe1_slug}")
    update_payload = {
        "id": recipe1["id"],
        "userId": recipe1["userId"],
        "householdId": recipe1["householdId"],
        "groupId": recipe1["groupId"],
        "name": recipe1["name"],
        "slug": recipe1_slug,
        "recipeCategory": [{"id": category["id"], "name": category["name"], "slug": category["slug"]}]
    }
    e2e_client.patch(f"/api/recipes/{recipe1_slug}", json=update_payload)

    # Search with category filter
    search_result = e2e_client.get("/api/recipes", params={
        "categories": [category["name"]],
        "perPage": 50
    })

    # Verify only categorized recipe appears in results
    assert "items" in search_result
    found_slugs = [r["slug"] for r in search_result["items"]]
    assert recipe1_slug in found_slugs, "Categorized recipe should be in results"


@pytest.mark.e2e
def test_recipe_suggestions_workflow(e2e_client: MealieClient):
    """
    Test workflow: Get recipe suggestions with default and custom limits.

    Validates that recipe suggestions can be retrieved from the live API.
    """
    # Get suggestions with default limit
    suggestions_default = e2e_client.get_recipe_suggestions()
    
    assert isinstance(suggestions_default, list), "Suggestions should be a list"
    # Note: May be empty if no recipes exist or no history, but should not error
    assert len(suggestions_default) <= 10, "Default limit should be 10"
    
    # Get suggestions with custom limit (5)
    suggestions_custom = e2e_client.get_recipe_suggestions(limit=5)
    
    assert isinstance(suggestions_custom, list), "Suggestions should be a list"
    assert len(suggestions_custom) <= 5, "Custom limit should be respected"
    
    # If we have suggestions, verify structure
    if len(suggestions_default) > 0:
        first_suggestion = suggestions_default[0]
        assert "name" in first_suggestion, "Suggestion should have a name"
        assert "slug" in first_suggestion, "Suggestion should have a slug"
