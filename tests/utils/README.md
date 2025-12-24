# MCP Test Utilities

Reusable testing utilities for MCP protocol validation and testing.

## Overview

The `tests/utils/` directory provides helper functions for testing MCP tools:

- **Tool Registration Validation** - Verify tools are registered correctly
- **Parameter Schema Validation** - Check parameter types and requirements
- **Response Structure Validation** - Ensure MCP protocol compliance
- **Error Handling Validation** - Test error responses
- **Data Validation** - Assert data structure and content

## Module: mcp_test_helpers.py

See `tests/utils/mcp_test_helpers.py` for full API documentation.

### Quick Reference

**Tool Registration:**
- `validate_tool_exists(server, tool_name)` - Check if tool registered
- `get_tool_metadata(server, tool_name)` - Get tool metadata
- `assert_tool_params(tool, params, types)` - Validate parameters

**Response Validation:**
- `assert_valid_mcp_response(result)` - Validate MCP protocol
- `extract_json_from_result(result)` - Parse JSON response
- `assert_json_response_schema(result, schema)` - Validate JSON schema

**Data Validation:**
- `assert_has_fields(data, fields)` - Check required fields
- `assert_field_type(data, field, type)` - Validate field type
- `assert_list_length(data, field, length)` - Check list length

See [Integration Testing Guide](../integration/README.md) for usage examples.
