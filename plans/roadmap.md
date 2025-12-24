# Roadmap

## Batch 1 (Current - High-Value User Features)

### Phase 1.1: Recipe Ratings Management
- **Status:** ⚪ Not Started
- **Tasks:**
  - [ ] Add `rate_recipe`, `get_user_ratings`, `get_recipe_rating` to MealieClient
  - [ ] Create `ratings_set`, `ratings_list`, `ratings_get_recipe` in `tools/recipes.py`
  - [ ] Register 3 MCP tools: `mealie_ratings_set`, `mealie_ratings_list`, `mealie_ratings_get_recipe`
  - [ ] Write unit tests (mock-based)
  - [ ] Write E2E tests (live API)
  - [ ] Write MCP tests (tool invocation)
  - [ ] Update CHANGELOG.md
- **Effort:** M
- **Done When:** All tests passing (unit, E2E, MCP), PR merged
- **Plan:** [High-Value Features Plan](./high-value-features-plan.md)

### Phase 1.2: Recipe Favorites Management
- **Status:** ⚪ Not Started
- **Tasks:**
  - [ ] Add `add_favorite`, `remove_favorite`, `get_user_favorites` to MealieClient
  - [ ] Create `favorites_add`, `favorites_remove`, `favorites_list` in `tools/recipes.py`
  - [ ] Register 3 MCP tools: `mealie_favorites_add`, `mealie_favorites_remove`, `mealie_favorites_list`
  - [ ] Write unit tests (mock-based)
  - [ ] Write E2E tests (live API)
  - [ ] Write MCP tests (tool invocation)
  - [ ] Update CHANGELOG.md
- **Effort:** M
- **Done When:** All tests passing (unit, E2E, MCP), PR merged

### Phase 1.3: Recipe Suggestions
- **Status:** ⚪ Not Started
- **Tasks:**
  - [ ] Add `get_recipe_suggestions` to MealieClient
  - [ ] Create `suggestions_get` in `tools/recipes.py`
  - [ ] Register MCP tool: `mealie_recipes_suggestions`
  - [ ] Write unit tests (mock-based)
  - [ ] Write E2E tests (live API)
  - [ ] Write MCP tests (tool invocation)
  - [ ] Update CHANGELOG.md
- **Effort:** S
- **Done When:** All tests passing (unit, E2E, MCP), PR merged

### Phase 1.4: Shared Recipes Management
- **Status:** ⚪ Not Started
- **Tasks:**
  - [ ] Add `list_shared_recipes`, `create_share`, `get_shared_recipe`, `delete_share`, `access_shared_recipe` to MealieClient
  - [ ] Create new file `tools/sharing.py` with 5 functions
  - [ ] Register 5 MCP tools: `mealie_shared_list`, `create`, `get`, `delete`, `access`
  - [ ] Write unit tests (mock-based)
  - [ ] Write E2E tests (live API)
  - [ ] Write MCP tests (tool invocation)
  - [ ] Update CHANGELOG.md
- **Effort:** M
- **Done When:** All tests passing (unit, E2E, MCP), PR merged

---

## Batch 2 (Integration & Automation)

### Phase 2.1: Webhooks Management
- **Status:** 🔴 Blocked
- **Depends On:** Phase 1.1, 1.2, 1.3, 1.4
- **Tasks:**
  - [ ] Add `list_webhooks`, `create_webhook`, `update_webhook`, `delete_webhook`, `test_webhook` to MealieClient
  - [ ] Create new file `tools/webhooks.py` with 5 functions
  - [ ] Register 5 MCP tools: `mealie_webhooks_list`, `create`, `update`, `delete`, `test`
  - [ ] Write unit tests (mock-based)
  - [ ] Write E2E tests (live API)
  - [ ] Write MCP tests (tool invocation)
  - [ ] Update CHANGELOG.md
