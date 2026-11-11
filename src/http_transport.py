"""
HTTP transport for the Mealie MCP server.

Runs the FastMCP server over streamable HTTP (instead of stdio) so it can be
hosted as a long-running container, e.g. a Home Assistant app (add-on).

Environment variables:
    MCP_HOST        Bind address (default: 0.0.0.0)
    MCP_PORT        Listen port (default: 8099)
    MCP_PATH        Endpoint path (default: /mcp)
    MCP_AUTH_TOKEN  Optional bearer token. When set, every request must send
                    "Authorization: Bearer <token>".
    MCP_LOG_LEVEL   Uvicorn log level (default: info)
"""

import hmac
import os

import uvicorn
from starlette.middleware import Middleware


class BearerAuthMiddleware:
    """Minimal pure-ASGI bearer token check (safe for streaming responses)."""

    def __init__(self, app, token: str):
        self.app = app
        self.expected = f"Bearer {token}".encode()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        provided = headers.get(b"authorization", b"")
        if not hmac.compare_digest(provided, self.expected):
            await send({
                "type": "http.response.start",
                "status": 401,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"www-authenticate", b"Bearer"),
                ],
            })
            await send({
                "type": "http.response.body",
                "body": b'{"error":"unauthorized"}',
            })
            return

        await self.app(scope, receive, send)


def run_http(mcp) -> None:
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8099"))
    path = os.getenv("MCP_PATH", "/mcp")
    token = os.getenv("MCP_AUTH_TOKEN", "").strip()
    log_level = os.getenv("MCP_LOG_LEVEL", "info").lower()

    middleware = [Middleware(BearerAuthMiddleware, token=token)] if token else []
    app = mcp.http_app(path=path, middleware=middleware)

    print(
        f"Mealie MCP server listening on http://{host}:{port}{path} "
        f"(auth: {'bearer token' if token else 'NONE'})",
        flush=True,
    )
    uvicorn.run(app, host=host, port=port, log_level=log_level)
