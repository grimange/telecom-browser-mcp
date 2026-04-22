# Live Transport Verification Verdict

## Commands Run

```bash
.venv/bin/python -m pytest tests/integration/test_transport_entrypoints.py -q
.venv/bin/python -m ruff check .
.venv/bin/python -m bandit -q -r src
bash scripts/run_live_transport_smoke.sh stdio
bash scripts/run_live_transport_smoke.sh http
bash scripts/run_live_transport_smoke.sh sse
```

## Per-Transport Result

### Stdio

Status: `VERIFIED`

- Command: `bash scripts/run_live_transport_smoke.sh stdio`
- Result: `5 passed in 0.86s`
- Classification: verified on host-capable runtime

### Streamable HTTP

Status: `VERIFIED`

- Command: `bash scripts/run_live_transport_smoke.sh http`
- Result: `5 passed in 1.19s`
- Classification: verified on host-capable runtime

### SSE

Status: `VERIFIED`

- Command: `bash scripts/run_live_transport_smoke.sh sse`
- Result: `5 passed in 1.10s`
- Classification: verified on host-capable runtime

## Secure Configuration Behavior

### Non-Local HTTP Without Required Opt-In/Auth

- Command: `FASTMCP_HOST=0.0.0.0 .venv/bin/python -m telecom_browser_mcp.server.streamable_http_server`
- Result: failed closed with `TransportSecurityError`

### Non-Local SSE Without Required Opt-In/Auth

- Command: `FASTMCP_HOST=0.0.0.0 .venv/bin/python -m telecom_browser_mcp.server.sse_server`
- Result: failed closed with `TransportSecurityError`

### Non-Local HTTP With Explicit Opt-In + Auth

- Startup command:
  `FASTMCP_HOST=0.0.0.0 FASTMCP_PORT=8123 TELECOM_BROWSER_MCP_UNSAFE_BIND=1 TELECOM_BROWSER_MCP_AUTH_TOKEN=synthetic-token .venv/bin/python -m telecom_browser_mcp.server.streamable_http_server`
- Result: server started successfully
- Unauthenticated probe:
  `curl -i --max-time 5 http://127.0.0.1:8123/mcp`
  -> `401 Unauthorized`
- Authenticated probe:
  `curl -i --max-time 5 -H 'Authorization: Bearer synthetic-token' http://127.0.0.1:8123/mcp`
  -> authenticated path reached, `406 Not Acceptable` because the probe did not request `text/event-stream`

### Non-Local SSE With Explicit Opt-In + Auth

- Startup command:
  `FASTMCP_HOST=0.0.0.0 FASTMCP_PORT=8124 TELECOM_BROWSER_MCP_UNSAFE_BIND=1 TELECOM_BROWSER_MCP_AUTH_TOKEN=synthetic-token .venv/bin/python -m telecom_browser_mcp.server.sse_server`
- Result: server started successfully
- Unauthenticated probe:
  `curl -i --max-time 5 http://127.0.0.1:8124/sse`
  -> `401 Unauthorized`
- Authenticated probe:
  `curl -i --max-time 5 -H 'Authorization: Bearer synthetic-token' http://127.0.0.1:8124/sse`
  -> `200 OK` with `text/event-stream`

## Release Verdict

Verdict: `READY_FOR_BOUNDED_RELEASE`

Basis:

- Live stdio, HTTP, and SSE smoke checks passed on a host-capable runtime.
- Non-local HTTP/SSE fail-closed startup behavior was verified.
- Bearer-token enforcement on protected non-local HTTP/SSE paths was verified.
- No doc or helper-script drift was found during host verification.

## Remaining Residuals

- Browser request governance remains intentionally bounded to requests surfaced through Playwright routing.
- Screenshot pixel redaction remains intentionally residual and is not implemented.
- Production posture still depends on operator-managed reverse proxy, firewall, secret rotation, and outbound egress controls.

## Operator Prerequisites Before Production Deployment

- Keep HTTP/SSE on localhost unless remote exposure is intentional.
- For non-local HTTP/SSE, set both `TELECOM_BROWSER_MCP_UNSAFE_BIND=1` and `TELECOM_BROWSER_MCP_AUTH_TOKEN`.
- Rotate `TELECOM_BROWSER_MCP_AUTH_TOKEN` through external secret-management and deployment rollout.
- Put non-local HTTP/SSE behind reverse proxy and firewall restrictions.
- Configure `TELECOM_BROWSER_MCP_ALLOWED_HOSTS` for real targets.
- Use `TELECOM_BROWSER_MCP_ALLOW_LOCAL_TARGETS=1` only for explicit harness/local-target testing.
- Treat screenshots as high-risk artifacts and enable them only when secure handling is in place.

## Docs Accuracy

Current docs were accurate enough for host execution. No correction to commands or security posture was required from this verification pass.
