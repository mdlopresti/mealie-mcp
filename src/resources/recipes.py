"""
Recipe Resources for Mealie MCP Server

Provides recipe information as MCP resources.
"""

from typing import Optional

# Handle imports for both module and script execution
try:
    from ..client import MealieClient, MealieAPIError
except ImportError:
    # Running as a script, use absolute imports
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from client import MealieClient, MealieAPIError


def get_recipes_list() -> str:
    """
    Get a summary of all recipes in Mealie.

    URI: recipes://list

    Returns:
        Formatted text with recipe names, slugs, tags, and categories
    """
    try:
        client = MealieClient()

        # Get all recipes (paginate if necessary)
        all_recipes = []
        page = 1
        per_page = 100

        while True:
            response = client.get("/api/recipes", params={
                "page": page,
                "perPage": per_page,
                "orderBy": "name",
                "orderDirection": "asc"
            })

            if not response or "items" not in response:
                break

            recipes = response["items"]
            if not recipes:
                break

            all_recipes.extend(recipes)

            # Check if there are more pages
            total = response.get("total", 0)
            if len(all_recipes) >= total:
                break

            page += 1

        client.close()

        # Organize recipes by category
        by_category = {}
        uncategorized = []

        for recipe in all_recipes:
            category = recipe.get("recipeCategory")
            if category:
                if isinstance(category, list):
                    category = category[0] if category else "Uncategorized"
                # Handle dict category (convert to string)
                if isinstance(category, dict):
                    category = category.get("name", "Uncategorized")
                # Ensure category is a string
                category_str = str(category)
                if category_str not in by_category:
                    by_category[category_str] = []
                by_category[category_str].append(recipe)
            else:
                uncategorized.append(recipe)

        # Format output
        output = ["# Recipes in Mealie", ""]
        output.append(f"**Total Recipes**: {len(all_recipes)}")
        output.append("")

        # List by category
        for category in sorted(by_category.keys()):
            recipes = by_category[category]
            output.append(f"## {category} ({len(recipes)} recipes)")
            output.append("")

            for recipe in recipes:
                name = recipe.get("name", "Unknown")
                slug = recipe.get("slug", "")
                tags = recipe.get("tags", [])

                # Format tags
                tag_str = ""
                if tags:
                    if isinstance(tags, list):
                        tag_names = [t.get("name", str(t)) if isinstance(t, dict) else str(t) for t in tags]
                        tag_str = f" [{', '.join(tag_names)}]"

                output.append(f"- **{name}** (`{slug}`){tag_str}")

            output.append("")

        # Add uncategorized
        if uncategorized:
            output.append(f"## Uncategorized ({len(uncategorized)} recipes)")
            output.append("")

            for recipe in uncategorized:
                name = recipe.get("name", "Unknown")
                slug = recipe.get("slug", "")
                tags = recipe.get("tags", [])

                tag_str = ""
                if tags:
                    if isinstance(tags, list):
                        tag_names = [t.get("name", str(t)) if isinstance(t, dict) else str(t) for t in tags]
                        tag_str = f" [{', '.join(tag_names)}]"

                output.append(f"- **{name}** (`{slug}`){tag_str}")

            output.append("")

        return "\n".join(output)

    except MealieAPIError as e:
        return f"Error fetching recipes: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


