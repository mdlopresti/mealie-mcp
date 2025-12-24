# Testing Gaps Implementation Plan

## Summary
Address critical testing gaps in Mealie MCP Server to achieve 70%+ coverage with a healthy test pyramid. Current state: 49% coverage with inverted pyramid (7% unit, 38% integration, 0% E2E). Critical MCP layer is 98% untested. This plan prioritizes the most critical risks first: MCP layer validation and E2E testing.

## Complexity Assessment
- **Systems affected:** 4 (MCP server layer, resources, test infrastructure, CI/CD)
- **Classification:** **Complex**
- **Reasoning:**
  - Requires new E2E test infrastructure with real Mealie API
  - MCP protocol testing requires stdio communication validation
  - Docker container testing needs environment setup
  - 200+ new tests across multiple layers
  - Must maintain existing 439 tests while refactoring
  - CI/CD integration for optional E2E test suite

## Affected Systems
- `src/server.py` - FastMCP server (350 statements, 2% coverage)
- `src/resources/*.py` - MCP resource providers (660 statements, 5-7% coverage)
- `tests/` - Test suite (expand from 439 to 600+ tests)
- `.github/workflows/test.yml` - CI/CD pipeline (add E2E test job)
- `tests/e2e/` - New E2E test infrastructure (0 → 20+ tests)

## Dependencies
- **Requires before starting:**
  - Test Mealie instance URL (recipe.vilo.network)
  - Test API token with appropriate permissions
  - Docker/Podman for container testing
  - MCP protocol test fixtures

- **External services:**
  - Mealie API at recipe.vilo.network (for E2E tests)
  - GitHub Container Registry (for Docker image testing)

- **Libraries/SDKs:**
  - pytest-asyncio (for async MCP protocol testing)
  - pytest-timeout (for E2E test timeouts)
  - mcp Python SDK (for protocol validation)

## Assumptions
- Recipe.vilo.network is available for E2E testing
- Test account can create/modify/delete test recipes without affecting production data
- CI/CD has 15 minutes for E2E test suite (currently 10 min timeout)
- E2E tests are opt-in via environment variable (not required for PR merges)
- Existing 439 tests continue to pass throughout refactoring

## Risks
- **E2E test flakiness**: Network issues, API timeouts → Mitigation: Retry logic, generous timeouts, clear error messages
- **Test data pollution**: E2E tests create real data → Mitigation: Dedicated test account, cleanup fixtures, unique identifiers
- **CI/CD runtime**: E2E tests slow down pipeline → Mitigation: Optional suite, parallel execution, caching
- **MCP protocol changes**: FastMCP updates break tests → Mitigation: Pin versions, protocol validation layer
- **Coverage regression**: Refactoring breaks existing tests → Mitigation: Run full suite after each phase

## Batch Execution Plan

### Batch 1 (CRITICAL - Foundation) - 3 phases in parallel
| Phase | Goal | Effort | Depends On |
|-------|------|--------|------------|
| 1.1 | E2E Test Infrastructure Setup | M | None |
| 1.2 | MCP Server Test Framework | M | None |
| 1.3 | Unit Test Utilities & Helpers | S | None |

### Batch 2 (CRITICAL - MCP Layer Validation) - 2 phases in parallel
| Phase | Goal | Effort | Depends On |
|-------|------|--------|------------|
| 2.1 | MCP Server Tool Registration Tests | M | 1.2 |
| 2.2 | MCP Resource Provider Tests | M | 1.2 |

### Batch 3 (HIGH - E2E Coverage) - 3 phases in parallel
| Phase | Goal | Effort | Depends On |
|-------|------|--------|------------|
| 3.1 | E2E Recipe Workflow Tests | M | 1.1 |
| 3.2 | E2E Meal Planning Workflow Tests | M | 1.1 |
| 3.3 | E2E Shopping List Workflow Tests | S | 1.1 |