- **Effort:** M
- **Done When:** All tests passing (unit, E2E, MCP), PR merged
- **Plan:** [High-Value Features Plan](./high-value-features-plan.md)

### Phase 2.2: Recipe Actions Management
- **Status:** 🔴 Blocked
- **Depends On:** Phase 1.1, 1.2, 1.3, 1.4
- **Tasks:**
  - [ ] Add `list_recipe_actions`, `create_recipe_action`, `update_recipe_action`, `delete_recipe_action`, `trigger_recipe_action` to MealieClient
  - [ ] Create new file `tools/actions.py` with 5 functions
  - [ ] Register 5 MCP tools: `mealie_actions_list`, `create`, `update`, `delete`, `trigger`
  - [ ] Write unit tests (mock-based)
  - [ ] Write E2E tests (live API)
  - [ ] Write MCP tests (tool invocation)
  - [ ] Update CHANGELOG.md
- **Effort:** M
- **Done When:** All tests passing (unit, E2E, MCP), PR merged

### Phase 2.3: Event Notifications Management
- **Status:** 🔴 Blocked
- **Depends On:** Phase 1.1, 1.2, 1.3, 1.4
- **Tasks:**
  - [ ] Add `list_notifications`, `create_notification`, `get_notification`, `update_notification`, `delete_notification`, `test_notification` to MealieClient
  - [ ] Create new file `tools/notifications.py` with 6 functions
  - [ ] Register 6 MCP tools: `mealie_notifications_list`, `create`, `get`, `update`, `delete`, `test`
  - [ ] Write unit tests (mock-based)
  - [ ] Write E2E tests (live API)
  - [ ] Write MCP tests (tool invocation)
  - [ ] Update CHANGELOG.md
- **Effort:** M
- **Done When:** All tests passing (unit, E2E, MCP), PR merged

---

## Batch 3 (Enhanced Features)

### Phase 3.1: Recipe Assets Management
- **Status:** 🔴 Blocked
- **Depends On:** Phase 2.1, 2.2, 2.3
- **Tasks:**
  - [ ] Research Mealie API endpoints for recipe assets (PDFs, videos)
  - [ ] Add asset upload/download methods to MealieClient
  - [ ] Create `tools/assets.py` with asset management functions
  - [ ] Register MCP tools for asset operations
  - [ ] Write comprehensive tests
  - [ ] Update CHANGELOG.md
- **Effort:** M
- **Done When:** All tests passing, PR merged
- **Notes:** Requires OpenAPI exploration to identify exact endpoints

### Phase 3.2: Group/Household Management
- **Status:** 🔴 Blocked
- **Depends On:** Phase 2.1, 2.2, 2.3
- **Tasks:**
  - [ ] Research Mealie API endpoints for household/group management
  - [ ] Add household methods to MealieClient (members, permissions, stats)
  - [ ] Create `tools/households.py` with management functions
  - [ ] Register MCP tools for household operations
  - [ ] Write comprehensive tests
  - [ ] Update CHANGELOG.md
- **Effort:** M
- **Done When:** All tests passing, PR merged
- **Notes:** May overlap with existing group endpoints

### Phase 3.3: Recipe Export Formats
- **Status:** 🔴 Blocked
- **Depends On:** Phase 2.1, 2.2, 2.3
- **Tasks:**
  - [ ] Add export format methods to MealieClient (PDF, ZIP, etc.)
  - [ ] Enhance existing `tools/recipes.py` with export format functions
  - [ ] Register MCP tools for various export formats
  - [ ] Write comprehensive tests
  - [ ] Update CHANGELOG.md
- **Effort:** S
- **Done When:** All tests passing, PR merged
- **Notes:** Some bulk export endpoints already exist

---

## Backlog

- [ ] Recipe assets (detailed implementation)
- [ ] Advanced filtering for ratings/favorites
- [ ] Batch operations for ratings/favorites
- [ ] Webhook event filtering
- [ ] Notification scheduling
