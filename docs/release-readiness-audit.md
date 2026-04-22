# Release Readiness Audit

## Local Stdio Verification

Classification: `READY_WITH_OPERATOR_ACTION`

- Repo support exists through `telecom-browser-mcp-stdio`, `python -m telecom_browser_mcp`, and `tests/integration/test_stdio_smoke.py`.
- Operator action required: run on a host-capable runtime that allows subprocess startup and stdio first contact.
- Current sandbox result is environment-blocked and should not be treated as a product regression.

## Local HTTP Verification

Classification: `READY_WITH_OPERATOR_ACTION`

- Repo support exists through `telecom-browser-mcp-http` and `tests/integration/test_http_transport_smoke.py`.
- Default localhost bind is safe for local verification.
- Operator action required: run on a host-capable runtime that allows loopback sockets.

## Local SSE Verification

Classification: `READY_WITH_OPERATOR_ACTION`

- Repo support exists through `telecom-browser-mcp-sse` and `tests/integration/test_http_transport_smoke.py`.
- Default localhost bind is safe for local verification.
- Operator action required: run on a host-capable runtime that allows loopback sockets.

## Secure Non-Local Deployment With Explicit Auth

Classification: `PARTIALLY_READY`

- Non-local HTTP/SSE startup is fail-closed unless `TELECOM_BROWSER_MCP_UNSAFE_BIND=1` and `TELECOM_BROWSER_MCP_AUTH_TOKEN` are configured.
- Docs now describe bearer token setup, localhost expectations, reverse proxy/firewall posture, and outbound egress controls as defense in depth.
- Residual: production posture still depends on operator-managed token rotation, reverse proxy policy, and host/container network controls outside this repo.

## Harness/Local-Target Testing Versus Real-Target Use

Classification: `READY`

- Repo clearly separates harness/local-target mode from real-target mode through `TELECOM_BROWSER_MCP_ALLOW_LOCAL_TARGETS` and `TELECOM_BROWSER_MCP_ALLOWED_HOSTS`.
- Browser request governance and artifact sensitivity boundaries are documented.
- Screenshots remain intentionally sensitive and are disabled by default for non-harness targets.