### Batch 4 (MEDIUM - Pyramid Rebalancing) - 2 phases in parallel
| Phase | Goal | Effort | Depends On |
|-------|------|--------|------------|
| 4.1 | Expand Unit Test Coverage (Client Layer) | M | 1.3 |
| 4.2 | Expand Unit Test Coverage (Tools Layer) | M | 1.3 |

### Batch 5 (MEDIUM - Integration & CI) - 2 phases in parallel
| Phase | Goal | Effort | Depends On |
|-------|------|--------|------------|
| 5.1 | CI/CD E2E Test Integration | S | 3.1, 3.2, 3.3 |
| 5.2 | Docker Container E2E Tests | M | 1.1 |

### Batch 6 (LOW - Polish & Documentation) - Sequential
| Phase | Goal | Effort | Depends On |
|-------|------|--------|------------|
| 6.1 | Documentation & Test Coverage Report | S | ALL |

---

## Detailed Phases

### Phase 1.1: E2E Test Infrastructure Setup
**Status:** ⚪ Not Started

- **Tasks:**
  - [ ] Create `tests/e2e/` directory structure
  - [ ] Implement E2E test fixtures (real Mealie client, test data cleanup)
  - [ ] Create `conftest_e2e.py` with skip logic (requires MEALIE_E2E_URL)
  - [ ] Add E2E-specific pytest markers (`@pytest.mark.e2e`)
  - [ ] Implement test data cleanup fixtures (delete test recipes/mealplans after)
  - [ ] Create unique identifier generator for test data (prevent collisions)
  - [ ] Add retry logic helpers for network failures
  - [ ] Document E2E test setup in README

- **Effort:** M (4-6 hours)

- **Done When:**
  - `tests/e2e/conftest_e2e.py` exists with working fixtures
  - E2E tests skip gracefully when `MEALIE_E2E_URL` not set
  - Cleanup fixtures successfully delete test data
  - Retry logic handles transient network failures
  - Documentation explains how to run E2E tests locally

- **Files Affected:**
  - `tests/e2e/conftest_e2e.py` (new)
  - `tests/e2e/__init__.py` (new)
  - `tests/e2e/helpers.py` (new - retry logic, unique IDs)
  - `README.md` (update - E2E test section)
  - `pytest.ini` or `pyproject.toml` (add e2e marker)

- **Parallelizable with:** 1.2, 1.3

---

### Phase 1.2: MCP Server Test Framework
**Status:** ⚪ Not Started

- **Tasks:**
  - [ ] Research FastMCP testing best practices (check fastmcp documentation)
  - [ ] Create MCP server test fixtures (mock MealieClient injection)
  - [ ] Implement tool invocation test helpers (call MCP tools via protocol)
  - [ ] Create resource provider test utilities (validate resource URIs)
  - [ ] Add MCP protocol validation helpers (check MCP spec compliance)
  - [ ] Create conftest fixtures for server.py testing
  - [ ] Document MCP testing patterns

- **Effort:** M (5-7 hours)

- **Done When:**
  - `tests/mcp/conftest.py` exists with reusable fixtures
  - Can invoke MCP tools programmatically in tests
  - Can validate MCP resource URIs and responses
  - Tool parameter validation can be tested
  - Protocol compliance can be verified
  - Documentation explains MCP testing approach

- **Files Affected:**
  - `tests/mcp/conftest.py` (new)
  - `tests/mcp/__init__.py` (new)
  - `tests/mcp/helpers.py` (new - protocol validation)
  - `docs/MCP_TESTING.md` (new - testing guide)

- **Parallelizable with:** 1.1, 1.3

---

### Phase 1.3: Unit Test Utilities & Helpers
**Status:** ⚪ Not Started

- **Tasks:**
  - [ ] Create mock data builders (recipe, mealplan, shopping list factories)
  - [ ] Implement validation test helpers (check response schemas)
  - [ ] Add assertion helpers for common checks (dates, IDs, nested structures)
  - [ ] Create parameterized test utilities (test same logic with different inputs)
  - [ ] Refactor existing conftest.py (extract reusable patterns)
  - [ ] Add unit test fixtures for isolated client methods
  - [ ] Document unit testing patterns

