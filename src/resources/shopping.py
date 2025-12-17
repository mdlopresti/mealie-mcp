"""
Shopping List Resources for Mealie MCP Server

Provides shopping list information as MCP resources.
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


def get_shopping_lists() -> str:
    """
    Get all shopping lists from Mealie.

    URI: shopping://lists

    Returns:
        Formatted shopping lists with items, counts, and status
    """
    try:
        client = MealieClient()

        # Get all shopping lists
        response = client.get("/api/households/shopping/lists")

        client.close()

        # Format output
        output = ["# Shopping Lists", ""]

        # Handle paginated response
        shopping_lists = []
        if response:
            if isinstance(response, dict) and "items" in response:
                shopping_lists = response["items"]
            elif isinstance(response, list):
                shopping_lists = response
            else:
                shopping_lists = [response]

        if not shopping_lists:
            output.append("*No shopping lists found*")
            return "\n".join(output)

        output.append(f"**Total Lists**: {len(shopping_lists)}")
        output.append("")

        # Display each list
        for shopping_list in shopping_lists:
            list_name = shopping_list.get("name", "Unnamed List")
            list_id = shopping_list.get("id", "")

            output.append(f"## {list_name}")
            output.append("")

            # Metadata
            created_at = shopping_list.get("createdAt", "")
            updated_at = shopping_list.get("updateAt", "")

            if created_at:
                output.append(f"- **Created**: {created_at}")
            if updated_at:
                output.append(f"- **Last Updated**: {updated_at}")

            # Get items
            items = shopping_list.get("listItems", [])

            if items:
                output.append(f"- **Total Items**: {len(items)}")

                # Count checked vs unchecked
                checked_count = sum(1 for item in items if item.get("checked", False))
                unchecked_count = len(items) - checked_count

                output.append(f"- **Completed**: {checked_count}/{len(items)}")
                output.append("")

                # Display unchecked items first
                if unchecked_count > 0:
                    output.append("### To Buy")
                    output.append("")

                    for item in items:
                        if not item.get("checked", False):
                            display = item.get("display", "")
                            quantity = item.get("quantity", "")
                            unit = item.get("unit")
                            food = item.get("food")
                            note = item.get("note", "")

                            # Build item text
                            item_text = ""

                            if display:
                                # Use display if available
                                item_text = display
                            else:
                                # Build from components
                                parts = []
                                if quantity:
                                    parts.append(str(quantity))
                                if unit and isinstance(unit, dict):
                                    parts.append(unit.get("name", ""))
                                elif unit:
                                    parts.append(str(unit))
                                if food and isinstance(food, dict):
                                    parts.append(food.get("name", ""))
                                elif food:
                                    parts.append(str(food))

                                item_text = " ".join(parts) if parts else "Unknown item"

                            output.append(f"- [ ] {item_text}")

                            if note:
                                output.append(f"  - *{note}*")

                    output.append("")

                # Display checked items
                if checked_count > 0:
                    output.append("### Already Purchased")
                    output.append("")

                    for item in items:
                        if item.get("checked", False):
                            display = item.get("display", "")
                            quantity = item.get("quantity", "")
                            unit = item.get("unit")
                            food = item.get("food")
                            note = item.get("note", "")

                            # Build item text
                            item_text = ""

                            if display:
                                item_text = display
                            else:
                                parts = []
                                if quantity:
                                    parts.append(str(quantity))
                                if unit and isinstance(unit, dict):
                                    parts.append(unit.get("name", ""))
                                elif unit:
                                    parts.append(str(unit))
                                if food and isinstance(food, dict):
                                    parts.append(food.get("name", ""))
                                elif food:
                                    parts.append(str(food))

                                item_text = " ".join(parts) if parts else "Unknown item"

                            output.append(f"- [x] {item_text}")

                            if note:
                                output.append(f"  - *{note}*")

                    output.append("")
            else:
                output.append("- **Total Items**: 0")
                output.append("")
                output.append("*No items in this list*")
                output.append("")

        return "\n".join(output)

    except MealieAPIError as e:
        return f"Error fetching shopping lists: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


def get_shopping_list_detail(list_id: str) -> str:
    """
    Get detailed information about a specific shopping list.

    URI: shopping://{list_id}

    Args:
        list_id: Shopping list ID

    Returns:
        Formatted shopping list with all items and details
    """
    try:
        client = MealieClient()
        shopping_list = client.get(f"/api/households/shopping/lists/{list_id}")
        client.close()

        if not shopping_list:
            return f"Shopping list '{list_id}' not found"

        # Format output
        output = []

        # Header
        list_name = shopping_list.get("name", "Unnamed List")
        output.append(f"# {list_name}")
        output.append("")

        # Metadata
        created_at = shopping_list.get("createdAt", "")
        updated_at = shopping_list.get("updateAt", "")

        if created_at:
            output.append(f"**Created**: {created_at}")
        if updated_at:
            output.append(f"**Last Updated**: {updated_at}")

        output.append("")

        # Get items
        items = shopping_list.get("listItems", [])

        if items:
            # Count checked vs unchecked
            checked_count = sum(1 for item in items if item.get("checked", False))
            unchecked_count = len(items) - checked_count

            output.append(f"**Progress**: {checked_count}/{len(items)} items completed")
            output.append("")

            # Display unchecked items first
            if unchecked_count > 0:
                output.append("## To Buy")
                output.append("")

                for item in items:
                    if not item.get("checked", False):
                        display = item.get("display", "")
                        quantity = item.get("quantity", "")
                        unit = item.get("unit")
                        food = item.get("food")
                        note = item.get("note", "")

                        # Build item text
                        item_text = ""

                        if display:
                            item_text = display
                        else:
                            parts = []
                            if quantity:
                                parts.append(str(quantity))
                            if unit and isinstance(unit, dict):
                                parts.append(unit.get("name", ""))
                            elif unit:
                                parts.append(str(unit))
                            if food and isinstance(food, dict):
                                parts.append(food.get("name", ""))
                            elif food:
                                parts.append(str(food))

                            item_text = " ".join(parts) if parts else "Unknown item"

                        output.append(f"- [ ] {item_text}")

                        if note:
                            output.append(f"  - *{note}*")

                output.append("")

            # Display checked items
            if checked_count > 0:
                output.append("## Already Purchased")
                output.append("")

                for item in items:
                    if item.get("checked", False):
                        display = item.get("display", "")
                        quantity = item.get("quantity", "")
                        unit = item.get("unit")
                        food = item.get("food")
                        note = item.get("note", "")

                        # Build item text
                        item_text = ""

                        if display:
                            item_text = display
                        else:
                            parts = []
                            if quantity:
                                parts.append(str(quantity))
                            if unit and isinstance(unit, dict):
                                parts.append(unit.get("name", ""))
                            elif unit:
                                parts.append(str(unit))
                            if food and isinstance(food, dict):
                                parts.append(food.get("name", ""))
                            elif food:
                                parts.append(str(food))

                            item_text = " ".join(parts) if parts else "Unknown item"

                        output.append(f"- [x] {item_text}")

                        if note:
                            output.append(f"  - *{note}*")

                output.append("")
        else:
            output.append("*No items in this list*")
            output.append("")

        return "\n".join(output)

    except MealieAPIError as e:
        return f"Error fetching shopping list '{list_id}': {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


if __name__ == "__main__":
    """Test shopping list resources."""
    import sys
    from pathlib import Path

    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from dotenv import load_dotenv
    from client import MealieClient

    load_dotenv()

    print("Testing Shopping List Resources")
    print("=" * 70)
    print()

    # Test 1: Get all shopping lists
    print("TEST 1: Get All Shopping Lists")
    print("-" * 70)
    result = get_shopping_lists()
    print(result)
    print()
    print()

    # Test 2: Get shopping list detail (if any lists exist)
    print("TEST 2: Get Shopping List Detail")
    print("-" * 70)
    client = MealieClient()
    try:
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

        if shopping_lists and len(shopping_lists) > 0:
            test_list_id = shopping_lists[0].get("id", "")
            if test_list_id:
                print(f"Testing with list ID: {test_list_id}")
                print()
                result = get_shopping_list_detail(test_list_id)
                print(result)
            else:
                print("No shopping lists found to test with")
        else:
            print("No shopping lists found to test with")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
