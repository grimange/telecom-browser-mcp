# 02 - MCP Capability Inventory

## Registered Tools
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

Status: Confirmed by source + tests.

## Canonical Contract Surface
- Canonical map: `CANONICAL_TOOL_INPUT_MODELS`
- Registration set equality assertion enforced in server bootstrap.
- Published schemas under `docs/contracts/m1/`.

Status: Confirmed by source + schema parity tests.

## Capability/Transport Notes
- First-contact trio (`health`, `capabilities`, `list_sessions`) validated over stdio.
- SSE and streamable HTTP entrypoints validated for transport wiring.
- Live SSE/HTTP session-level interoperability remains unverified in this run.

## Evidence References
- `src/telecom_browser_mcp/server/app.py:19`
- `src/telecom_browser_mcp/server/app.py:75`
- `src/telecom_browser_mcp/contracts/m1_contracts.py:35`
- `tests/contract/test_schema_runtime_parity.py:19`
- `tests/integration/test_stdio_smoke.py:28`
- `tests/integration/test_transport_entrypoints.py:14`
- `README.md:44`
