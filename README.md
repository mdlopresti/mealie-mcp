# Mealie MCP Server

[![Home Assistant App](https://github.com/warinthestars/mealie-mcp/actions/workflows/ha-addon.yml/badge.svg)](https://github.com/warinthestars/mealie-mcp/actions/workflows/ha-addon.yml)
[![Build and Push Docker Image](https://github.com/warinthestars/mealie-mcp/actions/workflows/docker.yml/badge.svg)](https://github.com/warinthestars/mealie-mcp/actions/workflows/docker.yml)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that enables AI assistants to interact with [Mealie](https://mealie.io/) for recipe management, meal planning, and shopping lists.

It can run three ways:

| | Best for | How clients connect |
| --- | --- | --- |
| **[Home Assistant app](#option-1-home-assistant-app)** | Home Assistant OS/Supervised users, especially with Mealie installed as an app too | HTTP: `http://<ha-ip>:8099/mcp` |
| **[Docker, stdio](#option-2-docker-stdio)** | A single client (Claude Code / Claude Desktop) on the same computer | The client starts the container itself |
| **[Docker, HTTP](#option-3-docker-http-server)** | A shared server for several clients or machines | HTTP: `http://<host>:8099/mcp` |

> This repository is a fork of [mdlopresti/mealie-mcp](https://github.com/mdlopresti/mealie-mcp) that adds the Home Assistant app and HTTP transport.

## Features

### Tools (134 total; highlights below)

**Recipes**
- `mealie_recipes_search` - Search recipes by name, tags, or categories
- `mealie_recipes_get` - Get full recipe details including ingredients and instructions
- `mealie_recipes_list` - List all recipes with pagination
- `mealie_recipes_create` - Create a new recipe
- `mealie_recipes_create_from_url` - Import recipe by scraping a URL
- `mealie_recipes_update` - Update an existing recipe
- `mealie_recipes_update_structured_ingredients` - Update recipe with structured ingredients from parser
- `mealie_recipes_delete` - Delete a recipe

**Meal Planning**
- `mealie_mealplans_list` - List meal plans for a date range
- `mealie_mealplans_today` - Get today's meals
- `mealie_mealplans_get` - Get specific meal plan entry
- `mealie_mealplans_get_date` - Get meals for a specific date
- `mealie_mealplans_create` - Create meal plan entry
- `mealie_mealplans_update` - Update meal plan entry
- `mealie_mealplans_delete` - Delete meal plan entry
- `mealie_mealplans_random` - Get random meal suggestion

**Shopping Lists**
- `mealie_shopping_lists_list` - List all shopping lists
- `mealie_shopping_lists_get` - Get shopping list with items
- `mealie_shopping_lists_create` - Create new shopping list
- `mealie_shopping_lists_delete` - Delete shopping list
- `mealie_shopping_items_add` - Add item to list
- `mealie_shopping_items_add_bulk` - Add multiple items at once
- `mealie_shopping_items_check` - Mark item checked/unchecked
- `mealie_shopping_items_delete` - Remove item from list
- `mealie_shopping_add_recipe` - Add recipe ingredients to list
- `mealie_shopping_generate_from_mealplan` - Generate shopping list from meal plan
- `mealie_shopping_clear_checked` - Clear all checked items

**Full API & maintenance**
- `mealie_api_request` / `mealie_api_endpoints` / `mealie_api_schema` - Call and discover any Mealie endpoint
- `mealie_recipes_reparse` - Turn imported plain-text ingredients into structured ones, server-side
- `mealie_recipes_audit` - Find recipes missing images, servings, categories, parsed ingredients and more
- `mealie_recipes_patch` / `mealie_recipes_set_tools` - Edit any recipe field; assign kitchen tools
- `mealie_recipes_fill_missing_images` - Add images from each recipe's source page

**Foods & Labels**
- `mealie_foods_list` - List foods with `search`, `query_filter` (e.g. `labelId IS NULL`) and a compact `slim` view
- `mealie_foods_merge` - Merge a duplicate food into another
- `mealie_labels_list` / `_create` / `_update` / `_delete` - Manage the labels that group foods on shopping lists

**Backups** (admin token)
- `mealie_backups_create` - Create a full Mealie backup before large changes
- `mealie_backups_list` / `_get_download_url` / `_delete` - Manage existing backups (restore stays in Mealie's UI)

**Ingredient Parsing**
- `mealie_parser_ingredient` - Parse single ingredient string to structured format
- `mealie_parser_ingredients_batch` - Parse multiple ingredient strings at once

### Resources

- `recipes://list` - Browse all recipes
- `recipes://{slug}` - View specific recipe
- `mealplans://current` - Current week's meal plan
- `mealplans://today` - Today's meals
- `mealplans://{date}` - Specific date's meals
- `shopping://lists` - All shopping lists
- `shopping://{list_id}` - Specific shopping list

## Before you start

You need a running Mealie instance (v1.0+) and a **Mealie API token**:

1. Log into Mealie as the user the assistant should act as.
2. Click your avatar → **API Tokens** (`/user/profile/api-tokens`).
3. Create a token (e.g. "MCP Server") and copy it immediately. It's only shown once.

## Option 1: Home Assistant app

1. **Settings → Apps → App store → ⋮ → Repositories**, add `https://github.com/warinthestars/mealie-mcp`.
2. Install **Mealie MCP Server** and open its **Configuration** tab:
   - `mealie_url`: how the app reaches Mealie. **If Mealie is an app on the same Home Assistant**, use its internal hostname and container port, e.g. `http://db21ed7f-mealie:9001` for the alexbelgium Mealie app. Not `localhost`, `mealie.local` or an Ingress URL.
   - `mealie_api_token`: the token from above.
   - `mcp_auth_token`: a long letters-and-digits password that clients must send as a bearer token.
3. Start the app and check its **Log** tab.
4. Connect a client:
   - **Claude Desktop (LAN):** use `mcp-remote` in `claude_desktop_config.json`.
   - **Claude custom connector:** needs a public HTTPS URL, e.g. via the Cloudflared app.
   - **Claude Code:** `claude mcp add --transport http ...`
   - **Home Assistant Assist:** Model Context Protocol integration.

**Full step-by-step instructions, client configs and troubleshooting:
[mealie_mcp/DOCS.md](mealie_mcp/DOCS.md)** (also shown on the app's Documentation tab in Home Assistant).

> It's a Home Assistant **app** (add-on), installed from the app store, not HACS.

## Option 2: Docker, stdio

The MCP client launches the container for each session and talks to it over stdin/stdout.

```bash
docker pull ghcr.io/warinthestars/mealie-mcp:latest
# or build it yourself:
git clone https://github.com/warinthestars/mealie-mcp.git && cd mealie-mcp && docker build -t mealie-mcp:latest .
```

**Claude Code**: add to `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "mealie": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "MEALIE_URL=https://your-mealie-instance.com",
        "-e", "MEALIE_API_TOKEN=your-api-token-here",
        "ghcr.io/warinthestars/mealie-mcp:latest"
      ]
    }
  }
}
```

**Claude Desktop**: put the same `mealie` block in `claude_desktop_config.json`
(**Settings → Developer → Edit Config**) and fully restart Claude Desktop.

Then ask: *"Can you search for recipes in Mealie?"*

## Option 3: Docker, HTTP server

Run one long-lived server that any number of clients can share:

```bash
docker run -d --name mealie-mcp --restart unless-stopped -p 8099:8099 \
  -e MCP_TRANSPORT=http \
  -e MEALIE_URL=http://192.168.1.50:9925 \
  -e MEALIE_API_TOKEN=your-api-token \
  -e MCP_AUTH_TOKEN=$(openssl rand -hex 32) \
  ghcr.io/warinthestars/mealie-mcp:latest
```

Clients connect to `http://<host>:8099/mcp` with the header
`Authorization: Bearer <MCP_AUTH_TOKEN>`. See
[connecting clients](mealie_mcp/DOCS.md#5-connect-an-ai-client) for Claude
Desktop, custom connector and Claude Code configs. They're the same as for the
Home Assistant app.

## Configuration reference

| Variable | Default | Description |
| --- | --- | --- |
| `MEALIE_URL` | (required) | Mealie base URL, no trailing slash |
| `MEALIE_API_TOKEN` | (required) | Mealie API token |
| `MCP_TRANSPORT` | `stdio` | `stdio` or `http` (the Home Assistant app always uses `http`) |
| `MCP_HOST` | `0.0.0.0` | HTTP bind address |
| `MCP_PORT` | `8099` | HTTP port |
| `MCP_PATH` | `/mcp` | HTTP endpoint path |
| `MCP_AUTH_TOKEN` | (empty) | Bearer token required on every HTTP request; empty disables auth |
| `MCP_LOG_LEVEL` | `info` | HTTP server log level |

## Usage Examples

### Clearing Optional Fields

To clear an optional field (remove its value), pass the special sentinel value `"__CLEAR__"`:

```python
# Remove recipe association from a meal plan entry
mealie_mealplans_update(
    mealplan_id="abc-123",
    recipe_id="__CLEAR__"
)

# Clear the title from an entry
mealie_mealplans_update(
    mealplan_id="abc-123",
    title="__CLEAR__"
)

# Clear the text/notes from an entry
mealie_mealplans_update(
    mealplan_id="abc-123",
    text="__CLEAR__"
)

# Clear multiple fields at once
mealie_mealplans_update(
    mealplan_id="abc-123",
    recipe_id="__CLEAR__",
    title="__CLEAR__",
    text="__CLEAR__"
)
```

To leave a field unchanged, simply omit it from the call:

```python
# Update only the date, preserving all other fields
mealie_mealplans_update(
    mealplan_id="abc-123",
    meal_date="2025-12-25"
)
```

## Development

### Local Development (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MEALIE_URL=https://your-mealie-instance.com
export MEALIE_API_TOKEN=your-api-token

# Run server
python -m src.server
```

### Running Tests

**Unit/Integration Tests** (mock API, always run):
```bash
# Run all tests except E2E
pytest -m "not e2e"

# Run all tests with coverage
pytest --cov=src --cov-report=term-missing
```

**End-to-End Tests** (optional):

E2E tests validate against a real Mealie instance. Two modes are supported:

**Docker E2E Tests** (recommended - isolated environment):
```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run Docker E2E tests
pytest tests/e2e/test_docker_e2e.py -v

# These tests:
# - Start a containerized Mealie instance automatically
# - Run tests in isolated environment
# - Clean up containers and data after tests
# - Require Docker/Podman to be running
```

**Live Instance E2E Tests** (test against existing server):
```bash
# Set required environment variables
export MEALIE_E2E_URL="https://your-mealie-instance.com"
export MEALIE_E2E_TOKEN="your-test-api-token"

# Run E2E tests against live instance
pytest -m e2e

# These tests are skipped if environment variables are not set
```

See [tests/e2e/README.md](tests/e2e/README.md) for detailed E2E testing documentation.

Note: Live instance E2E tests create and delete test resources. Use a test/development instance, not production!

### Project Structure

```
mealie-mcp/
├── Dockerfile           # Container definition
├── requirements.txt     # Python dependencies
├── build.sh            # Build helper script
└── src/
    ├── server.py       # MCP server entry point
    ├── client.py       # Mealie API client
    ├── tools/          # MCP tool implementations
    │   ├── recipes.py
    │   ├── mealplans.py
    │   ├── shopping.py
    │   └── parser.py
    └── resources/      # MCP resource implementations
        ├── recipes.py
        ├── mealplans.py
        └── shopping.py
```

## Security

- **Never commit API tokens** - Use environment variables
- The API token has full access to your Mealie account
- Consider creating a dedicated Mealie user for the MCP server
- In HTTP mode, always set `MCP_AUTH_TOKEN` (`mcp_auth_token` in the app). Anyone with network access and the token can read and modify your Mealie data
- Only publish the HTTP endpoint to the internet (e.g. for Claude custom connectors) over HTTPS with a token set

## Requirements

- Python 3.12+
- Mealie v1.0+ (tested with v3.6.1 and v3.30.0)

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR. Maintainers and AI agents: see [docs/FORK_MAINTENANCE.md](docs/FORK_MAINTENANCE.md) for syncing upstream and releasing.

## Related

- [Mealie](https://mealie.io/) - Self-hosted recipe manager
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [FastMCP](https://github.com/jlowin/fastmcp) - Python MCP framework
