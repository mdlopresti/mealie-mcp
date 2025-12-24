"""
Helper utilities for MCP server testing.

Provides validation functions for MCP protocol compliance and tool testing.
"""

from typing import Any


def validate_tool_registration(server, tool_name: str) -> bool:
    """Check if a tool is registered with the MCP server.

    Args:
        server: FastMCP server instance
        tool_name: Name of the tool to check

    Returns:
        bool: True if tool is registered, False otherwise

    Example:
        assert validate_tool_registration(mcp_server, "mealie_recipes_search")
    """
    import asyncio

    async def _check():
        tools = await server.get_tools()
        return tool_name in tools

    return asyncio.run(_check())


def validate_tool_params(tool, expected_params: dict[str, bool]) -> bool:
    """Validate that a tool has the expected parameters.

    Args:
        tool: FastMCP FunctionTool instance
        expected_params: Dict mapping parameter names to required status
            Example: {"query": False, "limit": False} means both are optional

    Returns:
        bool: True if parameters match expectations

    Example:
        tool = await mcp.get_tools()["mealie_recipes_search"]
        assert validate_tool_params(tool, {
            "query": False,
            "tags": False,
            "categories": False,
            "limit": False
        })
    """
    if not hasattr(tool, 'parameters'):
        return False

    # Get tool parameter schema
    params = tool.parameters
    if not params or 'properties' not in params:
        return len(expected_params) == 0

    # Check each expected parameter
    for param_name, is_required in expected_params.items():
        if param_name not in params['properties']:
            return False

        # Check if required matches expectation
        required_params = params.get('required', [])
        actual_required = param_name in required_params
        if actual_required != is_required:
            return False

    return True


def validate_resource_uri(resource_uri: str) -> bool:
    """Validate MCP resource URI format.

    MCP resource URIs should follow the pattern:
    - "resource://type" for static resources
    - "resource://{param}" for templated resources

    Args:
        resource_uri: The resource URI to validate

    Returns:
        bool: True if URI is valid format

    Example:
        assert validate_resource_uri("recipes://list")
        assert validate_resource_uri("recipes://{slug}")
    """
    if not resource_uri:
        return False

    # Should contain ://
    if "://" not in resource_uri:
        return False

    parts = resource_uri.split("://")
    if len(parts) != 2:
        return False

    scheme, path = parts

    # Scheme should be alphanumeric
    if not scheme.replace("-", "").replace("_", "").isalnum():
        return False

    # Path should not be empty
    if not path:
        return False

    return True


def validate_mcp_response(result) -> dict[str, Any]:
    """Validate MCP protocol compliance of a ToolResult.

    Checks that the ToolResult follows MCP protocol requirements:
    - Has content attribute
    - Content is a list
    - Each content item has type and text

    Args:
        result: ToolResult from FastMCP

    Returns:
        dict with validation results:
            - valid: bool
            - error: str (if invalid)
            - content_count: int
            - has_text: bool

    Example:
        result = await invoke_mcp_tool("ping")
        validation = validate_mcp_response(result)
        assert validation["valid"]
    """
    validation = {
        "valid": True,
        "error": None,
        "content_count": 0,
        "has_text": False
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
        validation["error"] = f"Content should be list, got {type(content)}"
        return validation

    validation["content_count"] = len(content)

    # Check each content item
    for i, item in enumerate(content):
        # Should have type
        if not hasattr(item, 'type'):
            validation["valid"] = False
            validation["error"] = f"Content item {i} missing 'type'"
            return validation

        # Should have text for text content
        if item.type == 'text':
            if not hasattr(item, 'text'):
                validation["valid"] = False
                validation["error"] = f"Text content item {i} missing 'text'"
                return validation
            validation["has_text"] = True

    return validation


def extract_tool_result_text(result) -> str:
    """Extract text content from a ToolResult.

    Helper to get the actual text response from an MCP ToolResult,
    handling the nested structure of content objects.

    Args:
        result: ToolResult from FastMCP

    Returns:
        str: Concatenated text from all text content items

    Example:
        result = await invoke_mcp_tool("ping")
        text = extract_tool_result_text(result)
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
