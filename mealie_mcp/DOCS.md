# Mealie MCP Server

This app runs the Mealie MCP server as a long-running service and exposes it
over MCP's streamable HTTP transport at:

    http://<home-assistant-host>:8099/mcp

## Configuration

| Option | Required | Description |
| --- | --- | --- |
| `mealie_url` | yes | Base URL of Mealie, e.g. `http://192.168.1.50:9925`. If Mealie runs as another app on this Home Assistant, you can use its internal hostname. |
| `mealie_api_token` | yes | Mealie → User Profile → API Tokens. |
| `mcp_auth_token` | recommended | Any long random string. Clients must then send `Authorization: Bearer <token>`. Leave empty only on a trusted network. |
| `log_level` | no | `debug`, `info`, `warning` or `error`. |

Change the host port on the **Network** section of the Configuration tab if 8099 is taken.

## Connecting clients

**Home Assistant (Model Context Protocol integration):** Settings → Devices & services → Add integration → *Model Context Protocol*, and enter `http://localhost:8099/mcp`.

**Claude Code / other MCP clients:**

```json
{
  "mcpServers": {
    "mealie": {
      "type": "http",
      "url": "http://homeassistant.local:8099/mcp",
      "headers": { "Authorization": "Bearer YOUR_MCP_AUTH_TOKEN" }
    }
  }
}
```

**Claude Desktop** (stdio only) can bridge with `npx mcp-remote http://homeassistant.local:8099/mcp --header "Authorization: Bearer YOUR_MCP_AUTH_TOKEN"`.

## Troubleshooting

- *Missing configuration* in the log: fill in `mealie_url` and `mealie_api_token`, then restart.
- `401 unauthorized`: the client's bearer token doesn't match `mcp_auth_token`.
- Tool calls fail with connection errors: check that the Home Assistant host can reach `mealie_url`.
