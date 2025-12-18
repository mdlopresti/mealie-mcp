"""
Parser tools for Mealie MCP server.

Provides tools for parsing ingredient strings into structured format with
quantity, unit, and food components.
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


def parser_ingredient(ingredient: str, parser: str = "nlp") -> str:
    """Parse a single ingredient string to structured format.

    Args:
        ingredient: The ingredient string to parse (e.g., "2 cups flour", "1 tsp salt")
        parser: Parser type - "nlp" (default), "brute", or "openai"

    Returns:
        JSON string with parsed ingredient structure including:
        - input: Original ingredient text
        - confidence: Confidence scores for parsed components
        - ingredient: Structured ingredient with quantity, unit, food, display
    """
    try:
        with MealieClient() as client:
            # Parse the ingredient
            response = client.parse_ingredient(ingredient=ingredient, parser=parser)

            # Return the parsed ingredient
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


def parser_ingredients_batch(ingredients: list[str], parser: str = "nlp") -> str:
    """Parse multiple ingredient strings to structured format.

    Args:
        ingredients: List of ingredient strings to parse
        parser: Parser type - "nlp" (default), "brute", or "openai"

    Returns:
        JSON string with array of parsed ingredients, each containing:
        - input: Original ingredient text
        - confidence: Confidence scores for parsed components
        - ingredient: Structured ingredient with quantity, unit, food, display
    """
    try:
        with MealieClient() as client:
            # Parse all ingredients
            response = client.parse_ingredients_batch(ingredients=ingredients, parser=parser)

            # Return the parsed ingredients array
            result = {
                "count": len(response) if isinstance(response, list) else 0,
                "parsed_ingredients": response
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


if __name__ == "__main__":
    """
    Test the parser tools against the live Mealie instance.
    """
    from dotenv import load_dotenv

    print("Testing Mealie Parser Tools...")
    print("=" * 60)

    # Load environment variables
    load_dotenv()

    # Test 1: Parse single ingredient
    print("\n1. Testing parser_ingredient with '2 cups flour'...")
    print("-" * 60)
    result1 = parser_ingredient("2 cups flour")
    print(result1)

    # Test 2: Parse single ingredient with different format
    print("\n2. Testing parser_ingredient with '1 tsp salt'...")
    print("-" * 60)
    result2 = parser_ingredient("1 tsp salt")
    print(result2)

    # Test 3: Parse batch of ingredients
    print("\n3. Testing parser_ingredients_batch with multiple ingredients...")
    print("-" * 60)
    test_ingredients = [
        "2 cups flour",
        "1 tsp salt",
        "1/2 cup butter",
        "3 large eggs"
    ]
    result3 = parser_ingredients_batch(test_ingredients)
    print(result3)

    # Test 4: Test with different parser type
    print("\n4. Testing parser_ingredient with 'brute' parser...")
    print("-" * 60)
    result4 = parser_ingredient("2 cups flour", parser="brute")
    print(result4)

    print("\n" + "=" * 60)
    print("All tests completed!")
