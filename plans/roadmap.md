# Roadmap - Testing Gaps Implementation

## Batch 1 (Current - Foundation)

### Phase 1.1: E2E Test Infrastructure Setup
- **Status:** ⚪ Not Started
- **Tasks:**
  - [ ] Create `tests/e2e/` directory structure
  - [ ] Implement E2E test fixtures (real Mealie client, test data cleanup)
  - [ ] Create `conftest_e2e.py` with skip logic (requires MEALIE_E2E_URL)
  - [ ] Add E2E-specific pytest markers (`@pytest.mark.e2e`)
  - [ ] Implement test data cleanup fixtures (delete test recipes/mealplans after)
  - [ ] Create unique identifier generator for test data (prevent collisions)
  - [ ] Add retry logic helpers for network failures
  - [ ] Document E2E test setup in README
- **Effort:** M
- **Done When:**
  - `tests/e2e/conftest_e2e.py` exists with working fixtures
  - E2E tests skip gracefully when `MEALIE_E2E_URL` not set
  - Cleanup fixtures successfully delete test data
  - Retry logic handles transient network failures
  - Documentation explains how to run E2E tests locally
- **Plan:** [plans/testing-gaps-plan.md](testing-gaps-plan.md)

### Phase 1.2: MCP Server Test Framework
- **Status:** ⚪ Not Started
- **Tasks:**
  - [ ] Research FastMCP testing best practices (check fastmcp documentation)
  - [ ] Create MCP server test fixtures (mock MealieClient injection)
  - [ ] Implement tool invocation test helpers (call MCP tools via protocol)
  - [ ] Create resource provider test utilities (validate resource URIs)
  - [ ] Add MCP protocol validation helpers (check MCP spec compliance)
  - [ ] Create conftest fixtures for server.py testing
  - [ ] Document MCP testing patterns
- **Effort:** M
- **Done When:**
  - `tests/mcp/conftest.py` exists with reusable fixtures
  - Can invoke MCP tools programmatically in tests
  - Can validate MCP resource URIs and responses
  - Tool parameter validation can be tested
  - Protocol compliance can be verified
  - Documentation explains MCP testing approach
- **Plan:** [plans/testing-gaps-plan.md](testing-gaps-plan.md)

### Phase 1.3: Unit Test Utilities & Helpers
- **Status:** ⚪ Not Started
- **Tasks:**
  - [ ] Create mock data builders (recipe, mealplan, shopping list factories)
  - [ ] Implement validation test helpers (check response schemas)
  - [ ] Add assertion helpers for common checks (dates, IDs, nested structures)
  - [ ] Create parameterized test utilities (test same logic with different inputs)
  - [ ] Refactor existing conftest.py (extract reusable patterns)
  - [ ] Add unit test fixtures for isolated client methods
  - [ ] Document unit testing patterns
- **Effort:** S
- **Done When:**
  - `tests/unit/conftest.py` has reusable fixtures
  - Mock data builders can generate realistic test data
  - Validation helpers can check response structure
  - Assertion helpers simplify common checks
  - Documentation explains unit testing patterns
- **Plan:** [plans/testing-gaps-plan.md](testing-gaps-plan.md)

---

## Batch 2 (Blocked by Batch 1 - CRITICAL MCP Layer)

### Phase 2.1: MCP Server Tool Registration Tests
- **Status:** 🔴 Blocked
- **Depends On:** Phase 1.2
- **Tasks:**
  - [ ] Test all 31 MCP tool registrations (verify @mcp.tool decorator)
  - [ ] Test tool parameter validation (required vs optional params)
  - [ ] Test tool invocation with valid inputs
  - [ ] Test tool error handling (invalid params, API errors)
  - [ ] Test tool response formatting (JSON structure)
  - [ ] Test tool authentication (client initialization)
  - [ ] Test ping endpoint (connectivity check)
  - [ ] Validate tool names match documentation
- **Effort:** M
- **Done When:**
  - `tests/mcp/test_server_tools.py` exists with 50+ tests
  - All 31 tools have registration tests
  - Tool parameter validation is tested
  - Error handling for each tool is verified
  - Coverage of `src/server.py` reaches 60%+
  - All tool names consistent with README
- **Coverage Target:** 60%+ of `src/server.py` (currently 2%)
- **Plan:** [plans/testing-gaps-plan.md](testing-gaps-plan.md)

### Phase 2.2: MCP Resource Provider Tests
- **Status:** 🔴 Blocked
- **Depends On:** Phase 1.2
- **Tasks:**
  - [ ] Test recipes resource provider (list, get by slug)
  - [ ] Test mealplans resource provider (current, today, by date)
  - [ ] Test shopping resource provider (lists, specific list)
  - [ ] Test resource URI parsing (valid/invalid URIs)
  - [ ] Test resource response formatting (MCP resource schema)
  - [ ] Test resource error handling (404, 500)
  - [ ] Test resource pagination (if applicable)
  - [ ] Validate resource URIs match documentation
