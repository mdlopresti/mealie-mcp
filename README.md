# Mealie MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that enables AI assistants to interact with [Mealie](https://mealie.io/) for recipe management, meal planning, and shopping lists.

## Features

### Tools (24 total)

**Recipes**
- `mealie_recipes_search` - Search recipes by name, tags, or categories
- `mealie_recipes_get` - Get full recipe details including ingredients and instructions
- `mealie_recipes_list` - List all recipes with pagination

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

### Resources

- `recipes://list` - Browse all recipes
- `recipes://{slug}` - View specific recipe
- `mealplans://current` - Current week's meal plan
- `mealplans://today` - Today's meals
- `mealplans://{date}` - Specific date's meals
- `shopping://lists` - All shopping lists
- `shopping://{list_id}` - Specific shopping list

## Prerequisites

- Docker (or Podman)
- A running Mealie instance
- Mealie API token

## Quick Start

### 1. Build the Docker Image

```bash
git clone https://github.com/YOUR_USERNAME/mealie-mcp.git
cd mealie-mcp
docker build -t mealie-mcp:latest .
```

### 2. Get Your API Token

1. Log into your Mealie instance
2. Go to **User Settings** (click your name in sidebar)
3. Navigate to **API Tokens**
4. Create a new token (e.g., "MCP Server")
5. Copy the token immediately (it won't be shown again)

### 3. Configure Claude Code

Add to `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "mealie": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "MEALIE_URL=https://your-mealie-instance.com",
        "-e", "MEALIE_API_TOKEN=your-api-token-here",
        "mealie-mcp:latest"
      ]
    }
  }
}
```

Then add `mealie` to your `~/.claude/settings.json`:

```json
{
  "allowedMcpServers": [
    { "serverName": "mealie" }
  ]
}
```

### 4. Test the Connection

Restart Claude Code and try:
```
Can you search for recipes in Mealie?
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
    │   └── shopping.py
    └── resources/      # MCP resource implementations
        ├── recipes.py
        ├── mealplans.py
        └── shopping.py
```

## Security

- **Never commit API tokens** - Use environment variables
- The API token has full access to your Mealie account
- Consider creating a dedicated Mealie user for the MCP server

## Requirements

- Python 3.12+
- Mealie v1.0+ (tested with v3.6.1)

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.

## Related

- [Mealie](https://mealie.io/) - Self-hosted recipe manager
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [FastMCP](https://github.com/jlowin/fastmcp) - Python MCP framework
