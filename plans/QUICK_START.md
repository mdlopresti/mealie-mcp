# High-Value Features - Quick Start Guide

## Executive Summary

**Goal:** Add 24 new MCP tools for recipe ratings, favorites, sharing, and automation  
**Current:** 88 tools → **Target:** 112+ tools  
**Time:** ~3 batches (parallel execution) vs ~10 sessions (sequential)  
**Reduction:** 70% time savings with parallelization

---

## What We're Building

### Batch 1: User Engagement Features ⭐⭐⭐
**4 parallel agents, ~1 session each**

| Feature | Tools | Endpoints | Value |
|---------|-------|-----------|-------|
| Recipe Ratings | 3 | POST/GET ratings | Track favorite recipes |
| Recipe Favorites | 3 | POST/DELETE/GET favorites | Personal collections |
| Recipe Suggestions | 1 | GET suggestions | Meal planning automation |
| Shared Recipes | 5 | Full CRUD + access | Share with non-users |

**Total:** 12 new MCP tools

### Batch 2: Automation Features ⭐⭐
**3 parallel agents, ~1 session each**

| Feature | Tools | Endpoints | Value |
|---------|-------|-----------|-------|
| Webhooks | 5 | Full CRUD + test | External integrations |
| Recipe Actions | 5 | Full CRUD + trigger | Custom automation |
| Event Notifications | 6 | Full CRUD + test | Alerts & reminders |

**Total:** 16 new MCP tools

### Batch 3: Enhanced Features ⭐
**3 parallel agents, ~1 session each**

| Feature | Tools | Status | Value |
|---------|-------|--------|-------|
| Recipe Assets | TBD | Research needed | PDFs, videos |
| Household Mgmt | TBD | Research needed | Members, permissions |
| Export Formats | TBD | Some exist | PDF, ZIP exports |

**Total:** TBD new MCP tools

---

## Execution Plan

### Phase Flow
```
Batch 1 (Parallel)
├─ Phase 1.1: Ratings      (Agent 1) ─┐
├─ Phase 1.2: Favorites    (Agent 2) ─┤
├─ Phase 1.3: Suggestions  (Agent 3) ─┼─→ Batch 2 (Parallel)
└─ Phase 1.4: Shared       (Agent 4) ─┘    ├─ Phase 2.1: Webhooks   (Agent 1) ─┐
                                            ├─ Phase 2.2: Actions    (Agent 2) ─┼─→ Batch 3
                                            └─ Phase 2.3: Notify     (Agent 3) ─┘
```

### Time Estimate
- **Batch 1:** ~1 session (4 agents in parallel)
- **Batch 2:** ~1 session (3 agents in parallel)
- **Batch 3:** ~1 session (3 agents in parallel)
- **Total:** ~3 sessions vs ~10 sequential

---

## Getting Started

### Prerequisites
1. Access to Mealie API at https://recipe.vilo.network
2. Git configured for feature branch workflow
3. GitHub CLI (`gh`) for PR management
4. Python environment with httpx, pytest

### Kick Off Batch 1

Dispatch to 4 agents simultaneously:

**Agent 1: Ratings**
```bash
git checkout -b feat/ratings-management
# Implement Phase 1.1 following high-value-features-plan.md
# - Add 3 client methods to src/client.py
# - Add 3 tool functions to src/tools/recipes.py
# - Register 3 MCP tools in src/server.py
# - Write 15 tests (9 unit + 3 E2E + 3 MCP)
# - Update CHANGELOG.md
# - Create PR, wait for CI, merge
```

**Agent 2: Favorites**
```bash
git checkout -b feat/favorites-management
# Implement Phase 1.2 (same pattern as ratings)
```

**Agent 3: Suggestions**
```bash
git checkout -b feat/recipe-suggestions
# Implement Phase 1.3 (simpler - only 1 endpoint)
```

**Agent 4: Shared Recipes**
```bash
git checkout -b feat/shared-recipes
# Implement Phase 1.4 (creates new tools/sharing.py file)
```

---

## Implementation Pattern

Each phase follows this template:

### 1. Add Client Methods (`src/client.py`)
```python
def rate_recipe(self, user_id: str, recipe_slug: str, rating: float) -> dict:
    """Rate a recipe (0.0-5.0)."""
    response = self.post(
        f"/api/users/{user_id}/ratings/{recipe_slug}",
        json={"rating": rating}
    )
    return response
```

### 2. Create Tool Functions (`src/tools/recipes.py`)
```python
def ratings_set(slug: str, rating: float) -> str:
    """Set rating for a recipe via MCP tool."""
    try:
        with MealieClient() as client:
            result = client.rate_recipe("self", slug, rating)
            return json.dumps({"success": True, "rating": result}, indent=2)
    except MealieAPIError as e:
        return json.dumps({"error": str(e)}, indent=2)
```

