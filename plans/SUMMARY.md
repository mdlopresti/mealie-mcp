# Implementation Plans Summary

This directory contains implementation plans for the Mealie MCP server.

## Active Plans

### [High-Value Features Plan](./high-value-features-plan.md)
**Status:** Active (planning complete, ready for execution)
**Goal:** Add 24 new MCP tools for user engagement and automation
**Impact:** Expands MCP tool count from 88 → 112 tools

**Features:**
- **Batch 1 - User Features (4 phases, parallel):**
  - Recipe ratings management (3 tools)
  - Recipe favorites management (3 tools)
  - Recipe suggestions (1 tool)
  - Shared recipes management (5 tools)

- **Batch 2 - Automation (3 phases, parallel):**
  - Webhooks management (5 tools)
  - Recipe actions management (5 tools)
  - Event notifications management (6 tools)

- **Batch 3 - Enhanced (3 phases, parallel):**
  - Recipe assets management (TBD tools)
  - Group/household management (TBD tools)
  - Recipe export formats (TBD tools)

**Time Estimate:**
- Sequential: ~10 coding sessions
- Parallel: ~3 batches (70% reduction)

**Next Action:** Dispatch Batch 1 to 4 parallel agents

---

## Completed Plans

### [Testing Gaps Plan](./completed/testing-gaps-plan.md)
**Status:** Archived (superseded by high-value features plan)
**Completed:** 2025-12-23
**Notes:** Testing infrastructure already exists (334 unit tests, 42 E2E tests, 191 MCP tests). Focus shifted to high-value features.

---

## Roadmap

See [roadmap.md](./roadmap.md) for the current active work and batch status.

---

## Plan Format

All implementation plans follow the `project-phase-decomposition` pattern:

### Required Sections
1. **Summary** - 2-3 sentences on what this delivers
2. **Complexity Assessment** - Systems affected, classification, reasoning
3. **Affected Systems** - List of files/modules/components
4. **Dependencies** - Prerequisites, external services, libraries
5. **Assumptions** - Documented uncertainties
6. **Risks** - Identified risks with mitigation strategies
7. **Batch Execution Plan** - Table showing parallelization strategy
8. **Detailed Phases** - Per-phase breakdown with tasks, effort, acceptance criteria
9. **Critical Path** - Longest dependency chain
10. **Parallelization Strategy** - Agent coordination approach
11. **Stakeholders** - Who needs this and why
12. **Suggested First Action** - Specific instruction for kickoff

### Quality Checklist (Per Phase)
- [ ] All client methods implemented with error handling
- [ ] All tool functions created with JSON responses
- [ ] All MCP tools registered with @mcp.tool decorator
- [ ] Unit tests written (mock-based, no network)
- [ ] E2E tests written (live API, with cleanup)
- [ ] MCP tests written (tool invocation validation)
- [ ] All tests passing locally and in CI
- [ ] CHANGELOG.md updated
- [ ] PR merged to main
- [ ] Roadmap updated (phase archived)

---

## Git Workflow

Each phase follows feature branch workflow:

1. Create feature branch: `git checkout -b feat/feature-name`
2. Implement and commit: `git commit -m "feat: description (#issue)"`
3. Push and create PR: `gh pr create --title "..." --body "..."`
4. Wait for CI to pass
5. Merge: `gh pr merge --squash`
6. Update roadmap (move to archive)

---

## Testing Strategy

Each phase requires 3 test layers:

1. **Unit Tests** (mock-based)
   - Test tool functions with mocked MealieClient
   - Verify parameter validation, error handling, response formatting
   - Location: `tests/unit/test_tools_*.py`
   - Target: 3-5 tests per tool function

2. **E2E Tests** (live API)
   - Test against real Mealie instance
   - Validate full workflows (create → update → delete)
   - Use unique IDs and cleanup fixtures
   - Location: `tests/e2e/test_*_workflows.py`
   - Target: 1-2 tests per tool function

3. **MCP Tests** (tool invocation)
   - Test MCP tool registration
   - Validate parameter schemas
   - Test invocation and response format
   - Location: `tests/mcp/test_server_tools.py`
   - Target: 1 test per MCP tool

---

## Quick Reference

**Current Status:**
- Total MCP tools: 88
- Planned additions: 24 tools (Batch 1-2)
- Target total: 112+ tools

**Priority Order:**
1. ⭐⭐⭐ High-Value User Features (Batch 1)
2. ⭐⭐ Integration & Automation (Batch 2)
3. ⭐ Enhanced Features (Batch 3)

**Key Files:**
- `plans/roadmap.md` - Active work tracking
- `plans/high-value-features-plan.md` - Detailed implementation plan
- `plans/completed/` - Archived completed work
- `CHANGELOG.md` - Version history
