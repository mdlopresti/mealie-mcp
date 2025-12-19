# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.11] - 2025-12-19

### Fixed
- More defensive null/None handling for unit/food IDs
- Use `.get("id")` and explicit None/empty string checks
- Ensures null IDs properly trigger string-based food/unit creation

## [1.4.10] - 2025-12-19

### Added
- Debug logging in recipes.py to show ingredients being constructed
- Debug logging in client.py to show exact JSON being sent to Mealie PUT request
- Logs go to stderr for visibility in Docker/MCP output

## [1.4.9] - 2025-12-19

### Fixed
- Combine v1.4.8 ID logic with full recipe approach: GET → modify → PUT
- Use PUT instead of PATCH to ensure proper validation
- Keeps v1.4.8's smart ID handling for existing vs new units/foods

## [1.4.8] - 2025-12-19

### Fixed
- **CRITICAL: Handle existing vs new units/foods differently**
- If unit/food HAS an ID (already exists in Mealie DB): send minimal dict with {id, name}
- If unit/food DOESN'T have an ID (new): send just the name string for Pydantic to create it
- This matches Mealie's expectation: existing entities need IDs, new ones use field validators
- Solves the "Expected 'id' to be provided for unit/food" ValueError at last!

## [1.4.7] - 2025-12-19

### Fixed
- `update_recipe_ingredients`: Send minimal PATCH payload (only recipeIngredient field) instead of full recipe object
- This allows Pydantic validation to run properly on the recipeIngredient field during API request deserialization
- Full recipe object bypass may have prevented field validators from executing correctly
- Combines with v1.4.6 string approach to trigger proper CreateIngredient* object creation

## [1.4.6] - 2025-12-18

### Fixed
- **CRITICAL: Send unit/food as STRINGS not DICTS** - Leverages Mealie's Pydantic field validators
- Mealie's `@field_validator("unit", mode="before")` converts strings to CreateIngredientUnit automatically
- Mealie's `@field_validator("food", mode="before")` converts strings to CreateIngredientFood automatically
- When sent as dicts, SQLAlchemy ORM validation in `auto_init.py:175` expects 'id' field (ValueError)
- Root cause identified from Mealie server logs showing "Expected 'id' to be provided for food/unit"
- Changed from `{"name": "cup"}` to just `"cup"` - Mealie handles the rest
- **This finally fixes the HTTP 500 ValueError when updating recipes with structured ingredients**

## [1.4.5] - 2025-12-18

### Fixed
- **CRITICAL: PATCH requires full recipe object** - GET recipe first, modify, then PATCH back
- Mealie's PATCH endpoint expects complete Recipe object, not partial updates
- Changed approach: GET → modify recipe_ingredient field → PATCH full object
- Reverted to camelCase `recipeIngredient` (API uses camelCase in JSON)
- Fixes HTTP 500 ValueError when updating recipes with structured ingredients

## [1.4.4] - 2025-12-18

### Fixed
- **CRITICAL: Use snake_case field name for recipe updates** - Changed `recipeIngredient` to `recipe_ingredient`
- Mealie Pydantic models use snake_case field names, not camelCase
- Fixes HTTP 500 ValueError when updating recipes with structured ingredients

## [1.4.3] - 2025-12-18

### Fixed
- **Structured ingredient validation errors** - Use CreateIngredient* schema (no id field)
- Drop id field from unit/food objects to use CreateIngredientUnit/CreateIngredientFood schema
- Avoids IngredientUnit/IngredientFood validation which requires read-only fields (created_at, updated_at, label)
- Mealie lookups existing units/foods by name instead of id
- Fixes HTTP 500 ValueError when updating recipes with structured ingredients

## [1.4.2] - 2025-12-18

### Fixed
- **Structured ingredient validation errors** - Use whitelist approach for unit/food fields
- Only pass essential fields to Mealie API: id, name, labelId
- Exclude metadata fields: createdAt, update_at, label object, aliases, etc.
- Fixes HTTP 500 ValidationError when updating recipes with structured ingredients

## [1.3.0] - 2025-12-18

### Added

#### Structured Ingredient Update Support (Phase 6)
- `mealie_recipes_update_structured_ingredients` - Update recipes with structured ingredients from parser output
- Bridges the gap between ingredient parsing (v1.2.0) and recipe updates
- Accepts parsed ingredient data and updates recipes with full structure (quantity, unit, food fields)

### Technical Details
- Added `patch()` method to MealieClient for PATCH requests
- Added `update_recipe_ingredients()` method to MealieClient
- Created `recipes_update_structured_ingredients()` in tools/recipes.py
- Handles conversion from parser output format to Mealie ingredient schema
- Supports both dict and string formats for unit/food fields
- Auto-generates display field if not provided

### Use Cases
- Convert text-only ingredients to structured format for better data management
- Import recipes with structured ingredient data
- Enable recipe scaling and unit conversions
- Improve shopping list generation with structured data

### Example Workflow
```python
# 1. Parse ingredients
parsed = mealie_parser_ingredients_batch(["2 cups flour", "1 tsp salt"])

# 2. Update recipe with structured data
mealie_recipes_update_structured_ingredients(
    slug="my-recipe",
    parsed_ingredients=parsed['parsed_ingredients']
)

# 3. Recipe now has quantity, unit, food fields populated
```

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

[1.3.0]: https://github.com/mdlopresti/mealie-mcp/releases/tag/v1.3.0
[1.2.0]: https://github.com/mdlopresti/mealie-mcp/releases/tag/v1.2.0
[1.1.0]: https://github.com/mdlopresti/mealie-mcp/releases/tag/v1.1.0
[1.0.0]: https://github.com/mdlopresti/mealie-mcp/releases/tag/v1.0.0
