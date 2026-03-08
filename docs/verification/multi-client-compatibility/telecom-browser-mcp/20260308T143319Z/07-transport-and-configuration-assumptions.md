# 07 - Transport and Configuration Assumptions

## Server Launch/Transport Assumptions
- stdio:
  - `telecom-browser-mcp-stdio`
  - `python -m telecom_browser_mcp`
- SSE:
  - `telecom-browser-mcp-sse`
  - `python -m telecom_browser_mcp.server.sse_server`
- streamable-http:
  - `telecom-browser-mcp-http`
  - `python -m telecom_browser_mcp.server.streamable_http_server`

## Environment Variables Used by Transport Smoke
- `PYTHONPATH=<repo>/src`
- `FASTMCP_HOST=127.0.0.1`
- `FASTMCP_PORT=<free_port>`
- Optional strict gate: `MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME=1`

## Observed Constraints in This Run
- stdio smoke: timeout after 30s
- SSE smoke: `[Errno 1] Operation not permitted`
- streamable-http smoke: `[Errno 1] Operation not permitted`

## Interpretation
These constraints are environment limitations in this workspace and are not sufficient evidence of server defect by themselves.
