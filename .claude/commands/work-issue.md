---
description: Work on a GitHub issue (auto-select or specify issue number)
argument-hint: [issue-number]
---

Execute the complete GitHub issue workflow from branch creation through PR merge.

**Issue to work on:** $ARGUMENTS

## Workflow Steps

1. **Select Issue**
   - If issue number provided: Fetch details with `gh issue view $ARGUMENTS`
   - If no number: Auto-select most impactful issue from `gh issue list`
     - Priority: High priority labels > Quick wins > Blocking issues > User-facing features

2. **Create Feature Branch**
   - Determine prefix: `feature/` for enhancements, `fix/` for bugs
   - Pattern: `git checkout -b <prefix>/issue-<number>-<description>`

3. **Implement Fix**
   - Check OpenAPI spec if implementing new endpoints
   - Add client methods to `src/client.py`
   - Add tool functions to `src/tools/*.py`
   - Add MCP tool wrappers in `src/server.py`
   - Write tests in `tests/test_tools_*.py`
   - Update `CHANGELOG.md`

4. **Test Implementation**
   - Run: `pytest tests/ -v`
   - Type check: `mypy src/`
   - Fix all failures before proceeding

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "<type>: <description>

   Fixes #<number>"
   git push origin <branch-name>
   ```

6. **Create Pull Request**
   ```bash
   gh pr create --title "<Type> #<number>: <Title>" --body "Fixes #<number>..."
   ```

7. **Wait for CI** - All checks must pass (ruff, pytest, mypy, docker build)

8. **Merge PR** - `gh pr merge --squash` after CI passes

See `.claude/skills/github-issue-workflow/SKILL.md` for detailed guidelines.
