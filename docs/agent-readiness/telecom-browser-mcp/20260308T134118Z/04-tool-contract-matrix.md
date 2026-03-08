# 04 - Tool Contract Matrix

| Tool | Input Contract | Undeclared Field Rejection | Envelope | Drift | Notes |
|---|---|---|---|---|---|
| health | EmptyInput | Yes | ToolResponse v1 | none | first-contact |
| capabilities | EmptyInput | Yes | ToolResponse v1 | none | includes tools list |
| open_app | OpenAppInput | Yes | ToolResponse v1 | none | includes `ready_for_actions` |
| list_sessions | EmptyInput | Yes | ToolResponse v1 | none | deterministic summary |
| close_session | SessionInput | Yes | ToolResponse v1 | none | lock-timeout returns session_busy |
| login_agent | LoginInput | Yes | ToolResponse v1 | none | lock guarded |
| wait_for_ready | TimeoutInput | Yes | ToolResponse v1 | none | lock guarded + retryable timeout/busy |
| wait_for_registration | TimeoutInput | Yes | ToolResponse v1 | none | state diagnostics on failure |
| wait_for_incoming_call | TimeoutInput | Yes | ToolResponse v1 | none | state diagnostics on failure |
| answer_call | TimeoutInput | Yes | ToolResponse v1 | none | diagnostics + bundle on failure |
| get_active_session_snapshot | SessionInput | Yes | ToolResponse v1 | none | read-only snapshot |
| get_peer_connection_summary | SessionInput | Yes | ToolResponse v1 | none | lock guarded |
| collect_debug_bundle | CollectDebugBundleInput | Yes | ToolResponse v1 | none | lock guarded |
| diagnose_answer_failure | SessionInput | Yes | ToolResponse v1 | none | deterministic diagnosis |

## Evidence References
- `src/telecom_browser_mcp/contracts/m1_contracts.py:15`
- `src/telecom_browser_mcp/models/tools.py:8`
- `src/telecom_browser_mcp/models/common.py:46`
- `tests/contract/test_schema_runtime_parity.py:28`
- `tests/contract/test_m1_tool_envelopes.py:23`
- `tests/contract/test_service_contracts.py:7`
