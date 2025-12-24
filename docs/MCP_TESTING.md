# MCP Server Testing Guide

This guide explains how to test the Mealie MCP server's tool registration and invocation.

## Overview

MCP server tests verify that:
- Tools are properly registered with FastMCP
- Tools can be invoked programmatically
- Tool responses follow MCP protocol
- Parameters are validated correctly
- Resources are registered properly

## Test Structure

```
tests/mcp/
├── __init__.py
├── conftest.py         # MCP test fixtures
├── helpers.py          # Protocol validation utilities
└── test_server_basic.py # Example MCP server tests
```

## Key Concepts

### MCP Tools

MCP tools are registered via the `@mcp.tool()` decorator in `src/server.py`. Each tool:
- Has a unique name (e.g., `mealie_recipes_search`)
- Defines parameters with type annotations
- Returns a string (usually JSON)
- Is wrapped by FastMCP as a `FunctionTool`

### Tool Invocation

Tools are invoked asynchronously via FastMCP:

```python
tools = await mcp.get_tools()
tool = tools["mealie_recipes_search"]
result = await tool.run({"query": "pasta", "limit": 10})
```

The result is a `ToolResult` object with:
- `content`: List of content objects (usually `TextContent`)
- Each content item has `type` and `text` attributes

## Testing MCP Tools

### 1. Test Tool Registration

Verify tools are registered:

```python
@pytest.mark.asyncio
async def test_recipe_tools_registered(mcp_server):
    tools = await mcp_server.get_tools()
    tool_names = list(tools.keys())

    assert "mealie_recipes_search" in tool_names
    assert "mealie_recipes_create" in tool_names
```

### 2. Test Tool Invocation

Use the `invoke_mcp_tool` fixture to call tools with mocked MealieClient:

```python
@pytest.mark.asyncio
async def test_invoke_recipe_search(invoke_mcp_tool, mock_mealie_client):
    # Configure mock response
    mock_mealie_client.get.return_value = {
        "items": [{"name": "Pasta", "slug": "pasta"}],
        "total": 1
    }

    # Invoke tool
    result = await invoke_mcp_tool("mealie_recipes_search", query="pasta")

    # Validate response
    validation = validate_mcp_response(result)
    assert validation["valid"]

    # Extract text content
    text = extract_tool_result_text(result)
    data = json.loads(text)
    assert data["count"] == 1
```

### 3. Test Parameter Validation

Verify tool parameters are correct:

```python
@pytest.mark.asyncio
async def test_tool_parameters(mcp_server):
    tools = await mcp_server.get_tools()
    tool = tools["mealie_recipes_create"]

    # Check required parameters
    params = tool.parameters
    assert "name" in params.get("required", [])
```

### 4. Test MCP Protocol Compliance

Use validation helpers to check MCP protocol:

```python
from tests.mcp.helpers import validate_mcp_response

result = await invoke_mcp_tool("ping")
validation = validate_mcp_response(result)

assert validation["valid"]
assert validation["content_count"] > 0
assert validation["has_text"]
```

## Fixtures

### `mcp_server`

Returns the configured FastMCP server instance from `src.server`.

```python
def test_server_name(mcp_server):
    assert mcp_server.name == "mealie"
```

### `mock_mealie_client`

Provides a mocked MealieClient with:
- Context manager support (`__enter__`, `__exit__`)
- HTTP method mocks (`get`, `post`, `put`, `delete`)
- Configurable return values

```python
def test_with_mock(mock_mealie_client):
    mock_mealie_client.get.return_value = {"items": []}
```

### `invoke_mcp_tool`

Async fixture that invokes MCP tools with mocked client:

```python
@pytest.mark.asyncio
async def test_tool(invoke_mcp_tool, mock_mealie_client):
    mock_mealie_client.get.return_value = {"data": "test"}
    result = await invoke_mcp_tool("tool_name", param1="value")
```

## Helper Functions

### `validate_tool_registration(server, tool_name)`

Check if a tool is registered.