- **Effort:** S (2-4 hours)

- **Done When:**
  - `tests/unit/conftest.py` has reusable fixtures
  - Mock data builders can generate realistic test data
  - Validation helpers can check response structure
  - Assertion helpers simplify common checks
  - Documentation explains unit testing patterns

- **Files Affected:**
  - `tests/unit/__init__.py` (new)
  - `tests/unit/conftest.py` (new)
  - `tests/unit/builders.py` (new - mock data factories)
  - `tests/unit/assertions.py` (new - custom assertions)
  - `tests/conftest.py` (refactor - extract shared fixtures)

- **Parallelizable with:** 1.1, 1.2

---

### Phase 2.1: MCP Server Tool Registration Tests
**Status:** 🔴 Blocked
**Depends On:** Phase 1.2

- **Tasks:**
  - [ ] Test all 31 MCP tool registrations (verify @mcp.tool decorator)
  - [ ] Test tool parameter validation (required vs optional params)
  - [ ] Test tool invocation with valid inputs
  - [ ] Test tool error handling (invalid params, API errors)
  - [ ] Test tool response formatting (JSON structure)
  - [ ] Test tool authentication (client initialization)
  - [ ] Test ping endpoint (connectivity check)
  - [ ] Validate tool names match documentation

- **Effort:** M (5-7 hours)

- **Done When:**
  - `tests/mcp/test_server_tools.py` exists with 50+ tests
  - All 31 tools have registration tests
  - Tool parameter validation is tested
  - Error handling for each tool is verified
  - Coverage of `src/server.py` reaches 60%+
  - All tool names consistent with README

- **Files Affected:**
  - `tests/mcp/test_server_tools.py` (new - 50+ tests)
  - `tests/mcp/test_server_ping.py` (new - connectivity tests)
  - `tests/mcp/test_tool_validation.py` (new - parameter validation)

- **Coverage Target:** 60%+ of `src/server.py` (currently 2%)

- **Parallelizable with:** 2.2

---

### Phase 2.2: MCP Resource Provider Tests
**Status:** 🔴 Blocked
**Depends On:** Phase 1.2

- **Tasks:**
  - [ ] Test recipes resource provider (list, get by slug)
  - [ ] Test mealplans resource provider (current, today, by date)
  - [ ] Test shopping resource provider (lists, specific list)
  - [ ] Test resource URI parsing (valid/invalid URIs)
  - [ ] Test resource response formatting (MCP resource schema)
  - [ ] Test resource error handling (404, 500)
  - [ ] Test resource pagination (if applicable)
  - [ ] Validate resource URIs match documentation

- **Effort:** M (4-6 hours)

- **Done When:**
  - `tests/mcp/test_resources_recipes.py` exists with 20+ tests
  - `tests/mcp/test_resources_mealplans.py` exists with 15+ tests
  - `tests/mcp/test_resources_shopping.py` exists with 10+ tests
  - All 7 resource URIs tested
  - Resource error handling verified
  - Coverage of `src/resources/*.py` reaches 60%+

- **Files Affected:**
  - `tests/mcp/test_resources_recipes.py` (new - 20+ tests)
  - `tests/mcp/test_resources_mealplans.py` (new - 15+ tests)
  - `tests/mcp/test_resources_shopping.py` (new - 10+ tests)

- **Coverage Target:** 60%+ of `src/resources/*.py` (currently 5-7%)

- **Parallelizable with:** 2.1

---

### Phase 3.1: E2E Recipe Workflow Tests
**Status:** 🔴 Blocked
**Depends On:** Phase 1.1

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

- **Effort:** M (5-7 hours)

