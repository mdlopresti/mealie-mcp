# Branch Protection Setup Guide

## Problem Solved

Previously, the `test.yml` workflow was running both:
1. **Standalone** (on push/PR) → creating checks like `Python Syntax Check`
2. **Via docker.yml** workflow_call → creating checks like `Run Tests / Python Syntax Check`

This caused duplicate status checks and confusion about which ones to require in branch protection.

**Solution**: Modified `test.yml` to only run via `workflow_call`, eliminating duplicates.

## Required Status Checks

To enable branch protection on the `main` branch, add these **exact** status check names:

1. `Run Tests / Python Syntax Check`
2. `Run Tests / Type Checking with mypy`
3. `Run Tests / Smoke Tests with Coverage`
4. `build`

## Setup Instructions

### Option 1: GitHub Web UI

1. Go to repository **Settings** → **Branches**
2. Click **Add branch protection rule**
3. Set **Branch name pattern**: `main`
4. Check **Require status checks to pass before merging**
5. Check **Require branches to be up to date before merging**
6. In the search box, type and select each check:
   - `Run Tests / Python Syntax Check`
   - `Run Tests / Type Checking with mypy`
   - `Run Tests / Smoke Tests with Coverage`
   - `build`
7. Optionally enable:
   - **Require approvals** (recommend 1)
   - **Require signed commits**
   - **Include administrators**
8. Click **Create** or **Save changes**

### Option 2: GitHub CLI

```bash
# Enable branch protection with required status checks
gh api repos/mdlopresti/mealie-mcp/branches/main/protection \
  -X PUT \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Run Tests / Python Syntax Check",
      "Run Tests / Type Checking with mypy",
      "Run Tests / Smoke Tests with Coverage",
      "build"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

### Verification

After setting up branch protection, verify the configuration:

```bash
# View current branch protection settings
gh api repos/mdlopresti/mealie-mcp/branches/main/protection \
  --jq '.required_status_checks.contexts'
```

Expected output:
```json
[
  "Run Tests / Python Syntax Check",
  "Run Tests / Type Checking with mypy",
  "Run Tests / Smoke Tests with Coverage",
  "build"
]
```

## How It Works

### Workflow Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Event: Push to main or PR to main                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  v
┌─────────────────────────────────────────────────────────────┐
│ docker.yml: Build and Push Docker Image                     │
│                                                              │
│  Job 1: test (workflow_call)                                │
│    └─> Calls test.yml (creates "Run Tests / ..." checks)    │
│                                                              │
│  Job 2: build (depends on test)                             │
│    └─> Builds Docker image (creates "build" check)          │
└─────────────────────────────────────────────────────────────┘
```

### Status Check Names

When a workflow calls another workflow via `workflow_call`, GitHub creates check names with the format:

```
<caller-job-name> / <called-job-name>
```

Example:
- Caller: `docker.yml` has job named `test` (line 15-17)
- Called: `test.yml` has jobs named `syntax-check`, `type-check`, `smoke-test`
- Result: Checks named `Run Tests / Python Syntax Check`, etc.

The job **name** (not the job ID) is used in the check name:
- Job ID: `syntax-check` (line 16 in test.yml)
- Job Name: `Python Syntax Check` (line 17 in test.yml)
- Check Name: `Run Tests / Python Syntax Check`

## Troubleshooting

### Status Checks Not Appearing

If status checks don't appear in the branch protection UI:

1. **Wait for a workflow run**: Status checks only appear after running at least once on a PR
2. **Check workflow triggers**: Ensure workflows run on `pull_request` events
3. **Verify check names**: Use `gh api` to see actual check names:
   ```bash
   gh api repos/mdlopresti/mealie-mcp/commits/$(git rev-parse HEAD)/check-runs \
     --jq '.check_runs[] | .name'
   ```

### Wrong Check Names

If you see unexpected check names:

1. Check for duplicate workflow triggers (should only be in docker.yml)
2. Verify job names match expected format
3. Look for other workflows that might create similar checks

### Checks Always Failing

If required checks always fail:

1. View the workflow run: `gh run list --workflow=docker.yml --limit 1`
2. Check logs: `gh run view <run-id> --log`
3. Verify all jobs pass: `gh run view <run-id>`

## Maintenance

When adding new test jobs to `test.yml`:

1. Add the job to `test.yml`
2. Verify it runs successfully via docker.yml
3. Add the new check name to branch protection: `Run Tests / <new-job-name>`

## Related Files

- `.github/workflows/test.yml` - Test workflow (workflow_call only)
- `.github/workflows/docker.yml` - Calls test.yml, builds Docker image
- `.github/workflows/release.yml` - Calls test.yml for releases

## References

- [GitHub Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Required Status Checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging)
- [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
