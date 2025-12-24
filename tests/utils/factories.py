"""Test data factories for generating realistic mock data.

This module provides factory classes for creating test data that matches
Mealie API schemas. Factories support both simple creation and customization
through builder patterns.

Usage - Simple:
    >>> recipe = RecipeFactory.create()
    >>> mealplan = MealPlanFactory.create_dinner()
    >>> shopping_list = ShoppingListFactory.with_items(3)

Usage - Customized:
    >>> recipe = RecipeFactory.create(
    ...     name="Custom Recipe",
    ...     tags=["Vegan", "Quick"],
    ...     recipeYield="6 servings"
    ... )

Usage - Batch:
    >>> recipes = RecipeFactory.create_batch(10)
    >>> mealplans = MealPlanFactory.create_week()
"""

from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any, Optional
import uuid


class RecipeFactory:
    """Factory for creating recipe test data.

    Provides methods for creating individual recipes, batches, and
    recipes with specific characteristics.
    """

    @staticmethod
    def create(
        slug: str = None,
        name: str = "Test Recipe",
        **overrides
    ) -> Dict[str, Any]:
        """Create a single recipe with optional customization.

        Args:
            slug: Recipe URL slug (auto-generated if not provided)
            name: Recipe name
            **overrides: Additional fields to override

        Returns:
            Recipe dictionary matching Mealie API schema

        Example:
            >>> recipe = RecipeFactory.create(name="Pasta", recipeYield="4 servings")
            >>> recipe["name"]
            'Pasta'
        """
        if slug is None:
            slug = name.lower().replace(" ", "-")

        recipe = {
            "id": str(uuid.uuid4()),
            "slug": slug,
            "name": name,
            "description": f"A delicious {name.lower()} recipe",
            "recipeYield": "4 servings",
            "totalTime": "45 minutes",
            "prepTime": "15 minutes",
            "cookTime": "30 minutes",
            "recipeIngredient": [
                "2 cups all-purpose flour",
                "1 tsp salt",
                "1/2 cup water",
                "2 tbsp olive oil"
            ],
            "recipeInstructions": [
                {"text": "Preheat oven to 350°F (175°C)"},
                {"text": "Mix dry ingredients in a bowl"},
                {"text": "Add wet ingredients and stir until combined"},
                {"text": "Bake for 30 minutes until golden brown"}
            ],
            "tags": [],
            "recipeCategory": [],
            "tools": [],
            "nutrition": {},
            "orgURL": None,
            "dateAdded": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "dateUpdated": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "groupId": str(uuid.uuid4())
        }
        recipe.update(overrides)
        return recipe

    @staticmethod
    def create_batch(count: int, **overrides) -> List[Dict[str, Any]]:
        """Create multiple recipes with sequential names.

        Args:
            count: Number of recipes to create
            **overrides: Common overrides for all recipes

        Returns:
            List of recipe dictionaries

        Example:
            >>> recipes = RecipeFactory.create_batch(5)
            >>> len(recipes)
            5
            >>> recipes[0]["name"]
            'Test Recipe 1'
        """
        return [
            RecipeFactory.create(
                name=f"Test Recipe {i+1}",
                slug=f"test-recipe-{i+1}",
                **overrides
            )
            for i in range(count)
        ]

    @staticmethod
    def with_tags(tags: List[str], **overrides) -> Dict[str, Any]:
        """Create a recipe with specific tags.

        Args:
            tags: List of tag names
            **overrides: Additional overrides

        Returns:
            Recipe with tags configured

        Example:
            >>> recipe = RecipeFactory.with_tags(["Vegan", "Quick", "Easy"])
            >>> len(recipe["tags"])
            3
        """
        tag_objects = [TagFactory.create(name=tag) for tag in tags]
        return RecipeFactory.create(tags=tag_objects, **overrides)

    @staticmethod
    def with_categories(categories: List[str], **overrides) -> Dict[str, Any]:
        """Create a recipe with specific categories.

        Args:
            categories: List of category names
            **overrides: Additional overrides

        Returns:
            Recipe with categories configured

        Example:
            >>> recipe = RecipeFactory.with_categories(["Dinner", "Italian"])
            >>> len(recipe["recipeCategory"])
            2
        """
        category_objects = [CategoryFactory.create(name=cat) for cat in categories]
        return RecipeFactory.create(recipeCategory=category_objects, **overrides)

    @staticmethod
    def with_full_details(**overrides) -> Dict[str, Any]:
        """Create a recipe with all fields populated.

        Returns:
            Comprehensive recipe with tags, categories, tools, and nutrition

        Example:
            >>> recipe = RecipeFactory.with_full_details()
            >>> len(recipe["tags"]) > 0
            True
            >>> "nutrition" in recipe
            True
        """
        return RecipeFactory.create(
            description="A comprehensive recipe with all details",
            recipeYield="6 servings",
            totalTime="1 hour 30 minutes",
            prepTime="30 minutes",
            cookTime="1 hour",
            recipeIngredient=[
                "2 cups all-purpose flour",
                "1 tsp baking powder",
                "1/2 tsp salt",
                "1 cup sugar",
                "2 large eggs",
                "1 cup milk",
                "1/2 cup vegetable oil"
            ],
            recipeInstructions=[
                {"text": "Preheat oven to 350°F"},
                {"text": "Mix dry ingredients"},
                {"text": "Beat eggs and sugar"},
                {"text": "Combine wet and dry ingredients"},
                {"text": "Bake for 45 minutes"}
            ],
            tags=[
                TagFactory.create(name="Vegan"),
                TagFactory.create(name="Quick")
            ],
            recipeCategory=[
                CategoryFactory.create(name="Dessert"),
                CategoryFactory.create(name="Baking")
            ],
            tools=[
                ToolFactory.create(name="Stand Mixer"),
                ToolFactory.create(name="Baking Pan")
            ],
            nutrition={
                "calories": "250",
                "fatContent": "10",
                "proteinContent": "5",
                "carbohydrateContent": "35"
            },
            **overrides
        )


