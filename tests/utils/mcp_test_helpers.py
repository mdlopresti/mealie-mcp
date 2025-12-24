"""
MCP Testing Utilities

Provides validation functions and helpers for testing MCP protocol compliance.
These utilities help verify that tools follow MCP specifications for:
- Tool registration and metadata
- Parameter schemas (types, required/optional)
- Response format and structure
- Error handling

Usage:
    from tests.utils.mcp_test_helpers import (
        validate_tool_schema,
        validate_tool_response,
        assert_tool_params,
        extract_json_from_result
    )
"""

import json
from typing import Any, Optional
from jsonschema import validate as json_validate, ValidationError


# ============================================================================
# Tool Registration Validation
# ============================================================================

async def validate_tool_exists(server, tool_name: str) -> bool:
    """Check if a tool is registered with the MCP server.

    Args:
        server: FastMCP server instance
        tool_name: Name of the tool to check

    Returns:
        bool: True if tool is registered, False otherwise

    Example:
        assert await validate_tool_exists(mcp_server, "mealie_recipes_search")
    """
    tools = await server.get_tools()
    return tool_name in tools


async def get_tool_metadata(server, tool_name: str) -> dict:
    """Get metadata for a registered tool.

    Args:
        server: FastMCP server instance
        tool_name: Name of the tool

    Returns:
        dict: Tool metadata including name, description, parameters

    Raises:
        ValueError: If tool is not registered

    Example:
        metadata = await get_tool_metadata(mcp_server, "mealie_recipes_search")
        assert metadata["description"]
    """
    tools = await server.get_tools()
    if tool_name not in tools:
        raise ValueError(f"Tool '{tool_name}' not registered")

    tool = tools[tool_name]
    return {
        "name": tool_name,
        "description": tool.description if hasattr(tool, 'description') else None,
        "parameters": tool.parameters if hasattr(tool, 'parameters') else None
    }


def validate_tool_schema(tool, expected_schema: dict) -> tuple[bool, Optional[str]]:
    """Validate that a tool's parameter schema matches expectations.

    Args:
        tool: FastMCP FunctionTool instance
        expected_schema: Expected parameter schema structure
            Example: {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer"}
                },
                "required": ["query"]
            }

    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])

    Example:
        tool = await mcp.get_tools()["mealie_recipes_search"]
        valid, error = validate_tool_schema(tool, {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            }
        })
        assert valid, error
    """
    if not hasattr(tool, 'parameters'):
        return False, "Tool missing 'parameters' attribute"

    actual = tool.parameters
    if not actual:
        if not expected_schema:
            return True, None
        return False, "Tool has no parameters but schema expected"

    # Check type
    if expected_schema.get("type") != actual.get("type"):
        return False, f"Schema type mismatch: expected {expected_schema.get('type')}, got {actual.get('type')}"

    # Check properties
    expected_props = expected_schema.get("properties", {})
    actual_props = actual.get("properties", {})

    for prop_name, prop_schema in expected_props.items():
        if prop_name not in actual_props:
            return False, f"Missing property: {prop_name}"

        # Check property type
        if "type" in prop_schema:
            actual_type = actual_props[prop_name].get("type")
            expected_type = prop_schema["type"]
            if actual_type != expected_type:
                return False, f"Property '{prop_name}' type mismatch: expected {expected_type}, got {actual_type}"

    # Check required fields
    expected_required = set(expected_schema.get("required", []))
    actual_required = set(actual.get("required", []))

    if expected_required != actual_required:
        return False, f"Required fields mismatch: expected {expected_required}, got {actual_required}"

    return True, None


def assert_tool_params(
    tool,
    expected_params: dict[str, bool],
    expected_types: Optional[dict[str, str]] = None
) -> None:
    """Assert that a tool has expected parameters.

    Convenience function that raises AssertionError if validation fails.

    Args:
        tool: FastMCP FunctionTool instance
        expected_params: Dict mapping parameter names to required status
            Example: {"query": False, "limit": False} (both optional)
        expected_types: Optional dict mapping parameter names to types
            Example: {"query": "string", "limit": "integer"}

    Raises:
        AssertionError: If parameters don't match expectations

    Example:
        tool = await mcp.get_tools()["mealie_recipes_search"]
        assert_tool_params(
            tool,
            {"query": False, "tags": False, "limit": False},
            {"query": "string", "limit": "integer"}
        )
    """
    if not hasattr(tool, 'parameters'):
        raise AssertionError("Tool missing 'parameters' attribute")

    params = tool.parameters
    if not params or 'properties' not in params:
        if expected_params:
            raise AssertionError(f"Tool has no parameters but expected: {expected_params}")
        return

    # Check each expected parameter
    actual_props = params['properties']
    required_params = set(params.get('required', []))

    for param_name, is_required in expected_params.items():
        if param_name not in actual_props:
            raise AssertionError(f"Missing parameter: {param_name}")

        # Check required status
        actual_required = param_name in required_params
        if actual_required != is_required:
            raise AssertionError(
                f"Parameter '{param_name}' required status mismatch: "
                f"expected {is_required}, got {actual_required}"
            )

    # Check types if provided
    if expected_types:
        for param_name, expected_type in expected_types.items():
            if param_name not in actual_props:
                raise AssertionError(f"Missing parameter for type check: {param_name}")

            actual_type = actual_props[param_name].get('type')
            if actual_type != expected_type:
                raise AssertionError(
                    f"Parameter '{param_name}' type mismatch: "
                    f"expected {expected_type}, got {actual_type}"
                )


