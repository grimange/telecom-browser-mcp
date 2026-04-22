# Codex CLI Config Examples

These examples are for `~/.codex/config.toml`.

They are intentionally conservative:

- `stdio` is the recommended first path
- local HTTP/SSE stay on `127.0.0.1`
- non-local HTTP/SSE are marked advanced and require explicit auth and unsafe-bind opt-in
- `supports_parallel_tool_calls` is set to `false` on purpose

## 1. Minimal Stdio Example

Use this first. Recommended.

```toml
[mcp_servers.telecom_browser_mcp]
command = "/absolute/path/to/repo/.venv/bin/telecom-browser-mcp-stdio"
default_tools_approval_mode = "prompt"
supports_parallel_tool_calls = false
```

What it is for:

- safest local Codex setup
- no listening socket
- easiest first registration path

First-use prompt:

```text
Use the telecom_browser_mcp server and call health, capabilities, and list_sessions.
```

## 2. Local HTTP Example

Recommended only when you need local HTTP transport behavior.

Start the server first:

```bash
cd /absolute/path/to/repo
FASTMCP_HOST=127.0.0.1 FASTMCP_PORT=8000 .venv/bin/telecom-browser-mcp-http
```

Codex config:

```toml
[mcp_servers.telecom_browser_mcp_http]
url = "http://127.0.0.1:8000/mcp"
default_tools_approval_mode = "prompt"
supports_parallel_tool_calls = false
```

Security note:

- localhost developer use does not require a bearer token
- this is not the recommended beginner path

Verification:

```bash
bash scripts/run_live_transport_smoke.sh http
```

## 3. Local SSE Example

Recommended only when you need local SSE transport behavior.

Start the server first:

```bash
cd /absolute/path/to/repo
FASTMCP_HOST=127.0.0.1 FASTMCP_PORT=8001 .venv/bin/telecom-browser-mcp-sse
```

Codex config:

```toml
[mcp_servers.telecom_browser_mcp_sse]
url = "http://127.0.0.1:8001/sse"
default_tools_approval_mode = "prompt"
supports_parallel_tool_calls = false
```

Security note:

- localhost developer use does not require a bearer token
- keep this local-only unless you are intentionally operating the advanced protected path

Verification:

```bash
bash scripts/run_live_transport_smoke.sh sse
```

## 4. Advanced Non-Local Protected HTTP Example

Advanced operator-managed deployment. Not recommended as a first setup.

Server startup:

```bash
cd /absolute/path/to/repo
FASTMCP_HOST=0.0.0.0 \
FASTMCP_PORT=8123 \
TELECOM_BROWSER_MCP_UNSAFE_BIND=1 \
TELECOM_BROWSER_MCP_AUTH_TOKEN="replace-with-a-strong-token" \
.venv/bin/telecom-browser-mcp-http
```

Before starting Codex:

```bash
export TELECOM_BROWSER_MCP_AUTH_TOKEN="replace-with-the-same-strong-token"
```

Codex config:

```toml
[mcp_servers.telecom_browser_mcp_http_remote]
url = "http://your-hostname-or-ip:8123/mcp"
bearer_token_env_var = "TELECOM_BROWSER_MCP_AUTH_TOKEN"
default_tools_approval_mode = "prompt"
supports_parallel_tool_calls = false
```

Security notes:

- non-local bind should fail closed without both `TELECOM_BROWSER_MCP_UNSAFE_BIND=1` and `TELECOM_BROWSER_MCP_AUTH_TOKEN`
- keep reverse proxy, firewall, token rotation, and outbound egress controls in place

Verification:

```bash
bash scripts/run_live_transport_smoke.sh http
```

## 5. Advanced Non-Local Protected SSE Example

Advanced operator-managed deployment. Not recommended as a first setup.

Server startup:

```bash
cd /absolute/path/to/repo
FASTMCP_HOST=0.0.0.0 \
FASTMCP_PORT=8124 \
TELECOM_BROWSER_MCP_UNSAFE_BIND=1 \
TELECOM_BROWSER_MCP_AUTH_TOKEN="replace-with-a-strong-token" \
.venv/bin/telecom-browser-mcp-sse
```

Before starting Codex:

```bash
export TELECOM_BROWSER_MCP_AUTH_TOKEN="replace-with-the-same-strong-token"
```

Codex config:

```toml
[mcp_servers.telecom_browser_mcp_sse_remote]
url = "http://your-hostname-or-ip:8124/sse"
bearer_token_env_var = "TELECOM_BROWSER_MCP_AUTH_TOKEN"
default_tools_approval_mode = "prompt"
supports_parallel_tool_calls = false
```

Security notes:

- bearer token and explicit unsafe-bind opt-in are required
- keep this behind operator-managed network controls

Verification:

```bash
bash scripts/run_live_transport_smoke.sh sse
```
