"""
Meal Plan Resources for Mealie MCP Server

Provides meal planning information as MCP resources.
"""

from datetime import date, timedelta
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


def get_current_mealplan() -> str:
    """
    Get the current week's meal plan.

    URI: mealplans://current

    Returns:
        Formatted meal plan showing each day's meals for the current week
    """
    try:
        client = MealieClient()

        # Calculate current week (Monday to Sunday)
        today = date.today()
        week_start = today - timedelta(days=today.weekday())  # Monday
        week_end = week_start + timedelta(days=6)  # Sunday

        # Get meal plans for the week
        response = client.get("/api/households/mealplans", params={
            "start_date": week_start.isoformat(),
            "end_date": week_end.isoformat(),
        })

        client.close()

        # Format output
        output = ["# Current Week's Meal Plan", ""]
        output.append(f"**Week of {week_start.strftime('%B %d, %Y')} - {week_end.strftime('%B %d, %Y')}**")
        output.append("")

        # Organize meals by date
        meals_by_date = {}
        if response and isinstance(response, list):
            for item in response:
                meal_date = item.get("date", "")
                if meal_date:
                    if meal_date not in meals_by_date:
                        meals_by_date[meal_date] = []
                    meals_by_date[meal_date].append(item)

        # Display each day
        current_day = week_start
        while current_day <= week_end:
            date_str = current_day.isoformat()
            day_name = current_day.strftime("%A, %B %d")

            # Mark today
            if current_day == today:
                output.append(f"## {day_name} **(TODAY)**")
            else:
                output.append(f"## {day_name}")

            output.append("")

            # Get meals for this day
            day_meals = meals_by_date.get(date_str, [])

            if day_meals:
                # Organize by entry type (breakfast, lunch, dinner, side)
                by_type = {}
                for meal in day_meals:
                    entry_type = meal.get("entryType", "meal").lower()
                    if entry_type not in by_type:
                        by_type[entry_type] = []
                    by_type[entry_type].append(meal)

                # Display in order
                for meal_type in ["breakfast", "lunch", "dinner", "side", "snack"]:
                    if meal_type in by_type:
                        type_label = meal_type.capitalize()
                        output.append(f"### {type_label}")
                        output.append("")

                        for meal in by_type[meal_type]:
                            recipe = meal.get("recipe")
                            if recipe:
                                if isinstance(recipe, dict):
                                    recipe_name = recipe.get("name", "Unknown")
                                    recipe_slug = recipe.get("slug", "")
                                    output.append(f"- **{recipe_name}** (`{recipe_slug}`)")
                                else:
                                    output.append(f"- {recipe}")

                            # Show note if present
                            note = meal.get("text")
                            if note:
                                output.append(f"  - *Note: {note}*")

                        output.append("")

                # Handle any other entry types
                other_types = [k for k in by_type.keys() if k not in ["breakfast", "lunch", "dinner", "side", "snack"]]
                for meal_type in other_types:
                    type_label = meal_type.capitalize()
                    output.append(f"### {type_label}")
                    output.append("")

                    for meal in by_type[meal_type]:
                        recipe = meal.get("recipe")
                        if recipe:
                            if isinstance(recipe, dict):
                                recipe_name = recipe.get("name", "Unknown")
                                recipe_slug = recipe.get("slug", "")
                                output.append(f"- **{recipe_name}** (`{recipe_slug}`)")
                            else:
                                output.append(f"- {recipe}")

                        note = meal.get("text")
                        if note:
                            output.append(f"  - *Note: {note}*")

                    output.append("")
            else:
                output.append("*No meals planned*")
                output.append("")

            current_day += timedelta(days=1)

        return "\n".join(output)

    except MealieAPIError as e:
        return f"Error fetching meal plan: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


def get_today_meals() -> str:
    """
    Get today's planned meals.

    URI: mealplans://today

    Returns:
        Today's breakfast, lunch, dinner, and sides
    """
    try:
        client = MealieClient()

        # Get today's date
        today = date.today()

        # Get meal plans for today
        response = client.get("/api/households/mealplans/today")

        client.close()

        # Format output
        output = [f"# Meals for {today.strftime('%A, %B %d, %Y')}", ""]

        if not response or (isinstance(response, list) and len(response) == 0):
            output.append("*No meals planned for today*")
            return "\n".join(output)

        # Ensure response is a list
        if not isinstance(response, list):
            response = [response]

        # Organize by entry type
        by_type = {}
        for meal in response:
            entry_type = meal.get("entryType", "meal").lower()
            if entry_type not in by_type:
                by_type[entry_type] = []
            by_type[entry_type].append(meal)

        # Display in order
        for meal_type in ["breakfast", "lunch", "dinner", "side", "snack"]:
            if meal_type in by_type:
                type_label = meal_type.capitalize()
                output.append(f"## {type_label}")
                output.append("")

                for meal in by_type[meal_type]:
                    recipe = meal.get("recipe")
                    if recipe:
                        if isinstance(recipe, dict):
                            recipe_name = recipe.get("name", "Unknown")
                            recipe_slug = recipe.get("slug", "")
                            description = recipe.get("description", "")

                            output.append(f"### {recipe_name}")
                            output.append("")

                            if description:
                                output.append(f"*{description}*")
                                output.append("")

                            # Show prep/cook times if available
                            prep_time = recipe.get("prepTime")
                            cook_time = recipe.get("performTime")
                            total_time = recipe.get("totalTime")

                            if prep_time or cook_time or total_time:
                                output.append("**Timing:**")
                                if prep_time:
                                    output.append(f"- Prep: {prep_time}")
                                if cook_time:
                                    output.append(f"- Cook: {cook_time}")
                                if total_time:
                                    output.append(f"- Total: {total_time}")
                                output.append("")

                            output.append(f"*Recipe slug: `{recipe_slug}`*")
                        else:
                            output.append(f"- {recipe}")

                    # Show note if present
                    note = meal.get("text")
                    if note:
                        output.append(f"**Note:** {note}")

                    output.append("")

        # Handle any other entry types
        other_types = [k for k in by_type.keys() if k not in ["breakfast", "lunch", "dinner", "side", "snack"]]
        for meal_type in other_types:
            type_label = meal_type.capitalize()
            output.append(f"## {type_label}")
            output.append("")

            for meal in by_type[meal_type]:
                recipe = meal.get("recipe")
                if recipe:
                    if isinstance(recipe, dict):
                        recipe_name = recipe.get("name", "Unknown")
                        recipe_slug = recipe.get("slug", "")
                        output.append(f"### {recipe_name}")
                        output.append("")
                        output.append(f"*Recipe slug: `{recipe_slug}`*")
                    else:
                        output.append(f"- {recipe}")

                note = meal.get("text")
                if note:
                    output.append(f"**Note:** {note}")

                output.append("")

        return "\n".join(output)

    except MealieAPIError as e:
        return f"Error fetching today's meals: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


if __name__ == "__main__":
    """Test meal plan resources."""
    import sys
    from pathlib import Path

    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from dotenv import load_dotenv

    load_dotenv()

    print("Testing Meal Plan Resources")
    print("=" * 70)
    print()

    # Test 1: Get current week's meal plan
    print("TEST 1: Get Current Week's Meal Plan")
    print("-" * 70)
    result = get_current_mealplan()
    print(result)
    print()
    print()

    # Test 2: Get today's meals
    print("TEST 2: Get Today's Meals")
    print("-" * 70)
    result = get_today_meals()
    print(result)
    print()
