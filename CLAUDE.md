# Mealie MCP Server

This directory contains the Mealie MCP (Model Context Protocol) server implementation.

## Development

### Git Workflow

**IMPORTANT:** Use feature branches and pull requests for all changes:

1. **Create a feature branch** for each issue:
   ```bash
   git checkout -b fix/issue-6-bulk-operations
   ```

2. **Make your changes** and commit:
   ```bash
   git add .
   git commit -m "fix: description of fix"
   ```

3. **Push the branch** and create a PR:
   ```bash
   git push origin fix/issue-6-bulk-operations
   gh pr create --title "Fix #6: Description" --body "Fixes #6"
   ```

4. **Wait for CI to pass** before merging:
   ```bash
   gh pr checks  # View CI status
   gh run watch  # Watch CI run
   ```

5. **Merge the PR** after CI passes:
   ```bash
   gh pr merge --squash  # Or merge via GitHub UI
   ```

6. **Update local main** after merge:
   ```bash
   git checkout main
   git pull origin main
   ```

**Benefits:**
- CI validates changes before they reach main
- Easy to review and revert if needed
- Clean git history with squash merges
- Automatic issue closing via PR references

### Primary API Reference

When implementing new endpoints or debugging existing ones, **always consult the OpenAPI specification** as the primary source of truth:

```bash
curl -s https://recipe.vilo.network/openapi.json | python3 -m json.tool
```

The OpenAPI spec provides:
- Exact endpoint paths and HTTP methods
- Request/response schemas with field names and types
- Required vs optional parameters
- Authentication requirements
- Multipart form-data structures

### Example: Finding Endpoint Details

```python
import json, sys

# Get the OpenAPI spec
spec = json.load(open('openapi.json'))

# Look up a specific endpoint
endpoint = spec['paths']['/api/recipes/{slug}/image']['put']
print(json.dumps(endpoint, indent=2))

# Get schema details
schema = spec['components']['schemas']['Body_update_recipe_image_api_recipes__slug__image_put']
print(json.dumps(schema, indent=2))
```

### Testing Endpoints

Test endpoints directly before implementing MCP tools:

```bash
# Example: Upload recipe image
curl -X PUT "https://recipe.vilo.network/api/recipes/test-recipe/image" \
  -H "Authorization: Bearer $MEALIE_API_TOKEN" \
  -F "image=@test.jpg" \
  -F "extension=jpg"
```

## Code Structure

```
mcp/mealie/
├── src/
│   ├── client.py           # MealieClient - HTTP client wrapping Mealie API
│   ├── server.py           # FastMCP server - exposes MCP tools
│   └── tools/              # Tool implementations by category
│       ├── recipes.py      # Recipe management tools
│       ├── mealplans.py    # Meal planning tools
│       ├── shopping.py     # Shopping list tools
│       ├── foods.py        # Foods & units management
│       ├── organizers.py   # Categories, tags, tools
│       └── parser.py       # Ingredient parsing
├── CHANGELOG.md            # Version history
├── README.md               # User documentation
└── requirements.txt        # Python dependencies
```

## Implementation Pattern

When adding new endpoints:

1. **Check OpenAPI spec** - Verify endpoint exists and understand the schema
2. **Add client method** - Implement in `client.py` with proper error handling
3. **Add tool function** - Create wrapper in appropriate `tools/*.py` file
4. **Add MCP tool** - Expose via `@mcp.tool()` decorator in `server.py`
5. **Update CHANGELOG** - Document the new feature
6. **Test manually** - Verify with direct API calls before MCP integration

## Common Issues

### Multipart Form Data

Mealie uses multipart/form-data for file uploads. In httpx:
- File uploads go in `files={...}` parameter
- Text fields go in `data={...}` parameter

```python
files = {'image': ('filename.jpg', file_bytes, 'image/jpeg')}
data = {'extension': 'jpg'}
response = client.put(url, files=files, data=data)
```

### Authentication

All requests require Bearer token authentication:

```python
headers = {"Authorization": f"Bearer {api_token}"}
```

The MealieClient handles this automatically via `self.client` (httpx.Client with default headers).

## Useful OpenAPI Queries

```bash
# List all endpoints
curl -s https://recipe.vilo.network/openapi.json | \
  python3 -c "import json, sys; spec=json.load(sys.stdin); print('\n'.join(spec['paths'].keys()))"

# Get all endpoints by tag
curl -s https://recipe.vilo.network/openapi.json | \
  python3 -c "
import json, sys
spec = json.load(sys.stdin)
by_tag = {}
for path, methods in spec['paths'].items():
    for method, details in methods.items():
        if 'tags' in details:
            for tag in details['tags']:
                by_tag.setdefault(tag, []).append(f'{method.upper()} {path}')
for tag in sorted(by_tag.keys()):
    print(f'\n{tag}:')
    for endpoint in by_tag[tag]:
        print(f'  {endpoint}')
"
```

## Version Management

- Use semantic versioning (MAJOR.MINOR.PATCH)
- Update CHANGELOG.md with each release
- Tag releases in git: `git tag v1.x.x && git push --tags`
- Build and push Docker image with version tag
- Update parent project's `.mcp.json` to reference new version

## Deploying MCP Changes

**IMPORTANT:** Code changes do NOT take effect immediately. The MCP server runs in a Docker container, so changes must go through the full deployment pipeline:

### Deployment Pipeline

1. **Commit changes** to the submodule:
   ```bash
   cd mcp/mealie
   git add .
   git commit -m "Description of changes"
   ```

2. **Push to remote** to trigger CI:
   ```bash
   git push origin main
   ```

3. **Wait for CI build** (GitHub Actions):
   - CI automatically builds Docker image on push
   - Check status: `gh run list --limit 1`
   - Wait for completion (~30 seconds)
   - Image pushed to `ghcr.io/mdlopresti/mealie-mcp:main`

4. **Pull new image** in parent project:
   - **Option A:** Restart Claude Code/session (if using `--pull=always`)
   - **Option B:** Manual pull: `docker pull ghcr.io/mdlopresti/mealie-mcp:main`

5. **Verify changes** are active:
   - Test the modified tool/endpoint
   - Check that new behavior works as expected

### Quick Reference

```bash
# Full deployment workflow
cd mcp/mealie
git add . && git commit -m "fix: your changes"
git push origin main

# Wait for CI (check with gh CLI)
gh run watch

# Restart Claude Code to pull new image
# (if .mcp.json has --pull=always)
```

### Common Pitfall

❌ **Don't test immediately after committing** - Changes won't be active until the new Docker image is pulled!

✅ **Always wait for CI → pull image → then test**

### For Tagged Releases

For version releases (e.g., v1.6.3):

```bash
git tag v1.6.3
git push origin v1.6.3  # Triggers release CI
# Then update parent .mcp.json to use the specific tag
```

## Debugging Mealie Server

When debugging issues with the Mealie API itself (not the MCP server), check the Mealie server logs:

```bash
# Get the Mealie pod name
kubectl get pod -n mealie

# View logs from the Mealie pod
kubectl logs -f <pod-name> -n mealie

# Example
kubectl logs -f mealie-7d8f9b5c4-xyz12 -n mealie
```

This helps diagnose 500 errors or other API issues that originate from the Mealie server rather than the MCP client.