class MealPlanFactory:
    """Factory for creating meal plan test data."""

    @staticmethod
    def create(
        meal_date: str = None,
        entry_type: str = "dinner",
        **overrides
    ) -> Dict[str, Any]:
        """Create a single meal plan entry.

        Args:
            meal_date: Date in YYYY-MM-DD format (defaults to today)
            entry_type: Type of meal (breakfast, lunch, dinner, side, snack)
            **overrides: Additional fields to override

        Returns:
            Meal plan dictionary

        Example:
            >>> mealplan = MealPlanFactory.create(entry_type="breakfast")
            >>> mealplan["entryType"]
            'breakfast'
        """
        if meal_date is None:
            meal_date = datetime.now(UTC).strftime("%Y-%m-%d")

        mealplan = {
            "id": str(uuid.uuid4()),
            "date": meal_date,
            "entryType": entry_type,
            "title": None,
            "text": None,
            "recipeId": None,
            "recipe": None,
            "groupId": str(uuid.uuid4()),
            "userId": str(uuid.uuid4())
        }
        mealplan.update(overrides)
        return mealplan

    @staticmethod
    def create_breakfast(meal_date: str = None, **overrides) -> Dict[str, Any]:
        """Create a breakfast meal plan entry."""
        return MealPlanFactory.create(meal_date=meal_date, entry_type="breakfast", **overrides)

    @staticmethod
    def create_lunch(meal_date: str = None, **overrides) -> Dict[str, Any]:
        """Create a lunch meal plan entry."""
        return MealPlanFactory.create(meal_date=meal_date, entry_type="lunch", **overrides)

    @staticmethod
    def create_dinner(meal_date: str = None, **overrides) -> Dict[str, Any]:
        """Create a dinner meal plan entry."""
        return MealPlanFactory.create(meal_date=meal_date, entry_type="dinner", **overrides)

    @staticmethod
    def with_recipe(recipe_id: str = None, **overrides) -> Dict[str, Any]:
        """Create a meal plan entry with a recipe attached.

        Args:
            recipe_id: Recipe ID to attach (auto-generated if not provided)
            **overrides: Additional overrides

        Returns:
            Meal plan with recipe configured

        Example:
            >>> mealplan = MealPlanFactory.with_recipe()
            >>> mealplan["recipeId"] is not None
            True
        """
        if recipe_id is None:
            recipe_id = str(uuid.uuid4())

        recipe = RecipeFactory.create(id=recipe_id)
        return MealPlanFactory.create(
            recipeId=recipe_id,
            recipe=recipe,
            **overrides
        )

    @staticmethod
    def create_day(meal_date: str = None) -> List[Dict[str, Any]]:
        """Create a full day of meal plans (breakfast, lunch, dinner).

        Args:
            meal_date: Date for the meals

        Returns:
            List of 3 meal plan entries

        Example:
            >>> day = MealPlanFactory.create_day("2025-12-25")
            >>> len(day)
            3
            >>> [m["entryType"] for m in day]
            ['breakfast', 'lunch', 'dinner']
        """
        return [
            MealPlanFactory.create_breakfast(meal_date=meal_date),
            MealPlanFactory.create_lunch(meal_date=meal_date),
            MealPlanFactory.create_dinner(meal_date=meal_date)
        ]

    @staticmethod
    def create_week(start_date: str = None) -> List[Dict[str, Any]]:
        """Create a week of meal plans (7 days, 3 meals each).

        Args:
            start_date: Starting date (defaults to today)

        Returns:
            List of 21 meal plan entries (7 days × 3 meals)

        Example:
            >>> week = MealPlanFactory.create_week()
            >>> len(week)
            21
        """
        if start_date is None:
            start_date = datetime.now(UTC).strftime("%Y-%m-%d")

        base_date = datetime.strptime(start_date, "%Y-%m-%d")
        mealplans = []

        for day_offset in range(7):
            date = (base_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            mealplans.extend(MealPlanFactory.create_day(date))

        return mealplans


class ShoppingListFactory:
    """Factory for creating shopping list test data."""

    @staticmethod
    def create(name: str = "Test Shopping List", **overrides) -> Dict[str, Any]:
        """Create a shopping list.

        Args:
            name: Shopping list name
            **overrides: Additional overrides

        Returns:
            Shopping list dictionary

        Example:
            >>> shopping_list = ShoppingListFactory.create(name="Grocery Run")
            >>> shopping_list["name"]
            'Grocery Run'
        """
        shopping_list = {
            "id": str(uuid.uuid4()),
            "name": name,
            "listItems": [],
            "groupId": str(uuid.uuid4())
        }
        shopping_list.update(overrides)
        return shopping_list

    @staticmethod
    def with_items(count: int, **overrides) -> Dict[str, Any]:
        """Create a shopping list with multiple items.

        Args:
            count: Number of items to add
            **overrides: Additional overrides for the list

        Returns:
            Shopping list with items

        Example:
            >>> shopping_list = ShoppingListFactory.with_items(5)
            >>> len(shopping_list["listItems"])
            5
        """
        items = [
            {
                "id": str(uuid.uuid4()),
                "note": f"Test item {i+1}",
                "checked": False,
                "quantity": 1.0,
                "shoppingListId": str(uuid.uuid4())
            }
            for i in range(count)
        ]
        return ShoppingListFactory.create(listItems=items, **overrides)

    @staticmethod
    def with_checked_items(total: int, checked: int, **overrides) -> Dict[str, Any]:
        """Create a shopping list with some checked items.

        Args:
            total: Total number of items
            checked: Number of items that are checked
            **overrides: Additional overrides

        Returns:
            Shopping list with mixed checked/unchecked items

        Example:
            >>> shopping_list = ShoppingListFactory.with_checked_items(total=10, checked=3)
            >>> checked_count = sum(1 for item in shopping_list["listItems"] if item["checked"])
            >>> checked_count
            3
        """
        items = []
        for i in range(total):
            items.append({
                "id": str(uuid.uuid4()),
                "note": f"Test item {i+1}",
                "checked": i < checked,
                "quantity": 1.0,
                "shoppingListId": str(uuid.uuid4())
            })
        return ShoppingListFactory.create(listItems=items, **overrides)


class TagFactory:
    """Factory for creating tag test data."""

    @staticmethod
    def create(name: str = "Test Tag", **overrides) -> Dict[str, Any]:
        """Create a tag.

        Args:
            name: Tag name
            **overrides: Additional overrides

        Returns:
            Tag dictionary

        Example:
            >>> tag = TagFactory.create(name="Vegan")
            >>> tag["slug"]
            'vegan'
        """
        tag = {
            "id": str(uuid.uuid4()),
            "name": name,
            "slug": name.lower().replace(" ", "-"),
            "groupId": str(uuid.uuid4())
        }
        tag.update(overrides)
        return tag

    @staticmethod
    def create_batch(names: List[str]) -> List[Dict[str, Any]]:
        """Create multiple tags from a list of names."""
        return [TagFactory.create(name=name) for name in names]


class CategoryFactory:
    """Factory for creating category test data."""

    @staticmethod
    def create(name: str = "Test Category", **overrides) -> Dict[str, Any]:
        """Create a category."""
        category = {
            "id": str(uuid.uuid4()),
            "name": name,
            "slug": name.lower().replace(" ", "-"),
            "groupId": str(uuid.uuid4())
        }
        category.update(overrides)
        return category

    @staticmethod
    def create_batch(names: List[str]) -> List[Dict[str, Any]]:
        """Create multiple categories from a list of names."""
        return [CategoryFactory.create(name=name) for name in names]


class ToolFactory:
    """Factory for creating kitchen tool test data."""

    @staticmethod
    def create(name: str = "Test Tool", **overrides) -> Dict[str, Any]:
        """Create a kitchen tool."""
        tool = {
            "id": str(uuid.uuid4()),
            "name": name,
            "slug": name.lower().replace(" ", "-"),
            "groupId": str(uuid.uuid4())
        }
        tool.update(overrides)
        return tool


class FoodFactory:
    """Factory for creating food test data."""

    @staticmethod
    def create(name: str = "Test Food", **overrides) -> Dict[str, Any]:
        """Create a food item."""
        food = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": f"Test {name}",
            "groupId": str(uuid.uuid4()),
            "labelId": None
        }
        food.update(overrides)
        return food


