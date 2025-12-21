---
name: github-issue-workflow
description: Execute complete GitHub issue workflow - auto-select or specify issue number to work from branch creation through PR merge
---

# GitHub Issue Workflow

Automates the complete development workflow for GitHub issues: select issue → feature branch → implement → test → PR → merge.

## Usage

**With specific issue:**
```
/github-issue-workflow 21
```

**Auto-select most impactful issue:**
```
/github-issue-workflow
```

## Workflow Steps

When this skill is invoked, execute the following workflow:

### 1. Select Issue

**If issue number provided:**
- Fetch issue details: `gh issue view <number> --json number,title,body,labels`

**If no issue number (auto-select):**
- List open issues: `gh issue list --state open --json number,title,labels`
- Select most impactful based on:
  - Priority: Labels with "high" priority first
  - Type: "enhancement" over "bug" (unless critical bug)
  - Dependencies: Issues blocking other work
  - Effort: Quick wins (low effort, high impact) preferred

### 2. Create Feature Branch

Follow the git workflow pattern from CLAUDE.md:

```bash
# Determine branch prefix
# enhancement → feature/
# bug → fix/

git checkout main
git pull origin main
git checkout -b <prefix>/issue-<number>-<short-description>
```

Examples:
- `feature/issue-21-categories-crud`
- `fix/issue-6-bulk-operations`

### 3. Implement Fix

Read the issue body for implementation tasks and requirements.

**Standard implementation pattern:**
1. Check OpenAPI spec if implementing new endpoints
2. Add client methods to `src/client.py`
3. Add tool functions to appropriate `src/tools/*.py` file
4. Add MCP tool wrappers in `src/server.py`
5. Write comprehensive tests in `tests/test_tools_*.py`
6. Update `CHANGELOG.md` with changes

**Follow existing patterns:**
- Look at similar existing implementations
- Match error handling patterns
- Use consistent naming conventions
- Include docstrings with examples

### 4. Test Implementation

**Run tests:**
```bash
pytest tests/ -v
```

**Type checking:**
```bash
mypy src/
```

**Fix any failures before proceeding.**

### 5. Commit and Push

```bash
git add .
git commit -m "<type>: <description>

<details>

Fixes #<number>"
```

Commit types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `test:` - Adding tests
- `refactor:` - Code refactoring

```bash
git push origin <branch-name>
```

### 6. Create Pull Request

```bash
gh pr create \
  --title "<Type> #<number>: <Title>" \
  --body "Fixes #<number>

## Changes
- <summary of changes>

## Testing
- <testing performed>
"
```

### 7. Wait for CI

```bash
gh pr checks
# or watch live:
gh run watch
```

**CI must pass before merging:**
- ✅ Syntax check (ruff)
- ✅ Tests (pytest)
- ✅ Type checking (mypy)
- ✅ Docker build

### 8. Merge PR

**After CI passes:**
```bash
gh pr merge --squash
```

**Update local main:**
```bash
git checkout main
git pull origin main
```

## Decision-Making Guidelines

### Selecting Most Impactful Issue

When auto-selecting (no issue number provided):

**Priority order:**
1. **Quick wins** - Low effort, high impact (completes existing features)
2. **High priority labels** - Issues labeled "high priority"
3. **Blocking issues** - Issues that unblock other work
4. **User-facing features** - New functionality over internal improvements

**Examples:**
- Issue with 3 simple CRUD operations > Issue with complex new system
- Completing partial implementation > Starting new feature
- Bug affecting users > Internal refactoring

### Implementation Strategy

**When implementing:**
- Read issue body carefully for specific requirements
- Check for linked issues or dependencies
- Look at similar existing code for patterns
- Start with simplest implementation first
- Add comprehensive tests (aim for >80% coverage)

**When stuck:**
- Check OpenAPI spec for endpoint details
- Look for similar implementations in codebase
- Test endpoint manually with curl before implementing
- Ask user for clarification if requirements unclear

## Example: Full Workflow

```bash
# User invokes: /work-issue 24

# 1. Fetch issue
$ gh issue view 24
#24: Add Cookbooks management (full CRUD)

# 2. Create branch
$ git checkout -b feature/issue-24-cookbooks-crud

# 3. Implement (following issue checklist)
- Create src/tools/cookbooks.py
- Add methods to src/client.py
- Add MCP tools to src/server.py
- Write tests/test_tools_cookbooks.py
- Update CHANGELOG.md

# 4. Test
$ pytest tests/test_tools_cookbooks.py -v
$ mypy src/

# 5. Commit and push
$ git add .
$ git commit -m "feat: add cookbooks management (full CRUD)

- Implement list, create, get, update, delete cookbooks
- Add bulk update operation
- Comprehensive tests with 95% coverage

Fixes #24"
$ git push origin feature/issue-24-cookbooks-crud

# 6. Create PR
$ gh pr create --title "Feature #24: Add Cookbooks management" --body "..."

# 7. Wait for CI
$ gh run watch

# 8. Merge after CI passes
$ gh pr merge --squash
$ git checkout main
$ git pull origin main
```

## Notes

- **Use Task tool for autonomous work:** This skill provides the workflow pattern, but actual implementation should use `Task` tool with `general-purpose` agent for autonomous execution
- **Follow CLAUDE.md patterns:** All git workflow, testing, and deployment patterns are documented in CLAUDE.md
- **One issue at a time:** Complete full workflow for one issue before starting another
- **CI is required:** Never merge without passing CI checks

## Related Documentation

- `CLAUDE.md` - Full git workflow and deployment pipeline
- `API_GAP_ANALYSIS.md` - Prioritized list of missing features
- GitHub Issues - Detailed implementation requirements
