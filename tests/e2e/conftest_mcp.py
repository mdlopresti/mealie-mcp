"""
Pytest fixtures for MCP server lifecycle management in E2E tests.

Provides fixtures for starting/stopping the MCP server connected to test Mealie instances.
This enables testing the full MCP protocol integration end-to-end.
"""

import os
import sys
import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Generator, Dict, Any, Optional
import pytest

logger = logging.getLogger(__name__)

# Path to MCP server source
MCP_SERVER_PATH = Path(__file__).parent.parent.parent / "src" / "server.py"


@pytest.fixture(scope="session")
def mcp_server_process(
    mealie_container: Dict[str, Any],
    mealie_api_token: str
) -> Generator[subprocess.Popen, None, None]:
    """
    Start the MCP server as a subprocess connected to test Mealie instance.

    The MCP server communicates via stdin/stdout, so we start it as a subprocess
    and provide a way to send/receive MCP protocol messages.

    Args:
        mealie_container: Container info from Docker fixture
        mealie_api_token: API token for Mealie authentication

    Yields:
        subprocess.Popen object for the running MCP server
    """
    logger.info("Starting MCP server subprocess...")

    # Prepare environment variables
    env = os.environ.copy()
    env["MEALIE_BASE_URL"] = mealie_container["base_url"]
    env["MEALIE_API_TOKEN"] = mealie_api_token

    # Start MCP server as subprocess
    process = subprocess.Popen(
        [sys.executable, "-m", "src.server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=Path(__file__).parent.parent.parent,  # Project root
        text=True,
        bufsize=1  # Line buffered
    )

    # Give server time to initialize
    time.sleep(2)

    # Check if process started successfully
    if process.poll() is not None:
        stderr = process.stderr.read() if process.stderr else ""
        raise RuntimeError(f"MCP server failed to start. stderr: {stderr}")

    logger.info(f"MCP server started with PID: {process.pid}")

    yield process

    # Teardown - terminate MCP server
    logger.info(f"Terminating MCP server (PID: {process.pid})")

    try:
        process.terminate()
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        logger.warning("MCP server did not terminate gracefully, killing...")
        process.kill()
        process.wait()

    logger.info("MCP server stopped")


@pytest.fixture
def mcp_client(mcp_server_process: subprocess.Popen) -> Dict[str, Any]:
    """
    Provide an MCP client interface for sending/receiving protocol messages.

    This fixture provides helper methods for interacting with the MCP server
    via JSON-RPC over stdin/stdout. It performs the MCP initialization handshake
    automatically.

    Args:
        mcp_server_process: Running MCP server process

    Returns:
        Dict with methods:
        - send(method, params): Send MCP request
        - receive(): Read MCP response
        - call(method, params): Send request and wait for response
        - server_info: Server capabilities and info from initialization
    """

    def send_message(method: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        Send JSON-RPC message to MCP server.

        Args:
            method: MCP method name (e.g., "tools/list", "tools/call")
            params: Method parameters

        Returns:
            Request ID for correlation
        """
        import random

        request_id = random.randint(1, 100000)

        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }

        logger.debug(f"Sending MCP message: {method}")
        mcp_server_process.stdin.write(json.dumps(message) + "\n")
        mcp_server_process.stdin.flush()

        return request_id

    def send_notification(method: str, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Send JSON-RPC notification to MCP server (no response expected).

        Args:
            method: MCP method name
            params: Method parameters
        """
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }

        logger.debug(f"Sending MCP notification: {method}")
        mcp_server_process.stdin.write(json.dumps(message) + "\n")
        mcp_server_process.stdin.flush()

    def receive_message() -> Dict[str, Any]:
        """
        Receive JSON-RPC response from MCP server.

        Returns:
            Response message dict
        """
        line = mcp_server_process.stdout.readline()

        if not line:
            raise RuntimeError("MCP server closed stdout")

        logger.debug(f"Received MCP message: {line[:100]}...")
        return json.loads(line)

    def call_method(method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Send MCP request and wait for response.

        Args:
            method: MCP method name
            params: Method parameters

        Returns:
            Result from MCP response

        Raises:
            RuntimeError: If response contains error
        """
        request_id = send_message(method, params)

        # Read response (may need to handle multiple responses for async)
        max_attempts = 10
        for _ in range(max_attempts):
            response = receive_message()

            # Check if this is the response we're waiting for
            if response.get("id") == request_id:
                if "error" in response:
                    raise RuntimeError(f"MCP error: {response['error']}")

                return response.get("result")

        raise RuntimeError(f"No response received for request {request_id}")

    # Perform MCP initialization handshake
    logger.info("Performing MCP initialization handshake...")

    # Step 1: Send initialize request
    init_result = call_method("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "roots": {"listChanged": True},
            "sampling": {}
        },
        "clientInfo": {
            "name": "mealie-mcp-test-client",
            "version": "1.0.0"
        }
    })

    logger.info(f"Server capabilities: {init_result.get('capabilities', {})}")
    logger.info(f"Server info: {init_result.get('serverInfo', {})}")

    # Step 2: Send initialized notification
    send_notification("notifications/initialized")

    # Wait a moment for any server responses
    time.sleep(0.5)

    logger.info("MCP initialization handshake complete")

    return {
        "send": send_message,
        "send_notification": send_notification,
        "receive": receive_message,
        "call": call_method,
        "process": mcp_server_process,
        "server_info": init_result
    }


@pytest.fixture
def mcp_tool_caller(mcp_client: Dict[str, Any]) -> callable:
    """
    Provide a simplified interface for calling MCP tools.

    Args:
        mcp_client: MCP client interface

    Returns:
        Function: call_tool(tool_name, **kwargs) -> result
    """

    def call_tool(tool_name: str, **kwargs) -> Any:
        """
        Call an MCP tool and return the result.

        Args:
            tool_name: Name of the tool (e.g., "mealie_recipes_get")
            **kwargs: Tool parameters

        Returns:
            Tool result

        Example:
            >>> recipe = call_tool("mealie_recipes_get", slug="test-recipe")
            >>> assert recipe["name"] == "Test Recipe"
        """
        params = {
            "name": tool_name,
            "arguments": kwargs
        }

        return mcp_client["call"]("tools/call", params)

    return call_tool


@pytest.fixture(scope="session")
def mcp_tools_list(mcp_client: Dict[str, Any]) -> list[Dict[str, Any]]:
    """
    Get list of all available MCP tools.

    Useful for validating that all expected tools are registered.

    Args:
        mcp_client: MCP client interface

    Returns:
        List of tool definitions with name, description, and inputSchema
    """
    logger.info("Fetching MCP tools list...")

    # Call tools/list method
    result = mcp_client["call"]("tools/list", {})

    tools = result.get("tools", [])
    logger.info(f"Found {len(tools)} MCP tools")

    return tools


@pytest.fixture
def mcp_resource_reader(mcp_client: Dict[str, Any]) -> callable:
    """
    Provide a simplified interface for reading MCP resources.

    Args:
        mcp_client: MCP client interface

    Returns:
        Function: read_resource(uri) -> content
    """

    def read_resource(uri: str) -> Any:
        """
        Read an MCP resource.

        Args:
            uri: Resource URI (e.g., "recipes://list")

        Returns:
            Resource content

        Example:
            >>> recipes = read_resource("recipes://list")
            >>> assert "recipes" in recipes
        """
        params = {
            "uri": uri
        }

        return mcp_client["call"]("resources/read", params)

    return read_resource


@pytest.fixture(scope="session")
def mcp_resources_list(mcp_client: Dict[str, Any]) -> list[Dict[str, Any]]:
    """
    Get list of all available MCP resources.

    Useful for validating that all expected resources are registered.

    Args:
        mcp_client: MCP client interface

    Returns:
        List of resource definitions with uri, name, description, and mimeType
    """
    logger.info("Fetching MCP resources list...")

    # Call resources/list method
    result = mcp_client["call"]("resources/list", {})

    resources = result.get("resources", [])
    logger.info(f"Found {len(resources)} MCP resources")

    return resources