- **Done When:**
  - `tests/e2e/test_recipe_workflows.py` exists with 15+ tests
  - All recipe CRUD operations tested against real API
  - Bulk operations verified
  - Image upload tested with real image URL
  - Test data cleanup successful
  - All tests pass with real Mealie instance

- **Files Affected:**
  - `tests/e2e/test_recipe_workflows.py` (new - 15+ tests)
  - `tests/e2e/test_recipe_bulk.py` (new - bulk operations)
  - `tests/e2e/test_recipe_images.py` (new - image upload)

- **Parallelizable with:** 3.2, 3.3

---

### Phase 3.2: E2E Meal Planning Workflow Tests
**Status:** 🔴 Blocked
**Depends On:** Phase 1.1

- **Tasks:**
  - [ ] Test mealplan list → create → update → delete workflow
  - [ ] Test mealplan search functionality
  - [ ] Test mealplan batch update
  - [ ] Test mealplan delete range
  - [ ] Test mealplan rules (create, update, delete)
  - [ ] Test mealplan today/current/by-date retrieval
  - [ ] Test mealplan random suggestion
  - [ ] Test error scenarios (invalid date, missing recipe)

- **Effort:** M (4-6 hours)

- **Done When:**
  - `tests/e2e/test_mealplan_workflows.py` exists with 12+ tests
  - All mealplan CRUD operations tested
  - Batch operations verified
  - Mealplan rules tested
  - Date-based retrieval tested
  - Test data cleanup successful

- **Files Affected:**
  - `tests/e2e/test_mealplan_workflows.py` (new - 12+ tests)
  - `tests/e2e/test_mealplan_rules.py` (new - rules tests)
  - `tests/e2e/test_mealplan_batch.py` (new - batch ops)

- **Parallelizable with:** 3.1, 3.3

---

### Phase 3.3: E2E Shopping List Workflow Tests
**Status:** 🔴 Blocked
**Depends On:** Phase 1.1

- **Tasks:**
  - [ ] Test shopping list create → add items → check → delete workflow
  - [ ] Test shopping list bulk add items
  - [ ] Test shopping list add recipe ingredients
  - [ ] Test shopping list generate from mealplan (high-value workflow)
  - [ ] Test shopping list clear checked items
  - [ ] Test shopping list delete recipe from list
  - [ ] Test error scenarios (invalid list ID, missing recipe)

- **Effort:** S (3-4 hours)

- **Done When:**
  - `tests/e2e/test_shopping_workflows.py` exists with 10+ tests
  - All shopping CRUD operations tested
  - Mealplan → shopping list generation verified (critical workflow)
  - Recipe → shopping list tested
  - Test data cleanup successful

- **Files Affected:**
  - `tests/e2e/test_shopping_workflows.py` (new - 10+ tests)
  - `tests/e2e/test_shopping_mealplan_integration.py` (new - critical workflow)

- **Parallelizable with:** 3.1, 3.2

---

### Phase 4.1: Expand Unit Test Coverage (Client Layer)
**Status:** 🔴 Blocked
**Depends On:** Phase 1.3

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

- **Effort:** M (5-7 hours)

- **Done When:**
  - `tests/unit/test_client.py` exists with 40+ tests
  - All client methods have unit tests
  - Error handling thoroughly tested
  - Coverage of `src/client.py` reaches 80%+
  - Tests run in <1 second (no network calls)

- **Files Affected:**
  - `tests/unit/test_client.py` (expand from existing test_client_basic.py)
  - `tests/unit/test_client_errors.py` (new - error handling)
  - `tests/unit/test_client_pagination.py` (new - pagination logic)

- **Coverage Target:** 80%+ of `src/client.py` (currently 66%)

- **Parallelizable with:** 4.2

---

### Phase 4.2: Expand Unit Test Coverage (Tools Layer)
**Status:** 🔴 Blocked
**Depends On:** Phase 1.3