# ============================================================================
# Response Validation
# ============================================================================

def validate_mcp_response(result) -> dict[str, Any]:
    """Validate MCP protocol compliance of a ToolResult.

    Checks that the ToolResult follows MCP protocol requirements:
    - Has content attribute
    - Content is a list
    - Each content item has type and appropriate data

    Args:
        result: ToolResult from FastMCP

    Returns:
        dict with validation results:
            - valid: bool
            - error: str (if invalid)
            - content_count: int
            - has_text: bool
            - text_content: str (if has_text)

    Example:
        result = await invoke_mcp_tool("ping")
        validation = validate_mcp_response(result)
        assert validation["valid"], validation.get("error")
    """
    validation = {
        "valid": True,
        "error": None,
        "content_count": 0,
        "has_text": False,
        "text_content": None
    }

    # Check for content attribute
    if not hasattr(result, 'content'):
        validation["valid"] = False
        validation["error"] = "Result missing 'content' attribute"
        return validation

    # Content should be a list
    content = result.content
    if not isinstance(content, list):
        validation["valid"] = False
        validation["error"] = f"Content should be list, got {type(content).__name__}"
        return validation

    validation["content_count"] = len(content)

    # Check each content item
    texts = []
    for i, item in enumerate(content):
        # Should have type
        if not hasattr(item, 'type'):
            validation["valid"] = False
            validation["error"] = f"Content item {i} missing 'type' attribute"
            return validation

        # Check text content
        if item.type == 'text':
            if not hasattr(item, 'text'):
                validation["valid"] = False
                validation["error"] = f"Text content item {i} missing 'text' attribute"
                return validation
            validation["has_text"] = True
            texts.append(item.text)

    if texts:
        validation["text_content"] = "\n".join(texts)

    return validation


def assert_valid_mcp_response(result) -> None:
    """Assert that a ToolResult is valid MCP response.

    Convenience function that raises AssertionError if invalid.

    Args:
        result: ToolResult from FastMCP

    Raises:
        AssertionError: If response is not valid

    Example:
        result = await invoke_tool("mealie_recipes_search", query="pasta")
        assert_valid_mcp_response(result)
    """
    validation = validate_mcp_response(result)
    if not validation["valid"]:
        raise AssertionError(f"Invalid MCP response: {validation['error']}")


def extract_text_from_result(result) -> str:
    """Extract text content from a ToolResult.

    Helper to get the actual text response from an MCP ToolResult,
    handling the nested structure of content objects.

    Args:
        result: ToolResult from FastMCP

    Returns:
        str: Concatenated text from all text content items

    Example:
        result = await invoke_mcp_tool("ping")
        text = extract_text_from_result(result)
        assert "pong" in text
    """
    if not hasattr(result, 'content'):
        return ""

    texts = []
    for item in result.content:
        if hasattr(item, 'type') and item.type == 'text':
            if hasattr(item, 'text'):
                texts.append(item.text)

    return "\n".join(texts)


def extract_json_from_result(result) -> dict:
    """Extract JSON data from a ToolResult.

    Parses the text content as JSON and returns the parsed object.

    Args:
        result: ToolResult from FastMCP

    Returns:
        dict: Parsed JSON data

    Raises:
        json.JSONDecodeError: If text is not valid JSON
        ValueError: If result has no text content

    Example:
        result = await invoke_tool("mealie_recipes_list")
        data = extract_json_from_result(result)
        assert "items" in data
    """
    text = extract_text_from_result(result)
    if not text:
        raise ValueError("Result has no text content")

    return json.loads(text)