class UnitFactory:
    """Factory for creating unit test data."""

    @staticmethod
    def create(name: str = "cup", abbreviation: str = "c", **overrides) -> Dict[str, Any]:
        """Create a unit."""
        unit = {
            "id": str(uuid.uuid4()),
            "name": name,
            "abbreviation": abbreviation,
            "description": f"Test {name}",
            "groupId": str(uuid.uuid4())
        }
        unit.update(overrides)
        return unit


class CookbookFactory:
    """Factory for creating cookbook test data."""

    @staticmethod
    def create(name: str = "Test Cookbook", **overrides) -> Dict[str, Any]:
        """Create a cookbook."""
        cookbook = {
            "id": str(uuid.uuid4()),
            "name": name,
            "slug": name.lower().replace(" ", "-"),
            "description": "A test cookbook",
            "public": False,
            "groupId": str(uuid.uuid4()),
            "recipes": []
        }
        cookbook.update(overrides)
        return cookbook

    @staticmethod
    def with_recipes(count: int, **overrides) -> Dict[str, Any]:
        """Create a cookbook with multiple recipes."""
        recipes = RecipeFactory.create_batch(count)
        return CookbookFactory.create(recipes=recipes, **overrides)


class CommentFactory:
    """Factory for creating comment test data."""

    @staticmethod
    def create(
        recipe_id: str = None,
        text: str = "Great recipe!",
        **overrides
    ) -> Dict[str, Any]:
        """Create a comment."""
        if recipe_id is None:
            recipe_id = str(uuid.uuid4())

        comment = {
            "id": str(uuid.uuid4()),
            "recipeId": recipe_id,
            "text": text,
            "userId": str(uuid.uuid4()),
            "createdAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "updatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z")
        }
        comment.update(overrides)
        return comment


