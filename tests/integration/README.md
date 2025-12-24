# MCP Integration Testing Framework

This directory contains the integration testing framework for validating MCP protocol interactions in the Mealie MCP server.

## Overview

Integration tests validate the MCP layer without hitting real API endpoints. They test:

1. **MCP Tool Registration** - Tools are registered with correct metadata
2. **Parameter Validation** - Tool parameters match expected schemas
3. **Response Structure** - Responses follow MCP protocol requirements
4. **Error Handling** - Tools handle errors gracefully
5. **Data Flow** - Integration between tools and client layer works correctly

## Directory Structure

```
tests/integration/
├── README.md                       # This file
├── __init__.py                     # Package initialization
├── conftest.py                     # Pytest fixtures for integration tests
└── test_mcp_tools_example.py      # Example integration tests

tests/utils/
├── __init__.py                     # Package initialization
└── mcp_test_helpers.py            # MCP testing utilities
```

## Quick Start

### Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/test_mcp_tools_example.py -v

# Run specific test class
pytest tests/integration/test_mcp_tools_example.py::TestToolRegistration -v

# Run specific test
pytest tests/integration/test_mcp_tools_example.py::TestToolRegistration::test_recipe_search_tool_exists -v
```

### Writing Your First Integration Test

```python
import pytest
from tests.utils.mcp_test_helpers import (
    validate_tool_exists,
    assert_valid_mcp_response,
    extract_json_from_result,
    assert_has_fields
)

class TestMyNewTool:
    """Test my new MCP tool."""

    @pytest.mark.asyncio
    async def test_tool_registered(self, mcp_server):
        """Test that my tool is registered."""
        assert await validate_tool_exists(mcp_server, "mealie_my_new_tool")

    @pytest.mark.asyncio
    async def test_tool_invocation(self, mcp_tool_invoker):
        """Test invoking my tool."""
        result = await mcp_tool_invoker(
            "mealie_my_new_tool",
            mock_response={"data": "test"},
            param1="value1"
        )

        # Validate MCP response structure
        assert_valid_mcp_response(result)

        # Extract and validate JSON
        data = extract_json_from_result(result)
        assert_has_fields(data, ["data"])
```

## Key Concepts

### Fixtures

#### `mcp_server`
The FastMCP server instance with all tools registered.

```python
@pytest.mark.asyncio
async def test_example(self, mcp_server):
    tools = await mcp_server.get_tools()
    assert "mealie_recipes_search" in tools
```

#### `mcp_tool_invoker`
Callable to invoke MCP tools with mocked HTTP responses.

```python
@pytest.mark.asyncio
async def test_example(self, mcp_tool_invoker):
    result = await mcp_tool_invoker(
        "mealie_recipes_search",
        mock_response={"items": [...], "total": 3},
        query="pasta"
    )
```

**Parameters:**
- `tool_name` (str): Name of the tool to invoke
- `mock_response` (dict): JSON response to return from HTTP calls
- `status_code` (int): HTTP status code (default: 200)
- `**kwargs`: Tool parameters

#### Sample Data Fixtures

Use builder-based fixtures for consistent test data:

- `sample_recipes` - List of 3 sample recipes
- `sample_mealplans` - List of meal plan entries
- `sample_shopping_lists` - Shopping lists with items
- `sample_organizers` - Tags, categories, and tools
- `sample_foods_and_units` - Foods and units

```python
@pytest.mark.asyncio
async def test_with_sample_data(self, mcp_tool_invoker, sample_recipes):
    result = await mcp_tool_invoker(
        "mealie_recipes_search",
        mock_response={"items": sample_recipes, "total": len(sample_recipes)},
        query="pasta"
    )
```

### Validation Helpers

#### Tool Registration

```python
from tests.utils.mcp_test_helpers import (
    validate_tool_exists,
    get_tool_metadata,
    validate_tool_schema,
    assert_tool_params
)

# Check if tool exists
assert await validate_tool_exists(mcp_server, "mealie_recipes_search")

# Get tool metadata
metadata = await get_tool_metadata(mcp_server, "mealie_recipes_search")
assert metadata["description"]

# Validate parameter schema
tools = await mcp_server.get_tools()
tool = tools["mealie_recipes_search"]

valid, error = validate_tool_schema(tool, {
    "type": "object",
    "properties": {
        "query": {"type": "string"}
    }
})
assert valid, error

# Assert parameters (raises AssertionError if invalid)
assert_tool_params(
    tool,
    {"query": False, "limit": False},  # Both optional
    {"query": "string", "limit": "integer"}  # Type validation
)
```

#### Response Validation

```python
from tests.utils.mcp_test_helpers import (
    validate_mcp_response,
    assert_valid_mcp_response,
    extract_text_from_result,
    extract_json_from_result,
    validate_json_response_schema,
    assert_json_response_schema
)

