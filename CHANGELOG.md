# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-12-18

### Added

#### Ingredient Parser Tools (Phase 5)
- `mealie_parser_ingredient` - Parse single ingredient string to structured format (quantity, unit, food)
- `mealie_parser_ingredients_batch` - Parse multiple ingredient strings at once for efficiency

### Technical Details
- Added `parse_ingredient()` and `parse_ingredients_batch()` methods to MealieClient
- Created new `tools/parser.py` module with parser tool implementations
- Supports three parser types: "nlp" (default, best for most cases), "brute", and "openai"
- Returns structured data with quantity, unit, food name, and confidence scores
- Useful for converting natural language ingredient descriptions into structured recipe data

### Use Cases
- Parse ingredient lists when creating recipes from unstructured text
- Extract structured data from scraped recipes
- Validate ingredient formatting
- Analyze ingredient quantities and units

## [1.1.0] - 2025-12-17

### Added

#### Recipe CRUD Tools (Phase 4)
- `mealie_recipes_create` - Create a new recipe with name, ingredients, instructions, etc.
- `mealie_recipes_create_from_url` - Import a recipe by scraping a URL
- `mealie_recipes_update` - Update an existing recipe's fields
- `mealie_recipes_delete` - Delete a recipe by slug

### Notes
- Ingredients and instructions accept simple string arrays for ease of use
- Tags and categories are automatically created if they don't exist

## [1.0.0] - 2025-12-17

### Added

#### Recipe Tools
- `mealie_recipes_search` - Search recipes by name, tags, or categories
- `mealie_recipes_get` - Get full recipe details including ingredients and instructions
- `mealie_recipes_list` - List all recipes with pagination

#### Meal Planning Tools
- `mealie_mealplans_list` - List meal plans for a date range
- `mealie_mealplans_today` - Get today's meals
- `mealie_mealplans_get` - Get specific meal plan entry
- `mealie_mealplans_get_date` - Get meals for a specific date
- `mealie_mealplans_create` - Create meal plan entry
- `mealie_mealplans_update` - Update meal plan entry
- `mealie_mealplans_delete` - Delete meal plan entry
- `mealie_mealplans_random` - Get random meal suggestion

#### Shopping List Tools
- `mealie_shopping_lists_list` - List all shopping lists
- `mealie_shopping_lists_get` - Get shopping list with items
- `mealie_shopping_lists_create` - Create new shopping list
- `mealie_shopping_lists_delete` - Delete shopping list
- `mealie_shopping_items_add` - Add item to list
- `mealie_shopping_items_add_bulk` - Add multiple items at once
- `mealie_shopping_items_check` - Mark item checked/unchecked
- `mealie_shopping_items_delete` - Remove item from list
- `mealie_shopping_add_recipe` - Add recipe ingredients to list
- `mealie_shopping_generate_from_mealplan` - Generate shopping list from meal plan
- `mealie_shopping_clear_checked` - Clear all checked items

#### Resources
- `recipes://list` - Browse all recipes
- `recipes://{slug}` - View specific recipe
- `mealplans://current` - Current week's meal plan
- `mealplans://today` - Today's meals
- `mealplans://{date}` - Specific date's meals
- `shopping://lists` - All shopping lists
- `shopping://{list_id}` - Specific shopping list

#### Infrastructure
- Docker-based deployment
- GitHub Actions CI/CD for automated builds
- Published to GitHub Container Registry (ghcr.io)

[1.2.0]: https://github.com/mdlopresti/mealie-mcp/releases/tag/v1.2.0
[1.1.0]: https://github.com/mdlopresti/mealie-mcp/releases/tag/v1.1.0
[1.0.0]: https://github.com/mdlopresti/mealie-mcp/releases/tag/v1.0.0
