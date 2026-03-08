# 04 - Tool Contract Matrix

## Matrix
| Tool | Input Model | Extra Fields Forbidden | Runtime Validation | Response Envelope | Drift Status | Notes |
|---|---|---|---|---|---|---|
| health | EmptyInput | Yes | Yes | ToolResponse v1 | No drift found | first-contact support |
| capabilities | EmptyInput | Yes | Yes | ToolResponse v1 | No drift found | includes tool list |
| open_app | OpenAppInput | Yes | Yes | ToolResponse v1 | No drift found | degraded open still `ok=true` |
| list_sessions | EmptyInput | Yes | Yes | ToolResponse v1 | No drift found | summary-only session list |
| close_session | SessionInput | Yes | Yes | ToolResponse v1 | No drift found | idempotent not provided |
| login_agent | LoginInput | Yes | Yes | ToolResponse v1 | No drift found | adapter-dependent |
| wait_for_ready | TimeoutInput | Yes | Yes | ToolResponse v1 | No drift found | retryable timeout |
| wait_for_registration | TimeoutInput | Yes | Yes | ToolResponse v1 | No drift found | explicit error code |
| wait_for_incoming_call | TimeoutInput | Yes | Yes | ToolResponse v1 | No drift found | explicit error code |
| answer_call | TimeoutInput | Yes | Yes | ToolResponse v1 | No drift found | failure emits diagnostics + bundle |
| get_active_session_snapshot | SessionInput | Yes | Yes | ToolResponse v1 | No drift found | source=session manager |
| get_peer_connection_summary | SessionInput | Yes | Yes | ToolResponse v1 | No drift found | adapter/runtime dependent |
| collect_debug_bundle | CollectDebugBundleInput | Yes | Yes | ToolResponse v1 | No drift found | artifact refs included |
| diagnose_answer_failure | SessionInput | Yes | Yes | ToolResponse v1 | No drift found | deterministic diagnosis structure |

## Contract Findings
- Canonical tool map is centralized (`CANONICAL_TOOL_INPUT_MODELS`) and reused for schema generation.
- Registration side has an assertion that registered set equals canonical model keys.
- Published schemas match generated schemas in tests.
- Runtime rejects undeclared fields across tools.
- Envelope contains deterministic `ok/tool/data/diagnostics/artifacts/meta` structure with structured `error` on failures.

## Residual Risks
- `data` payload is intentionally open (`dict[str, Any]`), so field-level per-tool shape is convention-driven rather than strict per-tool output models.
- `open_app` success semantics include degraded sessions.

## Evidence References
- `src/telecom_browser_mcp/contracts/m1_contracts.py:15`
- `src/telecom_browser_mcp/server/app.py:75`
- `src/telecom_browser_mcp/models/tools.py:8`
- `src/telecom_browser_mcp/models/common.py:46`
- `src/telecom_browser_mcp/tools/service.py:38`
- `tests/contract/test_schema_runtime_parity.py:19`
- `tests/contract/test_schema_runtime_parity.py:28`
- `tests/contract/test_m1_tool_envelopes.py:8`
- `docs/contracts/m1/open_app.schema.json`