- **Tasks:**
  - [ ] Add unit tests for tool parameter validation logic
  - [ ] Test tool response formatting (JSON transformation)
  - [ ] Test tool error message construction
  - [ ] Test tool business logic (parsing, filtering, transformation)
  - [ ] Add unit tests for parser tool (ingredient parsing)
  - [ ] Test tool helpers (date parsing, ID generation)
  - [ ] Test batch operation logic
  - [ ] Focus on tools with <50% coverage

- **Effort:** M (6-8 hours)

- **Done When:**
  - `tests/unit/test_tools_*.py` files expanded with 60+ new tests
  - All tool modules have 60%+ coverage
  - Business logic isolated from HTTP calls
  - Tests run in <2 seconds
  - Coverage gap in tools layer reduced by 15%

- **Files Affected:**
  - `tests/unit/test_tools_recipes.py` (new - pure logic tests)
  - `tests/unit/test_tools_mealplans.py` (new)
  - `tests/unit/test_tools_shopping.py` (new)
  - `tests/unit/test_tools_parser.py` (expand existing)

- **Coverage Target:** 60%+ for all tool modules (currently 48-77%)

- **Parallelizable with:** 4.1

---

### Phase 5.1: CI/CD E2E Test Integration
**Status:** 🔴 Blocked
**Depends On:** Phase 3.1, 3.2, 3.3

- **Tasks:**
  - [ ] Add E2E test job to `.github/workflows/test.yml`
  - [ ] Configure E2E job to run optionally (manual trigger or schedule)
  - [ ] Add GitHub secrets for E2E test credentials (MEALIE_E2E_URL, MEALIE_E2E_TOKEN)
  - [ ] Configure E2E test timeout (15 minutes)
  - [ ] Add E2E test result artifact upload
  - [ ] Add E2E test status badge to README
  - [ ] Document E2E CI/CD setup

- **Effort:** S (2-3 hours)

- **Done When:**
  - E2E tests run in GitHub Actions (manual trigger)
  - Tests use GitHub secrets for credentials
  - E2E job timeout set to 15 minutes
  - Test results uploaded as artifacts
  - README documents E2E CI/CD

- **Files Affected:**
  - `.github/workflows/test.yml` (add e2e-test job)
  - `.github/workflows/e2e-manual.yml` (new - manual E2E trigger)
  - `README.md` (add E2E badge, CI/CD docs)

- **Parallelizable with:** 5.2

---

### Phase 5.2: Docker Container E2E Tests
**Status:** 🔴 Blocked
**Depends On:** Phase 1.1

- **Tasks:**
  - [ ] Test MCP server runs in Docker container
  - [ ] Test MCP stdio communication in container
  - [ ] Test environment variable injection (MEALIE_BASE_URL, MEALIE_API_TOKEN)
  - [ ] Test container healthcheck
  - [ ] Test container logs and error output
  - [ ] Test container with real MCP client communication
  - [ ] Validate Docker image from GHCR

- **Effort:** M (4-5 hours)

- **Done When:**
  - `tests/e2e/test_docker_container.py` exists with 8+ tests
  - Docker container startup validated
  - MCP protocol over stdio works in container
  - Environment variables correctly injected
  - Real MCP client can communicate with containerized server

- **Files Affected:**
  - `tests/e2e/test_docker_container.py` (new - 8+ tests)
  - `tests/e2e/test_mcp_stdio.py` (new - protocol tests)

- **Parallelizable with:** 5.1

---

### Phase 6.1: Documentation & Test Coverage Report
**Status:** 🔴 Blocked
**Depends On:** ALL previous phases

- **Tasks:**
  - [ ] Generate final coverage report (all test categories)
  - [ ] Create test pyramid visualization (unit/integration/E2E breakdown)
  - [ ] Document test organization (unit, integration, mcp, e2e)
  - [ ] Update README with testing section
  - [ ] Create TESTING.md guide (how to run different test types)
  - [ ] Document CI/CD test jobs and when they run
  - [ ] Add coverage targets to documentation (70%+ overall)
  - [ ] Celebrate achieving healthy test pyramid! 🎉

