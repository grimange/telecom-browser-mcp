# Codex CLI Setup

This is the canonical setup guide for using `telecom-browser-mcp` from Codex CLI.

Recommended quickstart:

1. Install the repo into a local virtualenv.
2. Register the server in `~/.codex/config.toml` using `stdio`.
3. Restart Codex CLI and verify the first-contact tools: `health`, `capabilities`, `list_sessions`.
4. Use local HTTP or SSE only when you specifically need transport-level testing.

Stdio is the safest default because it does not expose a listening socket. Local HTTP and local SSE are supported for development and verification. Non-local HTTP/SSE is an advanced operator-managed deployment path and is not the beginner setup.

## Prerequisites

- Codex CLI installed on the host you actually run.
- Codex CLI config file at `~/.codex/config.toml`.
- Python 3.11 or newer.
- A local clone of this repository.
- A project virtualenv with the repo installed:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

- Playwright browser binaries installed for browser-driving tools:

```bash
.venv/bin/python -m playwright install chromium
```

This guide assumes a POSIX-style shell and path layout. The repo does not currently provide a separate native-Windows setup guide; if you are on Windows, use an environment that can run the same Python entrypoints and shell commands consistently.

## Where Codex CLI Reads MCP Config

Codex CLI reads MCP server definitions from `~/.codex/config.toml`.

You can either edit that file directly or use `codex mcp add` to write the entry for you. This guide shows the file contents explicitly because they are easier to review and keep under your own control.

For this server, keep the Codex-side defaults conservative:

- use `stdio` first
- prefer prompting or explicit approval over broad auto-approval
- leave `supports_parallel_tool_calls` disabled by default

`telecom-browser-mcp` manages browser sessions, artifacts, and other shared state. Parallel tool calls can introduce race conditions across session lifecycle and evidence paths, so this server should be treated as serialized by default.

## Recommended First Path: Stdio

Use `stdio` unless you have a specific need to exercise HTTP or SSE transport behavior.

Example `~/.codex/config.toml` entry:

```toml
[mcp_servers.telecom_browser_mcp]
command = "/absolute/path/to/repo/.venv/bin/telecom-browser-mcp-stdio"
default_tools_approval_mode = "prompt"
supports_parallel_tool_calls = false
```

Notes:

- Replace `/absolute/path/to/repo` with your local clone path.
- Using the virtualenv entrypoint avoids guessing which Python environment Codex will inherit.
- Codex accepts `default_tools_approval_mode` and `supports_parallel_tool_calls` under each `mcp_servers.<name>` entry.
- No transport environment variables are required for local stdio use.
- `default_tools_approval_mode = "prompt"` is the conservative recommendation for a browser-driving server.

If you prefer the module form instead of the console script, use:

```toml
[mcp_servers.telecom_browser_mcp]
command = "/absolute/path/to/repo/.venv/bin/python"
args = ["-m", "telecom_browser_mcp.server.stdio_server"]
default_tools_approval_mode = "prompt"
supports_parallel_tool_calls = false
```

Equivalent helper command:

```bash
codex mcp add telecom_browser_mcp -- /absolute/path/to/repo/.venv/bin/telecom-browser-mcp-stdio
```

## Local HTTP Example

Use local HTTP only when you want a localhost MCP endpoint for transport testing or a local bridge.

Start the server locally:

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

Equivalent helper command:

```bash
codex mcp add telecom_browser_mcp_http --url http://127.0.0.1:8000/mcp
```

Notes:

- Localhost is the intended local developer posture.
- A bearer token is not required for localhost-only developer use.
- This is still less conservative than stdio because it exposes a local listener.
- Do not treat this as permission to expose HTTP on a non-local interface.

## Local SSE Example

Use local SSE only when you specifically want to exercise the SSE transport.

Start the server locally:

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

Codex currently accepts URL-based MCP entries in `~/.codex/config.toml`. Keep SSE as a local or advanced transport choice, not the beginner path.

