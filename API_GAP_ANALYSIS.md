# Mealie MCP Server - API Coverage Gap Analysis

Generated: 2025-12-20

## Current Implementation Status

✅ **64 tools implemented** covering:
- Recipes: 17 tools (CRUD, search, bulk operations, image management)
- Meal Plans: 13 tools (CRUD, search, batch operations, rules)
- Shopping: 11 tools (lists, items, recipe integration)
- Foods & Units: 8 tools (list, get, update, delete, merge)
- Organizers: 6 tools (categories, tags, tools - update/delete only)
- Parser: 2 tools (ingredient parsing)

📊 **API Coverage**: 64/247 endpoints (~26% coverage)

---

## HIGH PRIORITY - Missing Entire Features

### 1. Cookbooks (0/8 endpoints)
**Impact**: High - Essential for recipe organization workflow

Missing endpoints:
- `GET /api/households/cookbooks` - List all cookbooks
- `POST /api/households/cookbooks` - Create cookbook
- `GET /api/households/cookbooks/{id}` - Get cookbook
- `PUT /api/households/cookbooks/{id}` - Update cookbook
- `DELETE /api/households/cookbooks/{id}` - Delete cookbook
- `PUT /api/households/cookbooks` - Update many cookbooks

**Use Cases**:
- Organize recipes by theme (e.g., "Weeknight Dinners", "Batch Cooking", "Summer BBQ")
- Create meal planning collections
- Share curated recipe sets with household members

### 2. Recipe Comments (0/5 endpoints)
**Impact**: Medium-High - Valuable for recipe iteration and feedback

Missing endpoints:
- `GET /api/recipes/{slug}/comments` - Get recipe comments
- `POST /api/comments` - Add comment to recipe
- `GET /api/comments/{id}` - Get comment
- `PUT /api/comments/{id}` - Update comment
- `DELETE /api/comments/{id}` - Delete comment

**Use Cases**:
- Track recipe modifications ("Used 2 cups instead of 3")
- Record family feedback ("Kids loved it!")
- Note substitutions and improvements

### 3. Recipe Timeline Events (0/6 endpoints)
**Impact**: Medium - Useful for tracking recipe history

Missing endpoints:
- `GET /api/recipes/timeline/events` - List timeline events
- `POST /api/recipes/timeline/events` - Create timeline event
- `GET /api/recipes/timeline/events/{id}` - Get event
- `PUT /api/recipes/timeline/events/{id}` - Update event
- `DELETE /api/recipes/timeline/events/{id}` - Delete event
- `PUT /api/recipes/timeline/events/{id}/image` - Update event image

**Use Cases**:
- Track when recipes were made
- Analytics on cooking frequency
- Recipe popularity tracking

### 4. Recipe Actions (0/6 endpoints)
**Impact**: Medium - Automation for power users

Missing endpoints:
- `GET /api/households/recipe-actions` - List recipe actions
- `POST /api/households/recipe-actions` - Create recipe action
- `GET /api/households/recipe-actions/{id}` - Get action
- `PUT /api/households/recipe-actions/{id}` - Update action
- `DELETE /api/households/recipe-actions/{id}` - Delete action
- `POST /api/households/recipe-actions/{id}/trigger/{slug}` - Trigger action

**Use Cases**:
- Webhook triggers on recipe creation/update
- Automated workflows (e.g., add new recipes to specific cookbooks)
- Integration with external automation systems

---

## MEDIUM PRIORITY - Partial Implementation

### Organizers - Categories (Missing 3/7)
**Current**: Update and delete only

Missing endpoints:
- `GET /api/organizers/categories` - List all categories
- `POST /api/organizers/categories` - Create category
- `GET /api/organizers/categories/{id}` - Get category by ID

**Impact**: Limits ability to programmatically create new categories when importing recipes

### Organizers - Tags (Missing 3/7)
**Current**: Update and delete only

Missing endpoints:
- `GET /api/organizers/tags` - List all tags
- `POST /api/organizers/tags` - Create tag
- `GET /api/organizers/tags/{id}` - Get tag by ID

**Impact**: Cannot create tags during recipe import automation

### Organizers - Tools (Missing 3/6)
**Current**: Update and delete only