class TimelineEventFactory:
    """Factory for creating timeline event test data."""

    @staticmethod
    def create(
        recipe_id: str = None,
        subject: str = "Recipe made",
        **overrides
    ) -> Dict[str, Any]:
        """Create a timeline event."""
        if recipe_id is None:
            recipe_id = str(uuid.uuid4())

        event = {
            "id": str(uuid.uuid4()),
            "recipeId": recipe_id,
            "subject": subject,
            "eventType": "info",
            "eventMessage": "Test event message",
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "userId": str(uuid.uuid4())
        }
        event.update(overrides)
        return event


class ParsedIngredientFactory:
    """Factory for creating parsed ingredient test data."""

    @staticmethod
    def create(
        input_text: str = "2 cups flour",
        quantity: float = 2.0,
        unit: str = "cup",
        food: str = "flour",
        **overrides
    ) -> Dict[str, Any]:
        """Create a parsed ingredient."""
        parsed = {
            "input": input_text,
            "confidence": {
                "quantity": 0.95,
                "unit": 0.90,
                "food": 0.85,
                "average": 0.90
            },
            "ingredient": {
                "quantity": quantity,
                "unit": {"name": unit} if unit else None,
                "food": {"name": food} if food else None,
                "note": "",
                "display": input_text
            }
        }
        parsed.update(overrides)
        return parsed

    @staticmethod
    def create_batch(ingredient_strings: List[str]) -> List[Dict[str, Any]]:
        """Create multiple parsed ingredients from text strings.

        Example:
            >>> ingredients = ParsedIngredientFactory.create_batch([
            ...     "2 cups flour",
            ...     "1 tsp salt",
            ...     "1/2 cup butter"
            ... ])
        """
        parsed_list = []
        for text in ingredient_strings:
            # Simple parsing logic for demo purposes
            parts = text.split()
            quantity = float(parts[0]) if parts else 1.0
            unit = parts[1] if len(parts) > 1 else ""
            food = " ".join(parts[2:]) if len(parts) > 2 else "ingredient"

            parsed_list.append(
                ParsedIngredientFactory.create(
                    input_text=text,
                    quantity=quantity,
                    unit=unit,
                    food=food
                )
            )

        return parsed_list