def validate_json_response_schema(result, schema: dict) -> tuple[bool, Optional[str]]:
    """Validate that a ToolResult's JSON matches a JSON schema.

    Args:
        result: ToolResult from FastMCP
        schema: JSON schema to validate against

    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])

    Example:
        result = await invoke_tool("mealie_recipes_list")
        valid, error = validate_json_response_schema(result, {
            "type": "object",
            "properties": {
                "items": {"type": "array"},
                "total": {"type": "integer"}
            },
            "required": ["items"]
        })
        assert valid, error
    """
    try:
        data = extract_json_from_result(result)
    except (json.JSONDecodeError, ValueError) as e:
        return False, f"Failed to parse JSON: {e}"

    try:
        json_validate(instance=data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, f"Schema validation failed: {e.message}"


def assert_json_response_schema(result, schema: dict) -> None:
    """Assert that a ToolResult's JSON matches a schema.

    Convenience function that raises AssertionError if validation fails.

    Args:
        result: ToolResult from FastMCP
        schema: JSON schema to validate against

    Raises:
        AssertionError: If JSON doesn't match schema

    Example:
        result = await invoke_tool("mealie_recipes_list")
        assert_json_response_schema(result, {
            "type": "object",
            "properties": {
                "items": {"type": "array"}
            }
        })
    """
    valid, error = validate_json_response_schema(result, schema)
    if not valid:
        raise AssertionError(f"JSON response schema validation failed: {error}")


# ============================================================================
# Error Response Validation
# ============================================================================

def validate_error_response(result, expected_error_substring: str = None) -> tuple[bool, Optional[str]]:
    """Validate that a ToolResult contains an error response.

    Args:
        result: ToolResult from FastMCP
        expected_error_substring: Optional substring to check in error message

    Returns:
        tuple: (is_error: bool, error_message: str)

    Example:
        result = await invoke_tool("mealie_recipes_get", slug="nonexistent")
        is_error, msg = validate_error_response(result, "not found")
        assert is_error
    """
    try:
        data = extract_json_from_result(result)
    except Exception as e:
        # Not JSON, check if text contains error
        text = extract_text_from_result(result)
        is_error = "error" in text.lower()
        if expected_error_substring:
            is_error = is_error and expected_error_substring.lower() in text.lower()
        return is_error, text

    # Check if JSON contains error field
    if "error" in data:
        error_msg = str(data["error"])
        if expected_error_substring:
            contains_substring = expected_error_substring.lower() in error_msg.lower()
            return contains_substring, error_msg
        return True, error_msg

    return False, None


def assert_tool_error(result, expected_error_substring: str = None) -> None:
    """Assert that a ToolResult contains an error.

    Args:
        result: ToolResult from FastMCP
        expected_error_substring: Optional substring to check in error

    Raises:
        AssertionError: If result is not an error or doesn't contain substring

    Example:
        result = await invoke_tool("mealie_recipes_get", slug="invalid")
        assert_tool_error(result, "not found")
    """
    is_error, msg = validate_error_response(result, expected_error_substring)
    if not is_error:
        raise AssertionError(
            f"Expected error response"
            f"{' containing: ' + expected_error_substring if expected_error_substring else ''}"
            f", but got: {msg}"
        )


# ============================================================================
# Data Validation Helpers
# ============================================================================

def assert_has_fields(data: dict, required_fields: list[str]) -> None:
    """Assert that a dictionary contains required fields.

    Args:
        data: Dictionary to check
        required_fields: List of required field names

    Raises:
        AssertionError: If any required field is missing

    Example:
        recipe_data = extract_json_from_result(result)
        assert_has_fields(recipe_data, ["id", "name", "slug"])
    """
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise AssertionError(
            f"Missing required fields: {missing}. "
            f"Available fields: {list(data.keys())}"
        )


def assert_field_type(data: dict, field: str, expected_type: type) -> None:
    """Assert that a field has the expected type.

    Args:
        data: Dictionary containing the field
        field: Field name to check
        expected_type: Expected Python type

    Raises:
        AssertionError: If field missing or wrong type

    Example:
        recipe_data = extract_json_from_result(result)
        assert_field_type(recipe_data, "total", int)
    """
    if field not in data:
        raise AssertionError(f"Field '{field}' not found in data")

    actual_value = data[field]
    if not isinstance(actual_value, expected_type):
        raise AssertionError(
            f"Field '{field}' has wrong type: "
            f"expected {expected_type.__name__}, got {type(actual_value).__name__}"
        )


def assert_list_length(data: dict, field: str, expected_length: int = None, min_length: int = None) -> None:
    """Assert that a list field has expected length.

    Args:
        data: Dictionary containing the field
        field: Field name (should be a list)
        expected_length: Exact expected length (optional)
        min_length: Minimum expected length (optional)

    Raises:
        AssertionError: If list doesn't meet length requirements

    Example:
        response = extract_json_from_result(result)
        assert_list_length(response, "items", min_length=1)
    """
    if field not in data:
        raise AssertionError(f"Field '{field}' not found in data")

    value = data[field]
    if not isinstance(value, list):
        raise AssertionError(f"Field '{field}' is not a list: {type(value).__name__}")

    actual_length = len(value)

    if expected_length is not None and actual_length != expected_length:
        raise AssertionError(
            f"List '{field}' has wrong length: "
            f"expected {expected_length}, got {actual_length}"
        )

    if min_length is not None and actual_length < min_length:
        raise AssertionError(
            f"List '{field}' too short: "
            f"expected at least {min_length}, got {actual_length}"
        )