### `validate_tool_params(tool, expected_params)`

Validate tool parameters match expectations.

### `validate_mcp_response(result)`

Validate MCP protocol compliance of ToolResult.

### `extract_tool_result_text(result)`

Extract text content from ToolResult.

## Testing Resources

MCP resources are tested similarly:

```python
@pytest.mark.asyncio
async def test_resources(mcp_server):
    resources = await mcp_server.get_resources()
    resource_uris = [r.uri for r in resources]

    assert "recipes://list" in resource_uris
```

## Running MCP Tests

Run all MCP server tests:

```bash
pytest tests/mcp/ -v
```

Run specific test file:

```bash
pytest tests/mcp/test_server_basic.py -v
```

Run with coverage:

```bash
pytest tests/mcp/ --cov=src.server --cov-report=term-missing
```

## Best Practices

1. **Always mock MealieClient**: Use `invoke_mcp_tool` fixture to avoid real HTTP calls
2. **Validate MCP protocol**: Use `validate_mcp_response()` to ensure compliance
3. **Test both success and error paths**: Configure mock to return errors
4. **Check parameter validation**: Verify required vs optional params
5. **Test async properly**: Use `@pytest.mark.asyncio` for async tests

## Common Patterns

### Testing Error Handling

```python
@pytest.mark.asyncio
async def test_error_handling(invoke_mcp_tool, mock_mealie_client):
    # Mock HTTP error
    from src.client import MealieAPIError
    mock_mealie_client.get.side_effect = MealieAPIError("API error", 500)

    result = await invoke_mcp_tool("mealie_recipes_get", slug="test")

    # Tool should return error in text content
    text = extract_tool_result_text(result)
    assert "error" in text.lower()
```

### Testing Complex Tool Parameters

```python
@pytest.mark.asyncio
async def test_complex_params(invoke_mcp_tool, mock_mealie_client):
    mock_mealie_client.post.return_value = {"id": "recipe-123"}

    result = await invoke_mcp_tool(
        "mealie_recipes_create",
        name="Test Recipe",
        ingredients=["2 cups flour", "1 tsp salt"],
        tags=["Dinner"]
    )

    # Verify mock was called correctly
    assert mock_mealie_client.post.called
```

## Coverage Goals

MCP server tests should cover:
- ✅ Tool registration (all 70+ tools)
- ✅ Tool invocation with valid params
- ✅ Tool invocation with invalid params
- ✅ Error handling and error responses
- ✅ Parameter validation
- ✅ Resource registration
- ✅ MCP protocol compliance

## Troubleshooting

### "Tool not found" error

Ensure the tool name matches exactly (case-sensitive):

```python
tools = await mcp.get_tools()
print(list(tools.keys()))  # List all available tools
```

### Async test not running

Add `@pytest.mark.asyncio` decorator:

```python
@pytest.mark.asyncio
async def test_async_function():
    ...
```

### Mock not being used

Verify the module path in the patch is correct:

```python
# Should match where MealieClient is imported
patch('src.tools.recipes.MealieClient')
```

## Example: Complete Test

```python
@pytest.mark.asyncio
async def test_complete_workflow(invoke_mcp_tool, mock_mealie_client):
    """Complete test showing all best practices."""
    # 1. Configure mock
    mock_mealie_client.get.return_value = {
        "items": [{"name": "Pasta", "slug": "pasta"}],
        "total": 1
    }

    # 2. Invoke tool
    result = await invoke_mcp_tool(
        "mealie_recipes_search",
        query="pasta",
        limit=10
    )

    # 3. Validate MCP protocol
    validation = validate_mcp_response(result)
    assert validation["valid"], validation.get("error")

    # 4. Extract and verify content
    text = extract_tool_result_text(result)
    data = json.loads(text)

    assert "recipes" in data
    assert data["count"] == 1

    # 5. Verify mock was called correctly
    mock_mealie_client.get.assert_called_once()
    call_args = mock_mealie_client.get.call_args
    assert call_args[1]["params"]["search"] == "pasta"
```