- **Effort:** S (2-3 hours)

- **Done When:**
  - Coverage report shows 70%+ total coverage
  - Test pyramid is healthy (40% unit, 45% integration, 10% E2E)
  - Documentation complete and accurate
  - TESTING.md exists with clear instructions
  - README updated with test badges and sections

- **Files Affected:**
  - `TESTING.md` (new - comprehensive test guide)
  - `README.md` (update - testing section)
  - `docs/TEST_PYRAMID.md` (new - visualization and metrics)
  - `docs/COVERAGE_REPORT.md` (new - final coverage report)

---

## Critical Path
The longest dependency chain that gates final completion:

**Path 1 (MCP Layer):** 1.2 → 2.1 → 6.1 (11-17 hours)
**Path 2 (E2E Infrastructure):** 1.1 → 3.1 → 5.1 → 6.1 (13-19 hours)

**Critical Path:** Path 2 (E2E Infrastructure) - 13-19 hours

## Parallelization Strategy
- **Batch 1:** 3 agents in parallel (E2E infra, MCP framework, unit utilities)
- **Batch 2:** 2 agents in parallel (server tools, resource providers)
- **Batch 3:** 3 agents in parallel (recipe E2E, mealplan E2E, shopping E2E)
- **Batch 4:** 2 agents in parallel (client unit tests, tools unit tests)
- **Batch 5:** 2 agents in parallel (CI/CD integration, Docker tests)
- **Batch 6:** 1 agent (documentation - requires all work complete)

**Tool-level parallelization:** Each agent should use 3-5 parallel tool calls for context gathering and file operations.

**Expected time reduction:** ~75-80% vs sequential (19 hours → ~5 hours with parallelization)

## Expected Outcomes

### Coverage Improvement
- **Before:** 49% overall (7% unit, 38% integration, 0% E2E)
- **After:** 70%+ overall (40% unit, 45% integration, 10% E2E)

### Test Count
- **Before:** 439 tests
- **After:** 600+ tests (161+ new tests)

### Layer Coverage
- **Server (src/server.py):** 2% → 60%+ (98% gap closed)
- **Resources (src/resources/):** 5-7% → 60%+ (93-95% gap closed)
- **Client (src/client.py):** 66% → 80%+ (14% improvement)
- **Tools (src/tools/):** 48-77% → 60-85% (12-8% improvement)

### Test Pyramid Health
- **Before (Inverted):**
  ```
  E2E:         0% (0 tests)     ← Missing critical validation
  Integration: 38% (328 tests)  ← Overweight, brittle
  Unit:        7% (58 tests)    ← Underdeveloped foundation
  ```

- **After (Healthy):**
  ```
  E2E:         10% (50+ tests)  ← Real API + Docker validation
  Integration: 45% (350 tests)  ← Right-sized for integration
  Unit:        40% (200+ tests) ← Strong foundation
  ```

## Stakeholders
- **Michael LoPresti (mike@lopresti.org):** Project maintainer, approval for E2E test credentials
- **MCP Users/Contributors:** Benefit from improved reliability and test coverage
- **CI/CD Pipeline:** Must handle optional E2E tests without breaking PR workflow

## Suggested First Action

**Start Batch 1 in parallel:**

1. **Agent 1 (E2E Infrastructure):** Create E2E test setup
   ```bash
   mkdir -p tests/e2e
   # Follow Phase 1.1 tasks
   ```

2. **Agent 2 (MCP Framework):** Create MCP test utilities
   ```bash
   mkdir -p tests/mcp
   # Follow Phase 1.2 tasks
   ```

3. **Agent 3 (Unit Utilities):** Create unit test helpers
   ```bash
   mkdir -p tests/unit
   # Follow Phase 1.3 tasks
   ```

**Expected completion:** 4-6 hours with 3 agents working in parallel.

**Next step after Batch 1:** Kick off Batch 2 (MCP Layer Validation) - the most critical coverage gap.
