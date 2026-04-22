# Codex MCP Setup

Use stdio for local Codex registration unless you have a specific reason to test HTTP/SSE.

```bash
.venv/bin/python -m pip install -e ".[dev]"
telecom-browser-mcp-stdio
```

Local stdio smoke verification on a host-capable runtime:

```bash
bash scripts/run_live_transport_smoke.sh stdio
```

HTTP/SSE transports default to `127.0.0.1`. A non-local bind is rejected unless the deployment explicitly opts in and configures a bearer token:

```bash
export FASTMCP_HOST=0.0.0.0
export TELECOM_BROWSER_MCP_UNSAFE_BIND=1
export TELECOM_BROWSER_MCP_AUTH_TOKEN="replace-with-a-strong-token"
telecom-browser-mcp-http
```

Local HTTP smoke verification on a host-capable runtime:

```bash
bash scripts/run_live_transport_smoke.sh http
```

Local SSE smoke verification on a host-capable runtime:

```bash
bash scripts/run_live_transport_smoke.sh sse
```

Do not expose unauthenticated HTTP/SSE. If a client cannot send bearer tokens with the current MCP transport stack, keep the server on localhost behind a local client bridge or a separate authenticated reverse proxy.

Browser navigation is guarded by URL egress policy. Use `TELECOM_BROWSER_MCP_ALLOWED_HOSTS` to list allowed production hosts. Local harness targets require:

```bash
export TELECOM_BROWSER_MCP_ALLOWED_HOSTS=127.0.0.1,localhost
export TELECOM_BROWSER_MCP_ALLOW_LOCAL_TARGETS=1
```

These local-target settings are for deterministic harnesses only, not production exposure.

Live transport verification requires a host runtime that permits subprocesses and loopback sockets:

```bash
bash scripts/run_live_transport_smoke.sh all
```

If loopback socket creation fails with `Operation not permitted`, classify HTTP/SSE live verification as an environment limitation. If stdio first contact times out only inside a constrained sandbox, classify that as an environment limitation rather than a transport regression. Do not mark HTTP/SSE or stdio runtime-compatible until the host-capable commands pass.
