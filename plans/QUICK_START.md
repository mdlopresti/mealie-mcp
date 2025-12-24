# Quick Start Guide - Testing Gaps Implementation

## TL;DR

**Goal:** Fix critical testing gaps in Mealie MCP Server
**Current:** 49% coverage, MCP layer 98% untested, no E2E tests
**Target:** 70%+ coverage, healthy test pyramid, real API validation
**Time:** ~5 hours with parallelization (19 hours sequential)

## Prerequisites

### Required
- [x] Python 3.12+ environment
- [x] Existing test suite passing (439 tests)
- [x] Docker/Podman for container testing

### Needed for E2E Tests
- [ ] Mealie instance URL (recipe.vilo.network)
- [ ] API token with read/write permissions
- [ ] Test account with isolated data

## Start Here - Batch 1 (Foundation)

### Run All 3 Phases in Parallel

**Phase 1.1: E2E Infrastructure** (Agent 1)
```bash
cd /var/home/mike/source/meal-planning/mcp/mealie

# Create structure
mkdir -p tests/e2e

# Your tasks:
# - Create conftest_e2e.py with skip logic
# - Add cleanup fixtures
# - Implement retry helpers
# - Add unique ID generator
# - Document in README

# Verify
pytest tests/e2e/ -v --collect-only  # Should show 0 tests but no errors
```

**Phase 1.2: MCP Test Framework** (Agent 2)
```bash
# Create structure
mkdir -p tests/mcp

# Your tasks:
# - Research FastMCP testing (check fastmcp docs)
# - Create conftest.py with MCP fixtures
# - Add tool invocation helpers
# - Add resource validation utilities
# - Document patterns

# Verify
python -c "from tests.mcp.conftest import *"  # Should import cleanly
```

**Phase 1.3: Unit Test Utilities** (Agent 3)
```bash
# Create structure
mkdir -p tests/unit

# Your tasks:
# - Create mock data builders
# - Add validation helpers
# - Add assertion utilities
# - Refactor existing conftest.py
# - Document patterns

# Verify
python -c "from tests.unit.builders import *"  # Should import cleanly
```

### Batch 1 Acceptance Criteria

- [ ] `tests/e2e/conftest_e2e.py` exists and imports cleanly
- [ ] `tests/mcp/conftest.py` exists with MCP fixtures
- [ ] `tests/unit/conftest.py` exists with mock builders
- [ ] All existing tests still pass: `pytest tests/ -v`
- [ ] No new test failures introduced

## After Batch 1 - Continue

### Batch 2: MCP Layer Tests (CRITICAL)
**Unblocks after:** Batch 1 complete
**Phases:** 2.1 (Server Tools), 2.2 (Resource Providers)
**Goal:** Close the 98% MCP layer gap

### Batch 3: E2E Workflows
**Unblocks after:** Batch 1 complete
**Phases:** 3.1 (Recipes), 3.2 (Mealplans), 3.3 (Shopping)
**Goal:** Validate against real Mealie API

### Batch 4: Pyramid Rebalancing
**Unblocks after:** Batch 1 complete
**Phases:** 4.1 (Client Unit), 4.2 (Tools Unit)
**Goal:** Build strong unit test foundation

### Batch 5: Integration
**Unblocks after:** Batch 3 complete
**Phases:** 5.1 (CI/CD), 5.2 (Docker)
**Goal:** Automated E2E testing

### Batch 6: Documentation
**Unblocks after:** ALL complete
**Phases:** 6.1 (Coverage Report)
**Goal:** Celebrate success! 🎉

## Running Tests

### Unit Tests (Fast)
```bash
pytest tests/unit/ -v
# Expected: <1 second
```

### Integration Tests (Current)
```bash
pytest tests/ -v -k "not e2e"
# Expected: ~13 seconds
```

### E2E Tests (Optional)
```bash
export MEALIE_E2E_URL="https://recipe.vilo.network"
export MEALIE_E2E_TOKEN="your-token-here"
pytest tests/e2e/ -v --timeout=300
# Expected: 1-3 minutes
```

### All Tests
```bash
pytest tests/ -v --cov=src --cov-report=term
# Expected: 15-20 seconds (excluding E2E)
```

### Coverage Report
```bash
pytest tests/ -v \
  --cov=src \
  --cov-report=term \
  --cov-report=html

# Open htmlcov/index.html in browser
```

## Checking Progress