Notes:

- Localhost-only SSE is allowed for local development.
- A bearer token is not required for localhost-only developer use.
- As with local HTTP, this is not the recommended first path.

## Advanced: Non-Local Protected HTTP

This is an operator-managed deployment example, not a beginner Codex setup path.

Non-local HTTP fails closed unless both of these are set:

- `TELECOM_BROWSER_MCP_UNSAFE_BIND=1`
- `TELECOM_BROWSER_MCP_AUTH_TOKEN`

Server startup example:

```bash
cd /absolute/path/to/repo
FASTMCP_HOST=0.0.0.0 \
FASTMCP_PORT=8123 \
TELECOM_BROWSER_MCP_UNSAFE_BIND=1 \
TELECOM_BROWSER_MCP_AUTH_TOKEN="replace-with-a-strong-token" \
.venv/bin/telecom-browser-mcp-http
```

Before starting Codex, export the token in the shell environment that will launch Codex:

```bash
export TELECOM_BROWSER_MCP_AUTH_TOKEN="replace-with-the-same-strong-token"
```

Codex config example:

```toml
[mcp_servers.telecom_browser_mcp_http_remote]
url = "http://your-hostname-or-ip:8123/mcp"
bearer_token_env_var = "TELECOM_BROWSER_MCP_AUTH_TOKEN"
default_tools_approval_mode = "prompt"
supports_parallel_tool_calls = false
```

Equivalent helper command:

```bash
codex mcp add telecom_browser_mcp_http_remote \
  --url http://your-hostname-or-ip:8123/mcp \
  --bearer-token-env-var TELECOM_BROWSER_MCP_AUTH_TOKEN
```

Required safeguards:

- keep the bind/auth configuration explicit
- put the service behind reverse proxy and firewall restrictions
- rotate the bearer token through external secret management
- keep outbound egress controls in place
- configure `TELECOM_BROWSER_MCP_ALLOWED_HOSTS` for real targets

Do not use this path as your first Codex registration.

## Advanced: Non-Local Protected SSE

This is the same operator-managed posture for SSE.

Server startup example:

```bash
cd /absolute/path/to/repo
FASTMCP_HOST=0.0.0.0 \
FASTMCP_PORT=8124 \
TELECOM_BROWSER_MCP_UNSAFE_BIND=1 \
TELECOM_BROWSER_MCP_AUTH_TOKEN="replace-with-a-strong-token" \
.venv/bin/telecom-browser-mcp-sse
```

Before starting Codex, export the token in the shell environment that will launch Codex:

```bash
export TELECOM_BROWSER_MCP_AUTH_TOKEN="replace-with-the-same-strong-token"
```

Codex config example:

```toml
[mcp_servers.telecom_browser_mcp_sse_remote]
url = "http://your-hostname-or-ip:8124/sse"
bearer_token_env_var = "TELECOM_BROWSER_MCP_AUTH_TOKEN"
default_tools_approval_mode = "prompt"
supports_parallel_tool_calls = false
```

The same operator controls apply: reverse proxy, firewall rules, token rotation, outbound egress controls, and explicit allowed-host configuration.

## Approval Recommendations

Recommended starting point:

```toml
default_tools_approval_mode = "prompt"
```

Why:

- the server can open pages, wait on browser state, and collect artifacts
- some tools mutate session state
- shared sessions and evidence paths make accidental concurrency more expensive

Use `prompt` when:

- you are first wiring Codex to the server
- you are working against real targets
- you want explicit review before browser-driving or artifact-producing actions

Use a broader approval setting only when:

- you are working in a contained local harness
- you understand the session and browser side effects
- you accept the artifact and target-access implications

`supports_parallel_tool_calls` should stay disabled by default for this server. Only enable it if you have independently reviewed your own usage pattern and are confident concurrent tool execution cannot corrupt session lifecycle, evidence collection, or browser state.

## Verification After Registration

After editing `~/.codex/config.toml`, restart Codex CLI so it reloads MCP configuration.