def get_recipe_detail(slug: str) -> str:
    """
    Get detailed information about a specific recipe.

    URI: recipes://{slug}

    Args:
        slug: Recipe slug identifier

    Returns:
        Formatted recipe with ingredients, instructions, and nutrition
    """
    try:
        client = MealieClient()
        recipe = client.get(f"/api/recipes/{slug}")
        client.close()

        if not recipe:
            return f"Recipe '{slug}' not found"

        # Format output
        output = []

        # Header
        name = recipe.get("name", "Unknown Recipe")
        output.append(f"# {name}")
        output.append("")

        # Metadata
        description = recipe.get("description", "")
        if description:
            output.append(f"*{description}*")
            output.append("")

        # Basic info
        output.append("## Information")
        output.append("")

        category = recipe.get("recipeCategory")
        if category:
            if isinstance(category, list):
                category = ", ".join(category)
            output.append(f"- **Category**: {category}")

        tags = recipe.get("tags", [])
        if tags:
            if isinstance(tags, list):
                tag_names = [t.get("name", str(t)) if isinstance(t, dict) else str(t) for t in tags]
                output.append(f"- **Tags**: {', '.join(tag_names)}")

        yield_amount = recipe.get("recipeYield")
        if yield_amount:
            output.append(f"- **Yield**: {yield_amount}")

        total_time = recipe.get("totalTime")
        if total_time:
            output.append(f"- **Total Time**: {total_time}")

        prep_time = recipe.get("prepTime")
        if prep_time:
            output.append(f"- **Prep Time**: {prep_time}")

        perform_time = recipe.get("performTime")
        if perform_time:
            output.append(f"- **Cook Time**: {perform_time}")

        output.append("")

        # Ingredients
        ingredients = recipe.get("recipeIngredient", [])
        if ingredients:
            output.append("## Ingredients")
            output.append("")

            for ingredient in ingredients:
                if isinstance(ingredient, dict):
                    # Structured ingredient
                    quantity = ingredient.get("quantity", "")
                    unit = ingredient.get("unit", {})
                    if isinstance(unit, dict):
                        unit = unit.get("name", "")
                    food = ingredient.get("food", {})
                    if isinstance(food, dict):
                        food = food.get("name", "")
                    note = ingredient.get("note", "")

                    line = f"- {quantity} {unit} {food}".strip()
                    if note:
                        line += f" ({note})"
                    output.append(line)
                else:
                    # Simple string ingredient
                    output.append(f"- {ingredient}")

            output.append("")

        # Instructions
        instructions = recipe.get("recipeInstructions", [])
        if instructions:
            output.append("## Instructions")
            output.append("")

            for i, instruction in enumerate(instructions, 1):
                if isinstance(instruction, dict):
                    text = instruction.get("text", "")
                    title = instruction.get("title", "")

                    if title:
                        output.append(f"### Step {i}: {title}")
                        output.append("")
                    else:
                        output.append(f"### Step {i}")
                        output.append("")

                    output.append(text)
                else:
                    output.append(f"{i}. {instruction}")

                output.append("")

        # Nutrition
        nutrition = recipe.get("nutrition")
        if nutrition and isinstance(nutrition, dict):
            output.append("## Nutrition")
            output.append("")

            calories = nutrition.get("calories")
            if calories:
                output.append(f"- **Calories**: {calories}")

            protein = nutrition.get("proteinContent")
            if protein:
                output.append(f"- **Protein**: {protein}")

            carbs = nutrition.get("carbohydrateContent")
            if carbs:
                output.append(f"- **Carbohydrates**: {carbs}")

            fat = nutrition.get("fatContent")
            if fat:
                output.append(f"- **Fat**: {fat}")

            fiber = nutrition.get("fiberContent")
            if fiber:
                output.append(f"- **Fiber**: {fiber}")

            sodium = nutrition.get("sodiumContent")
            if sodium:
                output.append(f"- **Sodium**: {sodium}")

            output.append("")

        # Notes
        notes = recipe.get("notes", [])
        if notes:
            output.append("## Notes")
            output.append("")

            for note in notes:
                if isinstance(note, dict):
                    title = note.get("title", "")
                    text = note.get("text", "")

                    if title:
                        output.append(f"### {title}")
                        output.append("")

                    output.append(text)
                else:
                    output.append(note)

                output.append("")

        # Source
        recipe_url = recipe.get("orgURL")
        if recipe_url:
            output.append("## Source")
            output.append("")
            output.append(f"[Original Recipe]({recipe_url})")
            output.append("")

        return "\n".join(output)

    except MealieAPIError as e:
        return f"Error fetching recipe '{slug}': {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


if __name__ == "__main__":
    """Test recipe resources."""
    import sys
    from pathlib import Path

    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from dotenv import load_dotenv
    from client import MealieClient

    load_dotenv()

    print("Testing Recipe Resources")
    print("=" * 70)
    print()

    # Test 1: Get recipes list
    print("TEST 1: Get Recipes List")
    print("-" * 70)
    result = get_recipes_list()
    print(result)
    print()

    # Test 2: Get recipe detail (you'll need to update this with an actual slug)
    print("TEST 2: Get Recipe Detail")
    print("-" * 70)
    # Get the first recipe slug from the list for testing
    client = MealieClient()
    try:
        response = client.get("/api/recipes", params={"page": 1, "perPage": 1})
        if response and "items" in response and response["items"]:
            test_slug = response["items"][0].get("slug", "")
            if test_slug:
                print(f"Testing with recipe slug: {test_slug}")
                print()
                result = get_recipe_detail(test_slug)
                print(result)
            else:
                print("No recipes found to test with")
        else:
            print("No recipes found to test with")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
