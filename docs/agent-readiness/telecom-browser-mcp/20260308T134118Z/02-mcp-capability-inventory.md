# 02 - MCP Capability Inventory

## Registered Tool Surface
- `health`, `capabilities`
- `open_app`, `list_sessions`, `close_session`
- `login_agent`, `wait_for_ready`, `wait_for_registration`, `wait_for_incoming_call`, `answer_call`
- `get_active_session_snapshot`, `get_peer_connection_summary`
- `collect_debug_bundle`, `diagnose_answer_failure`

Status: Confirmed by source/tests.

## Canonical Contract Surface
- Single canonical contract map in `CANONICAL_TOOL_INPUT_MODELS`.
- Server bootstrap asserts registration set equality to canonical keys.
- Published schemas generated from canonical models.

Status: Confirmed by source/schema tests.

## Transport Surface
- stdio: runtime first-contact validated.
- sse/streamable-http: entrypoint routing validated; live smoke tests exist and are environment-sensitive.

Status: Confirmed by tests/source; live runtime may be unverified when skipped.

## Evidence References
- `src/telecom_browser_mcp/server/app.py:75`
- `src/telecom_browser_mcp/contracts/m1_contracts.py:35`
- `tests/integration/test_stdio_smoke.py:28`
- `tests/integration/test_transport_entrypoints.py:14`
- `tests/integration/test_http_transport_smoke.py:75`