# Validate MCP response structure
validation = validate_mcp_response(result)
assert validation["valid"], validation["error"]
assert validation["has_text"]

# Or use assertion helper
assert_valid_mcp_response(result)

# Extract text content
text = extract_text_from_result(result)
assert "expected text" in text

# Extract JSON data
data = extract_json_from_result(result)
assert "items" in data

# Validate JSON schema
valid, error = validate_json_response_schema(result, {
    "type": "object",
    "properties": {
        "items": {"type": "array"}
    },
    "required": ["items"]
})
assert valid, error

# Or use assertion helper
assert_json_response_schema(result, {...})
```

#### Error Validation

```python
from tests.utils.mcp_test_helpers import (
    validate_error_response,
    assert_tool_error
)

# Check if response contains error
is_error, msg = validate_error_response(result, "not found")
assert is_error

# Or use assertion helper
assert_tool_error(result, "not found")
```

#### Data Validation

```python
from tests.utils.mcp_test_helpers import (
    assert_has_fields,
    assert_field_type,
    assert_list_length
)

data = extract_json_from_result(result)

# Assert required fields exist
assert_has_fields(data, ["id", "name", "slug"])

# Assert field has correct type
assert_field_type(data, "total", int)

# Assert list length
assert_list_length(data, "items", min_length=1)
assert_list_length(data, "items", expected_length=3)
```

## Testing Patterns

### Pattern 1: Tool Registration Test

```python
class TestToolRegistration:
    @pytest.mark.asyncio
    async def test_tool_exists(self, mcp_server):
        """Test that tool is registered."""
        assert await validate_tool_exists(mcp_server, "mealie_my_tool")

    @pytest.mark.asyncio
    async def test_tool_parameters(self, mcp_server):
        """Test tool has correct parameters."""
        tools = await mcp_server.get_tools()
        tool = tools["mealie_my_tool"]

        assert_tool_params(
            tool,
            {"param1": True, "param2": False},  # param1 required, param2 optional
            {"param1": "string", "param2": "integer"}
        )
```

### Pattern 2: Response Validation Test

```python
class TestResponseValidation:
    @pytest.mark.asyncio
    async def test_response_structure(self, mcp_tool_invoker):
        """Test response follows MCP protocol."""
        result = await mcp_tool_invoker(
            "mealie_my_tool",
            mock_response={"data": "test"}
        )

        # Validate MCP structure
        assert_valid_mcp_response(result)

        # Validate JSON content
        data = extract_json_from_result(result)
        assert_has_fields(data, ["data"])
```

### Pattern 3: Parameter Handling Test

```python
class TestParameterHandling:
    @pytest.mark.asyncio
    async def test_with_parameters(self, mcp_tool_invoker, sample_data):
        """Test tool handles parameters correctly."""
        result = await mcp_tool_invoker(
            "mealie_my_tool",
            mock_response=sample_data,
            param1="value1",
            param2=42
        )

        data = extract_json_from_result(result)
        # Validate parameter effects
        assert data["processed"] is True
```

### Pattern 4: Error Handling Test

```python
class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_not_found_error(self, mcp_tool_invoker):
        """Test tool handles not found error."""
        result = await mcp_tool_invoker(
            "mealie_my_tool",
            mock_response={"detail": "Not found"},
            status_code=404,
            id="nonexistent"
        )

        # Verify error is present in response
        text = extract_text_from_result(result)
        assert text  # Should have some response
```

### Pattern 5: Integration Flow Test

```python
class TestDataFlowIntegration:
    @pytest.mark.asyncio
    async def test_create_and_retrieve(self, mcp_tool_invoker, sample_data):
        """Test creating and retrieving data."""
        # Create
        create_result = await mcp_tool_invoker(
            "mealie_items_create",
            mock_response=sample_data,
            name="Test Item"
        )

        created = extract_json_from_result(create_result)
        assert_has_fields(created, ["id"])

        # Retrieve
        get_result = await mcp_tool_invoker(
            "mealie_items_get",
            mock_response=sample_data,
            id=created["id"]
        )

        retrieved = extract_json_from_result(get_result)
        assert retrieved["id"] == created["id"]
```

## Best Practices

### 1. Use Builders for Test Data

Always use builders from `tests/unit/builders.py` for consistent test data:

```python
from tests.unit.builders import build_recipe, build_mealplan

