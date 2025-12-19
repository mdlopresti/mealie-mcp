# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.4] - 2025-12-19

### Fixed
- **Critical: Bulk operations missing ID validation**
  - Fixed `mealie_recipes_bulk_tag` and `mealie_recipes_bulk_categorize` failing with "Field required: id" error
  - Root cause: Mealie API requires all tags/categories to have IDs - can't create new ones via bulk actions
  - Solution: Automatically create missing tags/categories before bulk assignment
  - Bulk operations now work seamlessly with both existing and new tags/categories

### Added
- `create_tag(name)` method to MealieClient - Creates new tags on demand
- `create_category(name)` method to MealieClient - Creates new categories on demand

## [1.6.3] - 2025-12-19

### Fixed
- **Critical: Bulk operations pagination bug**
  - Fixed `mealie_recipes_bulk_tag` and `mealie_recipes_bulk_categorize` failing with "string indices must be integers" error
  - Root cause: Mealie API returns paginated responses `{"items": [...], "page": 1, ...}` but code expected direct arrays
  - Bulk operations were iterating over dict keys ("page", "per_page", etc.) instead of the items array
  - Solution: Extract `items` key from paginated responses before processing
  - Now properly handles both paginated and non-paginated responses

- **JSON parsing error handling**
  - Improved error reporting when API returns non-JSON responses
  - Changed silent fallback to text into explicit error with response preview
  - Helps diagnose API issues instead of returning strings that cause downstream errors

## [1.6.2] - 2025-12-19

### Fixed
- **Critical: `mealie_recipes_update` "Recipe already exists" bug**
  - Fixed issue where updating any recipe would fail with "Recipe already exists" error
  - Root cause: Recipe name was being sent in update payload, triggering Mealie's uniqueness check
  - Solution: Changed tags and categories to ADDITIVE behavior (adds to existing instead of replacing)
  - Properly handles slug to avoid conflicts
  - Now successfully updates recipes without name collision errors

- **Bulk operations validation errors**
  - Fixed `mealie_recipes_bulk_tag` - Now converts tag names to proper objects before sending to API
  - Fixed `mealie_recipes_bulk_categorize` - Now converts category names to proper objects before sending to API
  - Root cause: Mealie API expects dict objects with {id, name, slug} but tools were sending string arrays
  - Solution: Added helper methods to list and look up existing tags/categories, create proper object format

### Added
- `list_categories()` method to MealieClient - Lists all available categories
- `list_tags()` method to MealieClient - Lists all available tags
- `list_tools()` method to MealieClient - Lists all available tools

### Changed
- **Breaking**: `mealie_recipes_update` tags and categories parameters now use ADDITIVE behavior
  - Previous: tags/categories replaced existing values
  - New: tags/categories are added to existing values (no duplicates)
  - This prevents accidental data loss and aligns with expected bulk operations behavior

## [1.6.1] - 2025-12-19

### Added
- **Recipe Image Upload from URL** - `mealie_recipes_upload_image_from_url(slug, image_url)`
  - Downloads image from provided URL and uploads to existing recipe
  - Automatic image format detection (jpg, png, webp)
  - Mealie handles resizing and optimization automatically
  - Enables easy image addition without manual download/upload workflow

### Technical Implementation
- Added `upload_recipe_image_from_url()` method to MealieClient
- Uses multipart/form-data with `PUT /api/recipes/{slug}/image` endpoint
- Integrated httpx for image download with proper error handling
- Added `recipes_upload_image_from_url()` tool in tools/recipes.py
- Exposed as `mealie_recipes_upload_image_from_url` MCP tool

### Use Cases
- Add images to recipes imported from plain text or JSON
- Update recipe images from authoritative sources (e.g., Anova Culinary)
- Batch image updates for recipe collections
- Preserve visual context from original recipe sources

## [1.6.0] - 2025-12-19

### Added

#### High-Priority Recipe Management Features
- **Recipe Duplication** - `mealie_recipes_duplicate(slug, new_name?)`
  - Create variations of existing recipes
  - Useful for meal prep adaptations and recipe experimentation

- **Last Made Tracking** - `mealie_recipes_update_last_made(slug, timestamp?)`
  - Track when recipes were last prepared
  - Enables meal rotation planning and freshness tracking

- **Bulk URL Import** - `mealie_recipes_create_from_urls_bulk(urls, include_tags)`
  - Import multiple recipes from URLs at once
  - More efficient than sequential one-at-a-time imports

- **Bulk Recipe Actions** - Batch operations for recipe management:
  - `mealie_recipes_bulk_tag(recipe_ids, tags)` - Add tags to multiple recipes
  - `mealie_recipes_bulk_categorize(recipe_ids, categories)` - Categorize multiple recipes
  - `mealie_recipes_bulk_delete(recipe_ids)` - Delete multiple recipes at once
  - `mealie_recipes_bulk_export(recipe_ids, format)` - Export recipe batches
  - `mealie_recipes_bulk_update_settings(recipe_ids, settings)` - Update settings across recipes

