# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Added recipe suggestions with 1 new MCP tool (Phase 1.3)
- Added `mealie_recipes_get_suggestions` tool to get personalized recipe suggestions based on user preferences and history
- Added `get_recipe_suggestions` method to MealieClient for fetching AI-powered recipe recommendations
- Added support for limiting the number of suggestions returned (default 10)
- Added 6 comprehensive unit tests for recipe suggestions
- Added 1 E2E test for recipe suggestions workflow
- Added 3 MCP tests for recipe suggestions tool registration and invocation

## [1.8.0] - 2025-12-23

### Added
- Added `mealie_categories_list` MCP tool to list all categories (#21)
- Added `mealie_categories_create` MCP tool to create new categories (#21)
- Added `mealie_categories_get` MCP tool to get category by ID (#21)
- Added `get_category` method to MealieClient for retrieving category details (#21)
- Added comprehensive test coverage for all category operations (#21)
- Added `mealie_tags_list` MCP tool to list all tags (#22)
- Added `mealie_tags_create` MCP tool to create new tags (#22)
- Added `mealie_tags_get` MCP tool to get tag by ID (#22)
- Added `get_tag` method to MealieClient for retrieving tag details (#22)
- Added comprehensive test coverage for all tag operations (#22)
- Added `mealie_tools_list` MCP tool to list all kitchen tools (#23)
- Added `mealie_tools_create` MCP tool to create new kitchen tools (#23)
- Added `mealie_tools_get` MCP tool to get kitchen tool by ID (#23)
- Added `create_tool` and `get_tool` methods to MealieClient (#23)
- Added comprehensive test coverage for all kitchen tool operations (#23)
- Added `mealie_foods_create` MCP tool to create new foods (#25)
- Added `create_food` method to MealieClient for creating food items (#25)
- Added comprehensive test coverage for food creation (#25)
- Added `mealie_units_create` MCP tool to create new units (#26)
- Enhanced `create_unit` method to MealieClient with description and abbreviation parameters (#26)
- Added comprehensive test coverage for unit creation (#26)
- Added complete cookbooks management with full CRUD operations (#24)
- Added `mealie_cookbooks_list`, `mealie_cookbooks_create`, `mealie_cookbooks_get`, `mealie_cookbooks_update`, and `mealie_cookbooks_delete` MCP tools (#24)
- Created `src/tools/cookbooks.py` with cookbook management functions (#24)
- Added `list_cookbooks`, `create_cookbook`, `get_cookbook`, `update_cookbook`, and `delete_cookbook` methods to MealieClient (#24)
- Added comprehensive test coverage for all cookbook operations (#24)
- Added recipe comments management with full CRUD operations (#27)
- Created `src/tools/comments.py` with 5 comment management functions (#27)
- Added `get_recipe_comments`, `create_comment`, `get_comment`, `update_comment`, and `delete_comment` methods to MealieClient (#27)
- Added 5 MCP tools for comment management: `mealie_comments_get_recipe`, `create`, `get`, `update`, `delete` (#27)
- Added comprehensive test coverage for all comment operations (#27)
- Added recipe timeline events management with full CRUD operations (#28)
- Created `src/tools/timeline.py` with 6 timeline event management functions (#28)
- Added `list_timeline_events`, `get_timeline_event`, `create_timeline_event`, `update_timeline_event`, `delete_timeline_event`, and `update_timeline_event_image` methods to MealieClient (#28)
- Added 6 MCP tools for timeline management: `mealie_timeline_list`, `create`, `get`, `update`, `delete`, `update_image` (#28)
- Added comprehensive test coverage for all timeline operations (#28)

### Impact
- Completes full CRUD functionality for all organizers (categories, tags, and kitchen tools)
- Enables automated recipe organization workflows with complete organizer management
- Allows programmatic category, tag, and tool management for bulk operations
- Enables programmatic creation of food items for recipe import workflows (#25)
- Enables programmatic creation of measurement units for recipe import workflows (#26)
- Enables cookbook management for organizing recipes into themed collections (#24)
- Supports meal planning workflows with cookbook-based recipe organization (#24)
- Enables tracking of when recipes were made and building cooking history analytics (#28)
- Supports recipe popularity tracking and visual timeline of cooking history (#28)
- Enables recipe iteration tracking through comments (#27)
- Supports collaborative recipe development with comment management (#27)
- Enables kitchen tool management during recipe imports
- Provides complete foundation for recipe organization automation

## [1.7.2] - 2025-12-21

### Fixed
- Fixed `mealie_foods_update` MCP tool wrapper to use `label_id` parameter instead of `label` (#17)
- Completed the fix from #16 by updating server.py to match the updated signature in client.py and foods.py

### Impact
- MCP tool now properly accepts `label_id` parameter for assigning labels to foods
- Resolves validation error when calling `mealie_foods_update` with label_id argument

## [1.7.1] - 2025-12-20

### Fixed
- Fixed `update_food` method to use PUT instead of PATCH (#16)
- Fixed `update_food` to use `label_id` parameter instead of `label` (#16)
- Fixed `update_food` to use correct API field `labelId` instead of `label` (#16)
- Implemented GET-then-PUT pattern in `update_food` to preserve all food fields (#16)
- Updated `foods_update` tool function to match new signature with `label_id` parameter (#16)

### Impact
- Enables programmatic label assignment to foods
- Supports shopping list organization by label category
- Enables bulk food categorization workflows
- Enables automated food organization

## [1.7.0] - 2025-12-20

### Added
- Comprehensive test suite expansion achieving 50% code coverage milestone
  - 307 new tests added (74 → 381 total passing tests)
  - Client API tests: 48 tests covering all MealieClient methods
  - Recipe tool tests: 36 tests for CRUD, bulk operations, error handling
  - Shopping tool tests: 35 tests for lists, items, meal plan generation
  - Mealplan tool tests: 34 tests for CRUD, rules, date-based queries
  - Foods/Units tests: 26 tests for management and merge operations
  - Organizers/Parser tests: 30 tests for categories, tags, tools, ingredient parsing
  - Error handling tests across all modules (MealieAPIError and unexpected exceptions)
  - Edge case tests for optional parameters and complex data structures
  - Shared test infrastructure (conftest.py) with fixtures and mock helpers

### Changed
- Improved overall code coverage from 15% to 50% (+35%, +879 lines covered)
- Module coverage improvements:
  - client.py: 36% → 79%
  - foods.py: 16% → 79%
  - mealplans.py: 62% → 78%
  - recipes.py: 72% → 77%
  - organizers.py: 68% → 87%
  - shopping.py: 54% → 67%
  - parser.py: 51% (maintained)

### Testing Infrastructure
- Established testing patterns using respx for HTTP mocking
- Implemented context manager mocking for MealieClient instances
- Created reusable test helpers and fixtures
- Focused on coverage-driven testing with practical assertions

## [1.6.9] - 2025-12-21

### Added
- Comprehensive test suite for client initialization and error parsing
  - 20 new tests for MealieClient basic functionality
  - Tests for environment variable configuration and URL building
  - Tests for error message parsing (422, 500, 409, 404)
  - Tests for MealieAPIError exception handling
  - Tests for context manager support

### Changed
- Improved code coverage from 14% to 15%
- client.py coverage improved from 32% to 36%
- Total test count increased from 54 to 74 tests

## [1.6.8] - 2025-12-21

### Added
- Support for clearing optional fields using `"__CLEAR__"` sentinel value (#4)
- `CLEAR_FIELD` constant in `tools/mealplans.py` for field clearing
- Comprehensive tests for field clearing in `tests/test_mealplan_clearing.py`
- Documentation for field clearing in tool docstrings and README

### Fixed
- Fixed inability to clear `recipe_id`, `title`, and `text` from meal plan entries (#4)
- Users can now remove recipe associations without deleting the entire entry
- Clearing fields sends `null` to API while omitting fields preserves existing values
- Maintains backward compatibility - omitted parameters still preserve existing values

## [1.6.7] - 2025-12-21

### Fixed
- **CRITICAL: Fix "Recipe already exists" error in mealie_recipes_create (#2)**
  - Root cause: `recipes_create` was creating tag/category objects without IDs
  - SQL integrity violations when tags/categories already existed in system
  - Applied same ID lookup pattern from `recipes_update` (fixed in v1.6.6)
  - Now uses shared utility functions to ensure consistent behavior

### Changed
- **Refactored tag/category resolution into shared utility functions**
  - Added `_resolve_tags()` helper function used by both create and update
  - Added `_resolve_categories()` helper function used by both create and update
  - Eliminated 66 lines of duplicate code between the two functions
  - Improved code maintainability and testability
  - Both functions now use identical logic for looking up/creating tags and categories

### Added
- Comprehensive unit tests for utility functions (18 test cases)
  - Test both REPLACE mode (recipes_create) and ADDITIVE mode (recipes_update)
  - Test handling of existing, new, and mixed tags/categories
  - Test duplicate detection, empty lists, paginated responses
  - Test error propagation from API calls

## [1.6.6] - 2025-12-19

### Fixed
- **MAJOR: SQL Integrity Error when updating recipes with tags/categories**
  - Fixed "Recipe already exists" error that was actually a SQL UNIQUE constraint violation
  - Root cause: Code created new tag/category objects without IDs, causing Mealie to try inserting duplicates
  - Previous fix (v1.6.5 PATCH approach) didn't work - both PUT and PATCH trigger same validation
  - Real solution: Look up existing tags/categories by name and use their full objects with IDs
  - For new tags/categories, create them via API first, then reference them by ID
  - Server logs showed: `ERROR SQL Integrity Error on recipe controller action`
  - This was the actual blocker preventing all recipe organization work

### Changed
- `mealie_recipes_update` now:
  1. Fetches all system tags/categories to build lookup table
  2. For each tag/category being added, checks if it exists in system
  3. If exists: uses the full object (with ID, groupId, name, slug)
  4. If new: calls `create_tag()` or `create_category()` first, then uses returned object
  5. Combines with existing recipe tags/categories and sends to API
- This matches how Mealie web UI works internally

## [1.6.5] - 2025-12-19

### Fixed
- **FAILED APPROACH: "Recipe already exists" error in mealie_recipes_update**
  - Attempted fix using PATCH instead of PUT for tag/category-only updates
  - This approach did not work - PATCH has same validation as PUT
  - See v1.6.6 for actual fix

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

[1.8.0]: https://github.com/mdlopresti/mealie-mcp/releases/tag/v1.8.0
[1.7.2]: https://github.com/mdlopresti/mealie-mcp/releases/tag/v1.7.2
[1.3.0]: https://github.com/mdlopresti/mealie-mcp/releases/tag/v1.3.0
[1.2.0]: https://github.com/mdlopresti/mealie-mcp/releases/tag/v1.2.0
[1.1.0]: https://github.com/mdlopresti/mealie-mcp/releases/tag/v1.1.0
[1.0.0]: https://github.com/mdlopresti/mealie-mcp/releases/tag/v1.0.0