recipe = build_recipe(name="Test Recipe", slug="test-recipe")
mealplan = build_mealplan(recipeId=recipe["id"])
```

### 2. Test One Thing Per Test

Each test should validate a single aspect:

```python
# Good - tests one thing
async def test_recipe_has_name_field(self, ...):
    data = extract_json_from_result(result)
    assert_has_fields(data, ["name"])

# Bad - tests too many things
async def test_recipe_validation(self, ...):
    # Tests fields, types, relationships, errors...
```

### 3. Use Descriptive Test Names

Test names should clearly describe what's being tested:

```python
# Good
async def test_recipe_search_returns_empty_list_when_no_matches(self, ...):

# Bad
async def test_search(self, ...):
```

### 4. Validate MCP Protocol First

Always validate MCP protocol compliance before checking data:

```python
# Good
assert_valid_mcp_response(result)  # MCP protocol
data = extract_json_from_result(result)  # Then data
assert_has_fields(data, ["items"])

# Bad
data = extract_json_from_result(result)  # Assumes valid MCP
```

### 5. Use Assertion Helpers

Prefer assertion helpers over manual checks for better error messages:

```python
# Good - clear error message
assert_has_fields(data, ["id", "name"])
# AssertionError: Missing required fields: ['name']. Available fields: ['id']

# Bad - unclear error
assert "id" in data and "name" in data
# AssertionError: (no helpful context)
```

## Common Issues

### Issue 1: Tool Not Found

**Error:** `ValueError: Tool 'mealie_my_tool' not found`

**Solution:** Ensure tool is registered in `src/server.py`:

```python
@mcp.tool()
def mealie_my_tool(...):
    ...
```

### Issue 2: JSON Parsing Error

**Error:** `json.JSONDecodeError: Expecting value`

**Solution:** Check that mock response is valid JSON:

```python
# Good
mock_response={"items": [], "total": 0}

# Bad
mock_response="invalid json"
```

### Issue 3: Schema Validation Fails

**Error:** `Schema validation failed: 'items' is a required property`

**Solution:** Ensure mock response matches expected schema:

```python
# Tool expects {"items": [...], "total": int}
mock_response={"items": sample_data, "total": len(sample_data)}
```

### Issue 4: Async Test Not Running

**Error:** Test appears to hang or doesn't run

**Solution:** Add `@pytest.mark.asyncio` decorator:

```python
@pytest.mark.asyncio  # Required for async tests
async def test_my_async_test(self, ...):
    ...
```

## Advanced Topics

### Custom Mock Responses

For complex scenarios, use `mock_mealie_api` fixture:

```python
@pytest.mark.asyncio
async def test_complex_scenario(self, mock_mealie_api):
    with mock_mealie_api as api:
        # Mock different endpoints differently
        api.get("/api/recipes").mock(
            return_value=Response(200, json={"items": [...]})
        )
        api.post("/api/recipes").mock(
            return_value=Response(201, json={"id": "new-recipe"})
        )

        # Now invoke tools...
```

### Testing Error Conditions

Test different HTTP status codes:

```python
@pytest.mark.asyncio
async def test_server_error(self, mcp_tool_invoker):
    result = await mcp_tool_invoker(
        "mealie_recipes_get",
        mock_response={"detail": "Internal Server Error"},
        status_code=500,
        slug="test"
    )

    # Verify error handling
    text = extract_text_from_result(result)
    # Check error is communicated appropriately
```

### Testing Pagination

Test pagination scenarios:

```python
@pytest.mark.asyncio
async def test_pagination(self, mcp_tool_invoker, sample_recipes):
    # Page 1
    result = await mcp_tool_invoker(
        "mealie_recipes_list",
        mock_response={
            "items": sample_recipes[:20],
            "total": 50,
            "page": 1,
            "per_page": 20
        },
        page=1,
        per_page=20
    )

    data = extract_json_from_result(result)
    assert data["page"] == 1
    assert len(data["items"]) == 20
```

## Related Documentation

- [Unit Testing Guide](../unit/README.md) - For isolated function tests
- [MCP Protocol Specification](https://modelcontextprotocol.io/) - Official MCP docs
- [Test Data Builders](../unit/builders.py) - Test data generation
- [FastMCP Documentation](https://github.com/jlowin/fastmcp) - FastMCP framework

## Contributing

When adding new integration tests:

1. Follow existing patterns in `test_mcp_tools_example.py`
2. Use descriptive test names
3. Add docstrings explaining what's tested
4. Use builders for test data
5. Validate MCP protocol compliance
6. Test both success and error cases

## Questions?

- Check existing tests in `test_mcp_tools_example.py` for examples
- Review validation helpers in `tests/utils/mcp_test_helpers.py`
- See unit tests in `tests/unit/` for comparison
