# 02 - MCP Capability Inventory

## Registered MCP Tools
Source-registered via `FastMCP` decorators:
- `health`
- `capabilities`
- `open_app`
- `list_sessions`
- `close_session`
- `login_agent`
- `wait_for_ready`
- `wait_for_registration`
- `wait_for_incoming_call`
- `answer_call`
- `get_active_session_snapshot`
- `get_peer_connection_summary`
- `collect_debug_bundle`
- `diagnose_answer_failure`

Status: Confirmed by source and tests.

## Canonical Contract Inventory
Canonical tool input models are defined in one map and asserted against registered tools.

- Support tools: `health`, `capabilities`
- M1 tools: 12 telecom/session tools

Status: Confirmed by source/tests.

## Transport Surfaces
- STDIO entrypoint (`telecom-browser-mcp-stdio`)
- SSE entrypoint (`telecom-browser-mcp-sse`)
- Streamable HTTP entrypoint (`telecom-browser-mcp-http`)

Status: Confirmed by source/package metadata; runtime validation unverified for SSE/HTTP in this run.

## Adapter Capability Surfaces
- `generic`: fallback, mostly unsupported operations.
- `fake_dialer`: deterministic telecom-flow support for test harness.
- `apntalk`: scaffolded readiness + limited webrtc summary support shape.

Status: Confirmed by source and e2e harness tests (for `fake_dialer`).

## First-Contact Readiness
Integration test confirms first-contact tool listing and invocation over stdio:
- discovery includes `health`, `capabilities`, `list_sessions`
- each responds with `ok=true` and envelope fields

Status: Confirmed by tests.

## Evidence References
- `src/telecom_browser_mcp/server/app.py:19`
- `src/telecom_browser_mcp/server/stdio_server.py:1`
- `src/telecom_browser_mcp/server/sse_server.py:1`
- `src/telecom_browser_mcp/server/streamable_http_server.py:1`
- `src/telecom_browser_mcp/contracts/m1_contracts.py:15`
- `src/telecom_browser_mcp/adapters/generic.py:7`
- `src/telecom_browser_mcp/adapters/fake_dialer.py:10`
- `src/telecom_browser_mcp/adapters/apntalk.py:10`
- `tests/integration/test_stdio_smoke.py:28`
- `pyproject.toml:26`