- **Effort:** M
- **Done When:**
  - `tests/mcp/test_resources_recipes.py` exists with 20+ tests
  - `tests/mcp/test_resources_mealplans.py` exists with 15+ tests
  - `tests/mcp/test_resources_shopping.py` exists with 10+ tests
  - All 7 resource URIs tested
  - Resource error handling verified
  - Coverage of `src/resources/*.py` reaches 60%+
- **Coverage Target:** 60%+ of `src/resources/*.py` (currently 5-7%)
- **Plan:** [plans/testing-gaps-plan.md](testing-gaps-plan.md)

---

## Batch 3 (Blocked by Batch 1 - E2E Coverage)

### Phase 3.1: E2E Recipe Workflow Tests
- **Status:** 🔴 Blocked
- **Depends On:** Phase 1.1
- **Tasks:**
  - [ ] Test recipe search → get → update workflow
  - [ ] Test recipe create → tag → categorize workflow
  - [ ] Test recipe import from URL (use test website)
  - [ ] Test recipe image upload from URL
  - [ ] Test recipe duplicate
  - [ ] Test recipe delete with cleanup
  - [ ] Test recipe bulk operations (tag, categorize, delete)
  - [ ] Test recipe structured ingredients update
  - [ ] Test recipe last made timestamp update
  - [ ] Test error scenarios (404, invalid slug)
- **Effort:** M
- **Done When:**
  - `tests/e2e/test_recipe_workflows.py` exists with 15+ tests
  - All recipe CRUD operations tested against real API
  - Bulk operations verified
  - Image upload tested with real image URL
  - Test data cleanup successful
  - All tests pass with real Mealie instance
- **Plan:** [plans/testing-gaps-plan.md](testing-gaps-plan.md)

### Phase 3.2: E2E Meal Planning Workflow Tests
- **Status:** 🔴 Blocked
- **Depends On:** Phase 1.1
- **Tasks:**
  - [ ] Test mealplan list → create → update → delete workflow
  - [ ] Test mealplan search functionality
  - [ ] Test mealplan batch update
  - [ ] Test mealplan delete range
  - [ ] Test mealplan rules (create, update, delete)
  - [ ] Test mealplan today/current/by-date retrieval
  - [ ] Test mealplan random suggestion
  - [ ] Test error scenarios (invalid date, missing recipe)
- **Effort:** M
- **Done When:**
  - `tests/e2e/test_mealplan_workflows.py` exists with 12+ tests
  - All mealplan CRUD operations tested
  - Batch operations verified
  - Mealplan rules tested
  - Date-based retrieval tested
  - Test data cleanup successful
- **Plan:** [plans/testing-gaps-plan.md](testing-gaps-plan.md)

### Phase 3.3: E2E Shopping List Workflow Tests
- **Status:** 🔴 Blocked
- **Depends On:** Phase 1.1
- **Tasks:**
  - [ ] Test shopping list create → add items → check → delete workflow
  - [ ] Test shopping list bulk add items
  - [ ] Test shopping list add recipe ingredients
  - [ ] Test shopping list generate from mealplan (high-value workflow)
  - [ ] Test shopping list clear checked items
  - [ ] Test shopping list delete recipe from list
  - [ ] Test error scenarios (invalid list ID, missing recipe)
- **Effort:** S
- **Done When:**
  - `tests/e2e/test_shopping_workflows.py` exists with 10+ tests
  - All shopping CRUD operations tested
  - Mealplan → shopping list generation verified (critical workflow)
  - Recipe → shopping list tested
  - Test data cleanup successful
- **Plan:** [plans/testing-gaps-plan.md](testing-gaps-plan.md)

---

## Batch 4 (Blocked by Batch 1 - Pyramid Rebalancing)

### Phase 4.1: Expand Unit Test Coverage (Client Layer)
- **Status:** 🔴 Blocked
- **Depends On:** Phase 1.3
- **Tasks:**
  - [ ] Test MealieClient initialization (valid/invalid config)
  - [ ] Test client HTTP error handling (timeout, connection error)
  - [ ] Test client authentication header injection
  - [ ] Test client JSON parsing
  - [ ] Test client pagination helpers
  - [ ] Test client retry logic (if implemented)
  - [ ] Add unit tests for each client method (recipes, mealplans, shopping)
  - [ ] Test client URL construction
  - [ ] Test client response transformation
- **Effort:** M
- **Done When:**
  - `tests/unit/test_client.py` exists with 40+ tests
  - All client methods have unit tests
  - Error handling thoroughly tested
  - Coverage of `src/client.py` reaches 80%+
  - Tests run in <1 second (no network calls)
