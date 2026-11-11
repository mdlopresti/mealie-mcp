# Mealie MCP Server

This app lets AI assistants (Claude, Home Assistant Assist, Claude Code and
other MCP clients) work with your [Mealie](https://mealie.io) instance: search
and edit recipes, plan meals, manage shopping lists and more.

It runs the Mealie MCP server as a long-running service and serves the
[Model Context Protocol](https://modelcontextprotocol.io) over **streamable
HTTP** at:

```
http://<home-assistant-ip>:8099/mcp
```

- [1. Install](#1-install)
- [2. Create a Mealie API token](#2-create-a-mealie-api-token)
- [3. Configure the app](#3-configure-the-app)
- [4. Start and verify](#4-start-and-verify)
- [5. Connect an AI client](#5-connect-an-ai-client)
- [6. Updating](#6-updating)
- [7. Troubleshooting](#7-troubleshooting)

---

## 1. Install

1. In Home Assistant go to **Settings → Apps → App store**.
2. Open the **⋮** menu (top right) → **Repositories**, add
   `https://github.com/warinthestars/mealie-mcp`, and close the dialog.
3. Refresh the store, find **Mealie MCP Server** and click **Install**.

> This is a Home Assistant **app** (formerly "add-on"). It isn't installed
> through HACS. HACS only handles integrations and dashboard cards.

## 2. Create a Mealie API token

1. Open Mealie and sign in as the user the assistant should act as.
   Recipes and meal plans are created as that user.
2. Click your avatar → **API Tokens** (`/user/profile/api-tokens`).
3. Give the token a name (e.g. `MCP`), click **Generate**, and copy it right away.
   Mealie only shows it once.

## 3. Configure the app

Open the app's **Configuration** tab.

| Option | Required | What to enter |
| --- | --- | --- |
| `mealie_url` | yes | Where **this app** can reach Mealie. See [Choosing the Mealie URL](#choosing-the-mealie-url). No trailing slash. |
| `mealie_api_token` | yes | The token from step 2. |
| `mcp_auth_token` | strongly recommended | A password that AI clients must send as `Authorization: Bearer <token>`. See [Choosing an MCP token](#choosing-an-mcp-token). |
| `log_level` | no | `info` by default; `debug` for troubleshooting. |

The MCP server listens on container port 8099. To use a different host port,
change it under **Network** on the same tab. Every client URL below then uses
your new port.

### Choosing the Mealie URL

The app runs in its own container, so `localhost` means the app itself, not
Mealie. `mealie.local` usually won't resolve inside a container either.

#### A) Mealie runs as an app on the same Home Assistant (recommended)

Use the Mealie app's **internal hostname** and **container port**. Traffic stays
on Home Assistant's internal network, with no ports or TLS to deal with.

1. Go to **Settings → Apps → Mealie**. The browser URL ends with the app slug,
   e.g. `.../app/db21ed7f_mealie`.
2. The hostname is that slug with `_` replaced by `-`: `db21ed7f-mealie`.
3. On the Mealie app's **Configuration → Network** section, the port in the
   **left** column is the container port. Use that one, not the host port on
   the right.

For the popular Mealie app from **alexbelgium/hassio-addons** this is:

```
http://db21ed7f-mealie:9001
```

(`9001` is its container port. `9090` is only the port published on your LAN.)

Alternatives that also work:
- `http://<home-assistant-lan-ip>:9090` uses the host port published on your network.
- Your public Mealie URL (e.g. `https://mealie.example.com`) works, but routes
  every call out through the internet and back.

**Don't** use the Ingress/sidebar URL (`/api/hassio_ingress/...`). It needs a
Home Assistant login session and won't accept API tokens.

#### B) Mealie runs elsewhere on your network (Docker, NAS, another server)

Use its LAN address and published port, e.g. `http://192.168.1.50:9925`.
Mealie's own Docker image listens on port `9000` inside its container. Use
whatever host port you mapped it to.

#### C) Mealie is only reachable through a public URL

Use the full HTTPS URL, e.g. `https://mealie.example.com`.

### Choosing an MCP token

Anyone who can reach port 8099 and knows this token can read and change your
Mealie data, so treat it like a password.

- Use **letters and digits only** (32+ characters). Symbols such as `& ^ % !`
  get mangled by Windows command lines and some config files. That is a common
  cause of "401 Unauthorized" even though the token looks right.
- Generate one with `openssl rand -hex 32`, or in Python with
  `python -c "import secrets; print(secrets.token_hex(32))"`.
- Leaving it empty turns authentication off. Only do that if port 8099 is
  unreachable from outside your home network and you trust every device on it.

## 4. Start and verify

1. Click **Save**, then **Start**. Turn on **Start on boot** and **Watchdog**.
2. Open the **Log** tab. A healthy start looks like:

   ```
   Mealie MCP Server app v1.9.0
   Mealie MCP server listening on http://0.0.0.0:8099/mcp (auth: bearer token)
   INFO:     Uvicorn running on http://0.0.0.0:8099
   ```

3. Optional check from any computer on your network. `401` means the server
   is up and enforcing the token:

   ```bash
   curl -i -X POST http://<home-assistant-ip>:8099/mcp
   ```

The log doesn't prove Mealie is reachable. The first real tool call does.
If tool calls fail with connection errors, see [Troubleshooting](#7-troubleshooting).

## 5. Connect an AI client

Pick the option that matches where the client runs:

| Client | Where it connects from | Needs public HTTPS? |
| --- | --- | --- |
| Claude Desktop, local config (5.1) | your computer | no (LAN) |
| Claude custom connector, web/desktop/mobile (5.2) | Anthropic's cloud | **yes** |
| Claude Code (5.3) | your computer | no (LAN) |
| Home Assistant Assist (5.4) | Home Assistant itself | no |

### 5.1 Claude Desktop, local configuration (LAN only, nothing exposed)

Claude Desktop runs a small bridge, [`mcp-remote`](https://www.npmjs.com/package/mcp-remote),
on your computer. The bridge connects to the app over your network. This
needs [Node.js](https://nodejs.org) (LTS) installed on the computer.

1. Claude Desktop → **Settings → Developer → Edit Config**. This opens
   `claude_desktop_config.json`.
2. Add a `mealie` entry under `mcpServers`, keeping any existing servers:

   ```json
   {
     "mcpServers": {
       "mealie": {
         "command": "npx",
         "args": [
           "-y", "mcp-remote",
           "http://192.168.1.10:8099/mcp",
           "--allow-http",
           "--header", "Authorization:${MEALIE_MCP_AUTH}"
         ],
         "env": { "MEALIE_MCP_AUTH": "Bearer YOUR_MCP_AUTH_TOKEN" }
       }
     }
   }
   ```

   - Replace `192.168.1.10` with your Home Assistant IP. An IP is more reliable
     than `homeassistant.local` on Windows.
   - `--allow-http` is required because the URL is plain HTTP.
   - Keep the header in the `env` block exactly as shown. Writing
     `"Authorization: Bearer ..."` directly in `args` breaks on Windows,
     because the space splits the argument.
3. Fully quit Claude Desktop (from the tray/menu bar, not just the window) and
   reopen it. **mealie** should appear under the tools (🔨) menu.

### 5.2 Claude custom connector (claude.ai, Claude Desktop "Connectors", mobile)

Custom connectors are called **from Anthropic's servers, not from your
computer**. A LAN address like `http://192.168.1.10:8099` or
`homeassistant.local` can never work here. The server must be reachable on a
public **HTTPS** URL.

If you already use the **Cloudflared** app to reach Home Assistant remotely,
publish the MCP server through the same tunnel:

1. **Settings → Apps → Cloudflared → Configuration → Additional hosts**, add:

   ```yaml
   - hostname: mealie-mcp.example.com
     service: http://<mealie-mcp-hostname>:8099
   ```

   `<mealie-mcp-hostname>` is this app's slug with `_` replaced by `-`
   (e.g. `98d3c1cb-mealie-mcp`; find the slug in this page's browser URL).
   Save and restart Cloudflared. It creates the DNS record for you.
2. Check `https://mealie-mcp.example.com/mcp` from a phone on mobile data.
   A `401` response means it works.
3. In Claude: **Settings → Connectors → Add custom connector**:
   - **URL:** `https://mealie-mcp.example.com/mcp`
   - **Authentication:** *No sign in*
   - **Request headers:** `Authorization` = `Bearer YOUR_MCP_AUTH_TOKEN`
4. Enable the connector in a chat from the **+** / tools menu.

> A public URL exposes your Mealie data to anyone holding the token. Always set
> a long `mcp_auth_token` before publishing. Optionally, protect the hostname
> further with Cloudflare Access rules.

### 5.3 Claude Code

```bash
claude mcp add --transport http mealie http://192.168.1.10:8099/mcp \
  --header "Authorization: Bearer YOUR_MCP_AUTH_TOKEN"
```

### 5.4 Home Assistant Assist (Model Context Protocol integration)

1. **Settings → Devices & services → Add integration → Model Context Protocol**.
2. URL: `http://localhost:8099/mcp`. Home Assistant reaches the app's
   published port on its own host.
3. Enable the integration's tools for your conversation agent under
   **Settings → Voice assistants**.

If the integration can't authenticate with a static bearer token, it gets 401
errors. In that case you'd have to leave `mcp_auth_token` empty, which is only
safe if port 8099 isn't reachable from outside your network.

## 6. Updating

Home Assistant offers updates when a new version is released. The update
dialog shows the changelog. Check the **Log** tab after updating.

## 7. Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| Log: `ERROR: missing configuration` | Fill in `mealie_url` and `mealie_api_token`, save, restart. |
| Tool calls fail with *connection refused*, *name resolution* or timeouts | `mealie_url` isn't reachable from the container. Don't use `localhost`, `mealie.local` or an Ingress URL. Use the internal hostname + container port (section 3A), e.g. `http://db21ed7f-mealie:9001`. |
| Tool calls fail with **401** from Mealie | `mealie_api_token` is wrong or was deleted in Mealie. Generate a new one. |
| Client gets **401 Unauthorized** from this app | The client isn't sending `Authorization: Bearer <mcp_auth_token>`, or the token was mangled. Use letters/digits only; on Windows use the `env` form in 5.1. |
| Log shows `GET /.well-known/oauth-protected-resource ... 404` | Normal. Clients check for OAuth first, then use the bearer header. |
| Claude custom connector: "couldn't connect" / asks to sign in | The URL must be public HTTPS (5.2), Authentication must be *No sign in*, and the header must be set. A LAN URL can't work. |
| Claude Desktop shows no mealie tools (5.1) | Node.js must be installed; fully quit and reopen Claude Desktop; check `%APPDATA%\Claude\logs\mcp-server-mealie.log` (Windows) or `~/Library/Logs/Claude/mcp-server-mealie.log` (macOS). |
| Port 8099 already in use | Change the host port under **Configuration → Network**, and update client URLs. |

Set `log_level: debug` and restart for more detail. Report issues at
<https://github.com/warinthestars/mealie-mcp/issues>.