Then verify in order:

1. Confirm Codex can see the server:

   ```bash
   codex mcp list
   codex mcp get telecom_browser_mcp
   ```

2. Ask Codex to call the first-contact-safe tools:
   - `health`
   - `capabilities`
   - `list_sessions`
3. Only after that, move on to `open_app` or session-bound tools.

Minimal first prompt inside Codex:

```text
Use the telecom_browser_mcp server and call health, then capabilities, then list_sessions.
```

For transport-level host verification outside Codex, use the repo helper:

```bash
bash scripts/run_live_transport_smoke.sh stdio
bash scripts/run_live_transport_smoke.sh http
bash scripts/run_live_transport_smoke.sh sse
```

Or run the combined host-capable verification:

```bash
bash scripts/run_live_transport_smoke.sh all
```

The current bounded release verdict is `READY_FOR_BOUNDED_RELEASE`, including verified stdio, HTTP, and SSE smoke behavior on a host-capable runtime. In constrained sandboxes, loopback socket creation or subprocess first contact can still fail for environment reasons; do not misclassify those as product regressions.

## URL Policy and Screenshot Notes

These are not extra setup steps, but they affect first use:

- `open_app` only accepts `http` and `https`
- blocked destinations include localhost/private/link-local/reserved targets unless explicitly allowed for harness mode
- configure `TELECOM_BROWSER_MCP_ALLOWED_HOSTS` for real targets
- use `TELECOM_BROWSER_MCP_ALLOW_LOCAL_TARGETS=1` only for explicit harness/local-target testing
- screenshots are sensitive and disabled by default for non-harness targets
- enable `TELECOM_BROWSER_MCP_CAPTURE_SCREENSHOTS=1` only when secure handling is in place

## Troubleshooting

### Codex does not see the MCP server

- confirm the file is `~/.codex/config.toml`
- restart Codex after editing the file
- check that the server table name is under `[mcp_servers.<name>]`
- confirm the configured `command`, `cwd`, and `url` values are valid on this host

### Wrong config path

This guide uses the global Codex CLI config file:

```text
~/.codex/config.toml
```

If you edit a different TOML file, Codex will not load this server definition.

### Python or virtualenv executable not found

- verify `.venv` exists in the repo
- verify `python -m pip install -e ".[dev]"` was run inside that virtualenv
- prefer absolute paths in `command` so Codex does not depend on a shell-specific `PATH`

### Browser dependencies missing

Install Chromium for Playwright:

```bash
.venv/bin/python -m playwright install chromium
```

Missing browser binaries are a setup problem, not a telecom-browser-mcp product regression.

### Local HTTP or SSE not reachable

- confirm the server is started in a separate shell
- confirm the `url` in `config.toml` matches the chosen host, port, and path
- use `127.0.0.1` for local-only testing
- if loopback socket creation fails on this host, classify it as an environment limitation

### Auth or token mismatch

For non-local HTTP/SSE:

- `TELECOM_BROWSER_MCP_UNSAFE_BIND=1` must be set on server startup
- `TELECOM_BROWSER_MCP_AUTH_TOKEN` must be set on server startup
- Codex must read the same token through `bearer_token_env_var`

If any of those are wrong, non-local startup or requests should fail closed.

### Setup failure vs runtime limitation

Examples of setup failures:

- wrong `config.toml` path
- bad `command` path
- missing virtualenv
- missing Playwright browser binaries
- malformed localhost URL

Examples of environment-limited runtime failures:

- loopback socket `PermissionError`
- constrained sandbox blocks subprocess stdio first contact

Those runtime limitations do not invalidate the repo's bounded release posture; they mean you need a host-capable runtime for live transport proof.

## Copy-Paste Examples

For a single place that only contains copy-pasteable TOML examples, see [codex-cli-config-examples.toml.md](/home/grimange/personal_projects/telecom-browser-mcp/docs/setup/codex-cli-config-examples.toml.md).