- **Coverage Target:** 80%+ of `src/client.py` (currently 66%)
- **Plan:** [plans/testing-gaps-plan.md](testing-gaps-plan.md)

### Phase 4.2: Expand Unit Test Coverage (Tools Layer)
- **Status:** 🔴 Blocked
- **Depends On:** Phase 1.3
- **Tasks:**
  - [ ] Add unit tests for tool parameter validation logic
  - [ ] Test tool response formatting (JSON transformation)
  - [ ] Test tool error message construction
  - [ ] Test tool business logic (parsing, filtering, transformation)
  - [ ] Add unit tests for parser tool (ingredient parsing)
  - [ ] Test tool helpers (date parsing, ID generation)
  - [ ] Test batch operation logic
  - [ ] Focus on tools with <50% coverage
- **Effort:** M
- **Done When:**
  - `tests/unit/test_tools_*.py` files expanded with 60+ new tests
  - All tool modules have 60%+ coverage
  - Business logic isolated from HTTP calls
  - Tests run in <2 seconds
  - Coverage gap in tools layer reduced by 15%
- **Coverage Target:** 60%+ for all tool modules (currently 48-77%)
- **Plan:** [plans/testing-gaps-plan.md](testing-gaps-plan.md)

---

## Batch 5 (Blocked by Batch 3 - Integration & CI)

### Phase 5.1: CI/CD E2E Test Integration
- **Status:** 🔴 Blocked
- **Depends On:** Phase 3.1, 3.2, 3.3
- **Tasks:**
  - [ ] Add E2E test job to `.github/workflows/test.yml`
  - [ ] Configure E2E job to run optionally (manual trigger or schedule)
  - [ ] Add GitHub secrets for E2E test credentials (MEALIE_E2E_URL, MEALIE_E2E_TOKEN)
  - [ ] Configure E2E test timeout (15 minutes)
  - [ ] Add E2E test result artifact upload
  - [ ] Add E2E test status badge to README
  - [ ] Document E2E CI/CD setup
- **Effort:** S
- **Done When:**
  - E2E tests run in GitHub Actions (manual trigger)
  - Tests use GitHub secrets for credentials
  - E2E job timeout set to 15 minutes
  - Test results uploaded as artifacts
  - README documents E2E CI/CD
- **Plan:** [plans/testing-gaps-plan.md](testing-gaps-plan.md)

### Phase 5.2: Docker Container E2E Tests
- **Status:** 🔴 Blocked
- **Depends On:** Phase 1.1
- **Tasks:**
  - [ ] Test MCP server runs in Docker container
  - [ ] Test MCP stdio communication in container
  - [ ] Test environment variable injection (MEALIE_BASE_URL, MEALIE_API_TOKEN)
  - [ ] Test container healthcheck
  - [ ] Test container logs and error output
  - [ ] Test container with real MCP client communication
  - [ ] Validate Docker image from GHCR
- **Effort:** M
- **Done When:**
  - `tests/e2e/test_docker_container.py` exists with 8+ tests
  - Docker container startup validated
  - MCP protocol over stdio works in container
  - Environment variables correctly injected
  - Real MCP client can communicate with containerized server
- **Plan:** [plans/testing-gaps-plan.md](testing-gaps-plan.md)

---

## Batch 6 (Final - Documentation)

### Phase 6.1: Documentation & Test Coverage Report
- **Status:** 🔴 Blocked
- **Depends On:** ALL previous phases
- **Tasks:**
  - [ ] Generate final coverage report (all test categories)
  - [ ] Create test pyramid visualization (unit/integration/E2E breakdown)
  - [ ] Document test organization (unit, integration, mcp, e2e)
  - [ ] Update README with testing section
  - [ ] Create TESTING.md guide (how to run different test types)
  - [ ] Document CI/CD test jobs and when they run
  - [ ] Add coverage targets to documentation (70%+ overall)
  - [ ] Celebrate achieving healthy test pyramid! 🎉
- **Effort:** S
- **Done When:**
  - Coverage report shows 70%+ total coverage
  - Test pyramid is healthy (40% unit, 45% integration, 10% E2E)
  - Documentation complete and accurate
  - TESTING.md exists with clear instructions
  - README updated with test badges and sections
- **Plan:** [plans/testing-gaps-plan.md](testing-gaps-plan.md)

---

## Backlog

- [ ] Performance testing for MCP protocol overhead
- [ ] Stress testing for concurrent requests
- [ ] Fuzz testing for input validation
- [ ] Security testing for API token handling
- [ ] Integration tests with different Mealie versions
- [ ] MCP protocol version compatibility testing
