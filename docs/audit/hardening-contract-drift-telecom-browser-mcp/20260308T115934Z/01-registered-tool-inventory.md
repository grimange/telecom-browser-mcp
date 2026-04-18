# 01 Registered Tool Inventory

## Registered MCP Tools (14)
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

## Registration Path
- Single authoritative registration path in `src/telecom_browser_mcp/server/app.py:create_mcp_server`.
- Transport entrypoints (`stdio/sse/streamable-http`) delegate to same factory.

See `registered-tools.json` and `tool-contract-matrix.json`.
