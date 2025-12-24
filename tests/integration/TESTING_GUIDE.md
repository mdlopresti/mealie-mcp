# MCP Integration Testing Guide

## Phase 1.2: MCP Server Test Framework - COMPLETED

This document describes the MCP testing infrastructure implemented in Phase 1.2.

## Implementation Summary

### Created Files

1. **tests/integration/conftest.py** - Integration test fixtures
   - `mcp_server` - FastMCP server instance
   - `mcp_tool_invoker` - Tool invocation with mocked HTTP
   - Sample data fixtures (recipes, mealplans, shopping lists, etc.)

2. **tests/utils/mcp_test_helpers.py** - MCP validation utilities
   - Tool registration validation
   - Parameter schema validation
   - Response structure validation
   - JSON schema validation
   - Error response validation
   - Data validation helpers

3. **tests/integration/test_mcp_tools_example.py** - Example integration tests
   - Tool registration tests
   - Response validation tests
   - Parameter handling tests
   - Error handling tests
   - Data flow integration tests
   - Complex scenario tests
   - Edge case tests

4. **Documentation**
   - tests/integration/README.md - Comprehensive testing guide
   - tests/utils/README.md - Utilities documentation
   - This file - Implementation notes

### Key Features

#### 1. MCP Tool Invocation
```python
result = await mcp_tool_invoker(
    "mealie_recipes_search",
    mock_response={"items": [...], "total": 3},
    query="pasta"
)
```

#### 2. Response Validation
```python
# Validate MCP protocol compliance
assert_valid_mcp_response(result)

# Extract and validate JSON
data = extract_json_from_result(result)
assert_has_fields(data, ["items", "total"])
```

#### 3. Schema Validation
```python
assert_json_response_schema(result, {
    "type": "object",
    "properties": {
        "items": {"type": "array"}
    },
    "required": ["items"]
})
```

#### 4. Tool Registration Testing
```python
assert await validate_tool_exists(mcp_server, "mealie_recipes_search")
assert_tool_params(tool, {"query": False}, {"query": "string"})
```

## Usage

### Running Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test class
pytest tests/integration/test_mcp_tools_example.py::TestToolRegistration -v

# Run with coverage
pytest tests/integration/ --cov=src/tools --cov=src/server
```

### Writing New Tests

See `tests/integration/test_mcp_tools_example.py` for patterns:

```python
import pytest
from tests.utils.mcp_test_helpers import (
    validate_tool_exists,
    assert_valid_mcp_response,
    extract_json_from_result
)

class TestMyNewTool:
    @pytest.mark.asyncio
    async def test_tool_registered(self, mcp_server):
        assert await validate_tool_exists(mcp_server, "mealie_my_tool")

    @pytest.mark.asyncio
    async def test_tool_invocation(self, mcp_tool_invoker):
        result = await mcp_tool_invoker(
            "mealie_my_tool",
            mock_response={"data": "test"}
        )
        assert_valid_mcp_response(result)
```

## Known Issues / Future Work

### Response Format Inconsistencies

Some tools wrap responses in success/error objects while others return data directly:

**Direct response:**
```json
{
  "items": [...],
  "total": 3
}
```

**Wrapped response:**
```json
{
  "success": true,
  "message": "Recipe created",
  "recipe": {...}
}
```

**Impact:** Example tests may fail due to these inconsistencies.

**Solution:** When writing tests for actual tools, check the tool implementation to understand its response format.

### Next Steps

1. **Standardize Response Format** - Consider standardizing all tool responses
2. **Add More Example Tests** - Cover more tool categories (timeline, webhooks, etc.)
3. **Integration with CI** - Add integration tests to CI pipeline
4. **Performance Testing** - Add benchmarks for tool invocation
5. **Error Scenario Coverage** - Expand error handling tests

## Benefits

### For Developers

1. **Fast Feedback** - Tests run in <1s without real API calls
2. **Isolation** - Test MCP layer independently of Mealie API
3. **Debugging** - Clear validation errors point to issues
4. **Confidence** - Verify MCP protocol compliance

### For the Project

1. **Regression Prevention** - Catch breaking changes early
2. **Documentation** - Tests serve as usage examples
3. **Quality** - Validate parameter schemas and responses
4. **Maintainability** - Reusable helpers reduce test code

## Architecture

```
tests/
├── integration/           # MCP protocol integration tests
│   ├── conftest.py       # Fixtures (mcp_server, mcp_tool_invoker)
│   ├── test_mcp_tools_example.py  # Example tests
│   └── README.md         # Usage documentation
│
├── utils/                 # Reusable test utilities
│   ├── mcp_test_helpers.py   # Validation helpers
│   └── README.md         # API documentation
│
└── unit/                  # Unit tests (existing)
    ├── conftest.py       # Unit test fixtures
    └── builders.py       # Test data builders
```

## Comparison with Existing Tests

| Feature | Unit Tests | MCP Integration | E2E Tests |
|---------|-----------|-----------------|-----------|
| Speed | ⚡ Instant | ⚡ Fast (<1s) | 🐌 Slow |
| Isolation | ✅ High | ✅ Medium | ❌ Low |
| Real API | ❌ No | ❌ No | ✅ Yes |
| MCP Protocol | ❌ No | ✅ Yes | ✅ Yes |
| Client Layer | ✅ Yes | ✅ Yes | ✅ Yes |
| Tool Layer | ❌ No | ✅ Yes | ✅ Yes |

## Related Documentation

- [Integration Tests README](README.md) - Detailed usage guide
- [MCP Helpers README](../utils/README.md) - API reference
- [MCP Protocol Spec](https://modelcontextprotocol.io/) - Protocol docs
- [FastMCP Documentation](https://github.com/jlowin/fastmcp) - Framework docs

## Credits

Implemented as part of Phase 1.2 of the Testing Infrastructure plan.