### Current Coverage
```bash
pytest tests/ -v --cov=src --cov-report=json
python -c "import json; data=json.load(open('coverage.json')); print(f\"Total: {data['totals']['percent_covered']:.1f}%\")"
```

### By Layer
```bash
# Server layer
pytest tests/mcp/ -v --cov=src/server --cov-report=term

# Resources layer
pytest tests/mcp/ -v --cov=src/resources --cov-report=term

# Client layer
pytest tests/unit/ -v --cov=src/client --cov-report=term
```

### Test Count
```bash
pytest tests/ --collect-only | grep "test session starts" -A 1
```

## Troubleshooting

### E2E Tests Skip
**Problem:** E2E tests don't run
**Solution:** Set `MEALIE_E2E_URL` environment variable
```bash
export MEALIE_E2E_URL="https://recipe.vilo.network"
pytest tests/e2e/ -v
```

### E2E Tests Fail
**Problem:** Network errors, timeouts
**Solution:** Check Mealie instance is running
```bash
curl -H "Authorization: Bearer $MEALIE_E2E_TOKEN" \
  $MEALIE_E2E_URL/api/app/about
```

### Coverage Doesn't Increase
**Problem:** New tests don't improve coverage
**Solution:** Ensure you're testing actual source code, not mocks
```bash
# Check which files are covered
pytest tests/ -v --cov=src --cov-report=term-missing
```

### CI/CD E2E Tests Don't Run
**Problem:** GitHub Actions doesn't run E2E tests
**Solution:** E2E tests are opt-in, trigger manually
```bash
# Via GitHub CLI
gh workflow run e2e-manual.yml

# Or use GitHub UI: Actions → E2E Tests → Run workflow
```

## Success Checkpoints

### After Batch 1
- [ ] 3 new test directories created
- [ ] Test infrastructure in place
- [ ] All existing tests still pass
- [ ] No coverage regression

### After Batch 2
- [ ] MCP layer coverage jumps from 2% → 60%+
- [ ] 60+ new MCP tests
- [ ] All 31 tools tested
- [ ] All 7 resources tested

### After Batch 3
- [ ] 37+ E2E tests passing
- [ ] Real API workflows validated
- [ ] Test data cleanup working
- [ ] E2E coverage contribution: ~10%

### After Batch 4
- [ ] Unit test coverage: 40%+ (was 7%)
- [ ] 100+ new unit tests
- [ ] Test suite faster
- [ ] Better test isolation

### After Batch 5
- [ ] E2E tests run in GitHub Actions
- [ ] Docker container tested
- [ ] MCP stdio communication validated

### Final (After Batch 6)
- [ ] 70%+ total coverage ✅
- [ ] Healthy test pyramid ✅
- [ ] Documentation complete ✅
- [ ] **Ship it!** 🚀

## Reference Files

- **Detailed Plan:** `plans/testing-gaps-plan.md`
- **Active Roadmap:** `plans/roadmap.md`
- **Completed Work:** `plans/completed/roadmap-archive.md`
- **Executive Summary:** `plans/SUMMARY.md`
- **This Guide:** `plans/QUICK_START.md`

## Getting Help

### Questions About...
- **Phase details:** See `plans/testing-gaps-plan.md`
- **What to work on next:** See `plans/roadmap.md`
- **Coverage targets:** See `plans/SUMMARY.md`
- **How to start:** You're reading it! 😄

### Common Issues
- E2E setup problems → Check prerequisites section
- MCP testing confusion → Research FastMCP docs first
- Coverage not improving → Check term-missing report
- CI/CD issues → Review workflow files in `.github/workflows/`

## Quick Commands

```bash
# Full test suite
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=term

# Only unit tests (fast)
pytest tests/unit/ -v

# Only E2E tests (requires env vars)
pytest tests/e2e/ -v

# Only MCP tests
pytest tests/mcp/ -v

# Check what would run
pytest tests/ -v --collect-only

# Run specific test file
pytest tests/mcp/test_server_tools.py -v

# Run specific test
pytest tests/mcp/test_server_tools.py::test_tool_registration -v

# Stop on first failure
pytest tests/ -v -x

# Show print statements
pytest tests/ -v -s

# Parallel execution (if you have pytest-xdist)
pytest tests/ -v -n auto
```

---

**Ready to start? Begin with Batch 1 phases 1.1, 1.2, and 1.3 in parallel!**