Missing endpoints:
- `GET /api/organizers/tools` - List all tools
- `POST /api/organizers/tools` - Create tool
- `GET /api/organizers/tools/{id}` - Get tool by ID

**Impact**: Cannot add new kitchen tools programmatically

### Foods (Missing 1/6)
**Current**: List, get, update, delete, merge

Missing endpoint:
- `POST /api/foods` - Create food

**Impact**: Cannot add new food items when importing recipes with novel ingredients

### Units (Missing 1/6)
**Current**: List, get, update, delete, merge

Missing endpoint:
- `POST /api/units` - Create unit

**Impact**: Cannot add new measurement units programmatically

### Shopping Lists (Missing 1/9)
**Current**: Create, get, delete, add items

Missing endpoint:
- `PUT /api/households/shopping/lists/{id}` - Update shopping list (name, etc.)

**Impact**: Cannot rename or modify shopping list metadata

---

## LOW PRIORITY - Advanced Features

### Recipe Exports (0/2)
- `GET /api/recipes/exports` - Get available export formats
- `GET /api/recipes/{slug}/exports` - Export recipe in specific format

**Use Cases**: Export recipes to PDF, JSON, other formats

### Recipe Sharing (0/4)
- `GET /api/shared/recipes` - List shared recipes
- `POST /api/shared/recipes` - Create recipe share link
- `GET /api/shared/recipes/{id}` - Get shared recipe
- `DELETE /api/shared/recipes/{id}` - Delete share link

**Use Cases**: Share recipes publicly via links

### Household Management (0/10+)
- `GET /api/households/self` - Get household info
- `GET /api/households/members` - Get household members
- `GET /api/households/preferences` - Get/update preferences
- `GET /api/households/statistics` - Get statistics

**Use Cases**: Household configuration and analytics

### Event Notifications (0/6)
Full CRUD for event notification management

**Use Cases**: Email/webhook notifications for household events

---

## NOT RECOMMENDED FOR IMPLEMENTATION

### Admin Endpoints (0/29)
- User management
- Group management
- Backup/restore
- System maintenance

**Reason**: Admin-only operations, not suitable for general MCP usage

---

## RECOMMENDED IMPLEMENTATION ORDER

### Phase 1: Complete Existing Categories (Estimated: 8 tools)
1. ✅ Categories CREATE + LIST + GET (3 tools)
2. ✅ Tags CREATE + LIST + GET (3 tools)
3. ✅ Tools CREATE + LIST + GET (2 tools)

**Why**: Completes organizer functionality, enables full recipe organization automation

### Phase 2: Essential Features (Estimated: 8 tools)
4. ✅ Cookbooks - Full CRUD (6 tools)
5. ✅ Foods CREATE (1 tool)
6. ✅ Units CREATE (1 tool)

**Why**: Cookbooks are essential for meal planning; foods/units needed for recipe imports

### Phase 3: Recipe Enhancement (Estimated: 5 tools)
7. ✅ Recipe Comments - Full CRUD (5 tools)

**Why**: Enhances recipe iteration and family feedback tracking

### Phase 4: Optional Advanced Features (Estimated: 12 tools)
8. Recipe Timeline Events (6 tools)
9. Recipe Actions (6 tools)

**Why**: Power user features for analytics and automation

---

## Implementation Effort Estimates

| Category | Tools | Effort | Priority |
|----------|-------|--------|----------|
| Organizers (complete) | 8 | Low | High |
| Cookbooks | 6 | Low-Medium | High |
| Foods/Units CREATE | 2 | Low | High |
| Recipe Comments | 5 | Low-Medium | Medium |
| Timeline Events | 6 | Medium | Low |
| Recipe Actions | 6 | Medium | Low |

**Total High Priority**: 16 tools (~2-3 days of work)
**Total Medium Priority**: 5 tools (~1 day)
**Total Low Priority**: 12 tools (~2-3 days)

---

## Notes

- All endpoints verified against live OpenAPI spec: https://recipe.vilo.network/openapi.json
- Coverage calculation: 64 implemented / 247 total = 26%
- Admin endpoints (29) excluded from coverage target
- Focus on household/recipe management endpoints for MCP use cases
