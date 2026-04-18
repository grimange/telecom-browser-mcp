# 07 - Transport and Configuration Assumptions

## Launch Paths
- stdio: `python -m telecom_browser_mcp`
- SSE: `python -m telecom_browser_mcp.server.sse_server`
- streamable-http: `python -m telecom_browser_mcp.server.streamable_http_server`

## Configuration Inputs
- `PYTHONPATH=src`
- `FASTMCP_HOST`
- `FASTMCP_PORT`
- strict runtime gate: `MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME=1`

## Remediations Applied During This Run
- Added executable module entry guards for SSE/HTTP server modules.
- Updated server bootstrap to read host/port from env for transport tests.

## Current Status
- Strict transport smoke now passes on all three transports in host-lane run.