#### Meal Plan Rules (Automated Planning)
- **Full CRUD for Meal Plan Rules** - `/api/households/mealplans/rules` endpoints:
  - `mealie_mealplan_rules_list()` - List all meal planning rules
  - `mealie_mealplan_rules_get(rule_id)` - Get specific rule details
  - `mealie_mealplan_rules_create(name, entry_type, tags?, categories?)` - Create automation rules
  - `mealie_mealplan_rules_update(rule_id, ...)` - Update existing rules
  - `mealie_mealplan_rules_delete(rule_id)` - Delete rules
- Enables automated meal plan generation with preference-based filtering

#### Foods & Units Management
- **Foods Management** - Complete CRUD operations for ingredient database:
  - `mealie_foods_list(page, per_page)` - Browse all foods with pagination
  - `mealie_foods_get(food_id)` - Get food details
  - `mealie_foods_update(food_id, name?, description?, label?)` - Update food entries
  - `mealie_foods_delete(food_id)` - Delete foods
  - `mealie_foods_merge(from_food_id, to_food_id)` - Merge duplicate foods across recipes

- **Units Management** - Complete CRUD operations for measurement units:
  - `mealie_units_list(page, per_page)` - Browse all units with pagination
  - `mealie_units_get(unit_id)` - Get unit details
  - `mealie_units_update(unit_id, name?, description?, abbreviation?)` - Update units
  - `mealie_units_delete(unit_id)` - Delete units
  - `mealie_units_merge(from_unit_id, to_unit_id)` - Merge duplicate units across recipes

#### Organizers Management (Categories, Tags, Tools)
- **Categories Management**:
  - `mealie_categories_update(category_id, name?, slug?)` - Update category details
  - `mealie_categories_delete(category_id)` - Delete categories

- **Tags Management**:
  - `mealie_tags_update(tag_id, name?, slug?)` - Update tag details
  - `mealie_tags_delete(tag_id)` - Delete tags

- **Tools Management**:
  - `mealie_tools_update(tool_id, name?, slug?)` - Update cooking tool details
  - `mealie_tools_delete(tool_id)` - Delete tools

#### Shopping List Enhancements
- **Recipe Ingredient Removal** - `mealie_shopping_delete_recipe_from_list(item_id, recipe_id)`
  - Remove specific recipe's ingredients from shopping list
  - Better control over shopping list composition

#### Experimental Features
- **Recipe from Image (AI)** - `mealie_recipes_create_from_image(image_data, extension)`
  - AI-generated recipes from photos (experimental)
  - Requires Mealie instance with AI features enabled

### Technical Implementation
- Added 46 new MCP tools across 9 feature categories
- Created new tool modules: `tools/foods.py`, `tools/organizers.py`
- Extended `tools/recipes.py`, `tools/mealplans.py`, `tools/shopping.py`
- Added 24 new client methods to `client.py`
- Comprehensive error handling and validation across all new endpoints

### Use Cases Enabled
- **Data Quality**: Merge duplicate foods/units, clean up organizers
- **Bulk Operations**: Tag/categorize/delete/export recipes in batches
- **Automation**: Set up meal planning rules for automated suggestions
- **Workflow Efficiency**: Duplicate recipes for variations, track last made dates
- **Import Scale**: Import multiple recipe URLs simultaneously

## [1.5.0] - 2025-12-19

### Added
- **orgURL and image support** in `mealie_recipes_update` tool
- New `org_url` parameter to set/update original recipe URL
- New `image` parameter to set/update recipe image identifier
- Enables preserving source attribution when modifying recipes

### Changed
- `recipes_update()` function signature updated with `org_url` and `image` parameters
- `mealie_recipes_update()` MCP tool now exposes orgURL and image fields

## [1.4.15] - 2025-12-19

### Fixed
- **Pre-create missing foods/units** before updating recipe ingredients
- Added `create_food()` and `create_unit()` client methods
- Ensures all unit/food references have IDs to avoid SQLAlchemy auto_init ValueError
- Resolves "Expected 'id' to be provided for unit/food" errors with new ingredients

### Changed
- Send unit/food as `{id, name}` dicts when IDs are available
- Fall back to string format only if ID is missing after pre-creation

## [1.4.14] - 2025-12-19

### Changed
- **Use PATCH instead of GET→PUT** for updating recipe ingredients
- Send only `recipeIngredient` field in minimal PATCH payload
- Avoids SQLAlchemy auto_init issues with full recipe PUT approach

## [1.4.13] - 2025-12-19

### Added
- Include `debug_ingredients_sent` in both success and error responses
- Shows exact ingredient structure sent to Mealie for troubleshooting

## [1.4.12] - 2025-12-19

### Fixed
- **ALWAYS send unit/food as strings** (just the name), never as dicts
- Simpler approach: let Mealie's Pydantic validators handle create-or-reference
- Eliminates complex ID checking that wasn't working reliably

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
