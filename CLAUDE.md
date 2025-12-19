# Mealie MCP Server

This directory contains the Mealie MCP (Model Context Protocol) server implementation.

## Development

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
