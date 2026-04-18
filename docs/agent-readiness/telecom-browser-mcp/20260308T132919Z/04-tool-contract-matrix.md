# 04 - Tool Contract Matrix

| Tool | Input Model | Runtime Extra-Field Rejection | Envelope | Drift Status | Notes |
|---|---|---|---|---|---|
| health | EmptyInput | Yes | ToolResponse v1 | No drift found | first-contact |
| capabilities | EmptyInput | Yes | ToolResponse v1 | No drift found | includes tool list |
| open_app | OpenAppInput | Yes | ToolResponse v1 | No drift found | includes `ready_for_actions` |
| list_sessions | EmptyInput | Yes | ToolResponse v1 | No drift found | session summary list |
| close_session | SessionInput | Yes | ToolResponse v1 | No drift found | lock-protected close |
| login_agent | LoginInput | Yes | ToolResponse v1 | No drift found | lock-protected op |
| wait_for_ready | TimeoutInput | Yes | ToolResponse v1 | No drift found | retryable timeout errors |
| wait_for_registration | TimeoutInput | Yes | ToolResponse v1 | No drift found | state diagnostics on failures |
| wait_for_incoming_call | TimeoutInput | Yes | ToolResponse v1 | No drift found | state diagnostics on failures |
| answer_call | TimeoutInput | Yes | ToolResponse v1 | No drift found | diagnostics + evidence bundle |
| get_active_session_snapshot | SessionInput | Yes | ToolResponse v1 | No drift found | read-only snapshot |
| get_peer_connection_summary | SessionInput | Yes | ToolResponse v1 | No drift found | lock-protected runtime read |
| collect_debug_bundle | CollectDebugBundleInput | Yes | ToolResponse v1 | No drift found | lock-protected capture |
| diagnose_answer_failure | SessionInput | Yes | ToolResponse v1 | No drift found | deterministic diagnosis payload |

## Evidence References
- `src/telecom_browser_mcp/contracts/m1_contracts.py:15`
- `src/telecom_browser_mcp/models/tools.py:8`
- `src/telecom_browser_mcp/models/common.py:46`
- `src/telecom_browser_mcp/tools/service.py:179`
- `src/telecom_browser_mcp/tools/service.py:240`
- `tests/contract/test_schema_runtime_parity.py:28`
- `tests/contract/test_m1_tool_envelopes.py:23`
- `tests/contract/test_service_contracts.py:7`