### 3. Register MCP Tools (`src/server.py`)
```python
@mcp.tool()
def mealie_ratings_set(slug: str, rating: float) -> str:
    """Set rating for a recipe (0.0-5.0 stars)."""
    return ratings_set(slug, rating)
```

### 4. Write Tests

**Unit Test** (`tests/unit/test_tools_recipes.py`):
```python
def test_ratings_set_success():
    mock_client = Mock()
    mock_client.rate_recipe.return_value = {"rating": 4.5}
    
    with patch('src.tools.recipes.MealieClient') as MockClient:
        MockClient.return_value.__enter__.return_value = mock_client
        result = ratings_set("test-recipe", 4.5)
        result_dict = json.loads(result)
        assert result_dict["success"] is True
```

**E2E Test** (`tests/e2e/test_recipe_workflows.py`):
```python
@pytest.mark.e2e
def test_rate_recipe_workflow(e2e_client, unique_id, test_cleanup_all):
    # Create recipe
    recipe_slug = e2e_client.post("/api/recipes", json={"name": f"Test {unique_id}"})
    test_cleanup_all["recipes"].append(recipe_slug)
    
    # Rate it
    rating = e2e_client.post(f"/api/users/self/ratings/{recipe_slug}", json={"rating": 4.5})
    assert rating["rating"] == 4.5
```

**MCP Test** (`tests/mcp/test_server_tools.py`):
```python
@pytest.mark.asyncio
async def test_ratings_set_invocation(invoke_mcp_tool):
    result = await invoke_mcp_tool(
        "mealie_ratings_set",
        slug="test-recipe",
        rating=4.5
    )
    validation = validate_mcp_response(result)
    assert validation["valid"]
```

---

## Quality Checklist (Per Phase)

Before marking phase complete:

- [ ] All client methods added to `src/client.py`
- [ ] All tool functions created in `src/tools/*.py`
- [ ] All MCP tools registered in `src/server.py`
- [ ] Unit tests written (mock-based, no network)
- [ ] E2E tests written (live API, with cleanup)
- [ ] MCP tests written (tool invocation validation)
- [ ] All tests passing locally (`pytest`)
- [ ] CI passing on feature branch
- [ ] CHANGELOG.md updated
- [ ] PR created and merged
- [ ] Roadmap updated (phase moved to archive)

---

## Common Commands

```bash
# Create feature branch
git checkout -b feat/ratings-management

# Run tests locally
pytest tests/unit/test_tools_recipes.py -v
pytest tests/e2e/test_recipe_workflows.py -v -m e2e
pytest tests/mcp/test_server_tools.py -v

# Push and create PR
git push origin feat/ratings-management
gh pr create --title "feat: Recipe Ratings Management" --body "Implements ratings management (Phase 1.1)"

# Check CI status
gh pr checks
gh run watch

# Merge after CI passes
gh pr merge --squash

# Update roadmap
# Move Phase 1.1 to plans/completed/roadmap-archive.md
```

---

## Success Metrics

**After Batch 1:**
- ✅ 12 new MCP tools (88 → 100)
- ✅ ~60 new tests (unit + E2E + MCP)
- ✅ Users can rate, favorite, and share recipes
- ✅ 4 PRs merged to main

**After Batch 2:**
- ✅ 16 new MCP tools (100 → 116)
- ✅ ~75 new tests
- ✅ Webhooks, actions, notifications enabled
- ✅ 3 PRs merged to main

**After Batch 3:**
- ✅ All planned tools implemented
- ✅ Full test coverage
- ✅ Documentation updated
- ✅ Ready for v2.0.0 release

---

## Troubleshooting

**Tests failing in CI but passing locally?**
- Check environment variables (MEALIE_BASE_URL, MEALIE_API_TOKEN)
- Verify Docker image built correctly
- Check GitHub Actions logs for details

**E2E tests flaky?**
- Use unique IDs per test (`unique_id` fixture)
- Ensure cleanup fixtures delete test data
- Add retry logic for network failures

**MCP tests failing?**
- Verify tool registration in `src/server.py`
- Check parameter schemas match expectations
- Validate JSON response format

---

## Next Steps

1. **Review the detailed plan:** See [high-value-features-plan.md](./high-value-features-plan.md)
2. **Check the roadmap:** See [roadmap.md](./roadmap.md)
3. **Start Batch 1:** Dispatch to 4 agents
4. **Monitor progress:** Track PRs and CI status
5. **Iterate:** Move completed phases to archive, start Batch 2

---

## Questions?

- **Detailed plan:** `plans/high-value-features-plan.md`
- **Roadmap tracking:** `plans/roadmap.md`
- **Implementation patterns:** Existing code in `src/tools/recipes.py`
- **Test examples:** `tests/unit/test_tools_recipes.py`
