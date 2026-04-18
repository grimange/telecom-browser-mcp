# 02 - MCP Capability Inventory

## Registered Tool Surface
- Support tools: `health`, `capabilities`
- Telecom tools: `open_app`, `list_sessions`, `close_session`, `login_agent`, `wait_for_ready`, `wait_for_registration`, `wait_for_incoming_call`, `answer_call`, `get_active_session_snapshot`, `get_peer_connection_summary`, `collect_debug_bundle`, `diagnose_answer_failure`

## Registration Evidence
- MCP registration/dispatch: `src/telecom_browser_mcp/server/app.py:11`
- Canonical input model map: `src/telecom_browser_mcp/contracts/m1_contracts.py:35`
- Registration alignment guard assertion: `src/telecom_browser_mcp/server/app.py:75`

## Transport Entry Points
- stdio: `src/telecom_browser_mcp/server/stdio_server.py`
- SSE: `src/telecom_browser_mcp/server/sse_server.py:5`
- streamable-http: `src/telecom_browser_mcp/server/streamable_http_server.py:5`

## Capability Evidence Quality
- Contract discoverability: Confirmed by source/tests.
- Runtime transport interoperability: Partially validated; environment-gated for live proof.
