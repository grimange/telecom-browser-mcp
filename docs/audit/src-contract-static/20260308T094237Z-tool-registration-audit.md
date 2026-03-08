# Tool Registration Audit

- Timestamp: `20260308T094237Z`
- Scope: `src/` static inspection

## Search Patterns Used

- `@mcp.tool`
- `@mcp.tool()`
- `server.tool`
- `register_tool`
- `tool_registry`
- `FastMCP`
- `inputSchema`

## Registration Sites Found

### Site R1 (Canonical)

- File: `src/telecom_browser_mcp/server/stdio_server.py:46-59`
- Symbol: `_register_tools_with_fastmcp(server, app)`
- Mechanism:
  - Enforces strict arg model (`ArgModelBase.model_config.extra = "forbid"`).
  - Iterates `TOOL_NAMES`, resolves `handler = getattr(app.orchestrator, tool_name, None)`, registers with `server.tool(name=tool_name)(handler)`.
- Schema style: inferred by FastMCP from bound handler signatures (no explicit `inputSchema` declarations in `src/`).
- Wrapper: none in current source path (direct bound method registration).

### Shared Bootstrap Callers

- `src/telecom_browser_mcp/server/stdio_server.py:116-117`
- `src/telecom_browser_mcp/server/sse_server.py:19-20`
- `src/telecom_browser_mcp/server/streamable_http_server.py:19-20`

All transports reuse the same registration function above.

## Registered Tools and Visible Signatures

| Tool | File | Function | Visible Signature | Schema Explicit/ Inferred | Wrapped by Helper |
|---|---|---|---|---|---|
| `health` | `tools/orchestrator.py:51` | `ToolOrchestrator.health` | `health()` | inferred | no |
| `capabilities` | `tools/orchestrator.py:65` | `ToolOrchestrator.capabilities` | `capabilities(include_groups: bool = True)` | inferred | no |
| `open_app` | `tools/orchestrator.py:180` | `ToolOrchestrator.open_app` | `open_app(url: str, adapter_name: str | None = None)` | inferred | no |
| `login_agent` | `tools/orchestrator.py:286` | `ToolOrchestrator.login_agent` | `login_agent(session_id: str, username: str, password: str, tenant: str | None = None)` | inferred | no |
| `wait_for_ready` | `tools/orchestrator.py:303` | `ToolOrchestrator.wait_for_ready` | `wait_for_ready(session_id: str, timeout_ms: int = 30000)` | inferred | no |
| `list_sessions` | `tools/orchestrator.py:243` | `ToolOrchestrator.list_sessions` | `list_sessions()` | inferred | no |
| `close_session` | `tools/orchestrator.py:262` | `ToolOrchestrator.close_session` | `close_session(session_id: str)` | inferred | no |
| `reset_session` | `tools/orchestrator.py:274` | `ToolOrchestrator.reset_session` | `reset_session(session_id: str)` | inferred | no |
| `get_registration_status` | `tools/orchestrator.py:337` | `ToolOrchestrator.get_registration_status` | `get_registration_status(session_id: str)` | inferred | no |
| `wait_for_registration` | `tools/orchestrator.py:352` | `ToolOrchestrator.wait_for_registration` | `wait_for_registration(session_id: str, expected: str = 'registered', timeout_ms: int = 30000)` | inferred | no |
| `assert_registered` | `tools/orchestrator.py:397` | `ToolOrchestrator.assert_registered` | `assert_registered(session_id: str, timeout_ms: int = 30000)` | inferred | no |
| `wait_for_incoming_call` | `tools/orchestrator.py:400` | `ToolOrchestrator.wait_for_incoming_call` | `wait_for_incoming_call(session_id: str, timeout_ms: int = 30000)` | inferred | no |
| `answer_call` | `tools/orchestrator.py:443` | `ToolOrchestrator.answer_call` | `answer_call(session_id: str, timeout_ms: int = 15000)` | inferred | no |
| `hangup_call` | `tools/orchestrator.py:509` | `ToolOrchestrator.hangup_call` | `hangup_call(session_id: str, timeout_ms: int = 15000)` | inferred | no |
| `get_ui_call_state` | `tools/orchestrator.py:523` | `ToolOrchestrator.get_ui_call_state` | `get_ui_call_state(session_id: str)` | inferred | no |
| `get_active_session_snapshot` | `tools/orchestrator.py:538` | `ToolOrchestrator.get_active_session_snapshot` | `get_active_session_snapshot(session_id: str)` | inferred | no |
| `get_store_snapshot` | `tools/orchestrator.py:553` | `ToolOrchestrator.get_store_snapshot` | `get_store_snapshot(session_id: str)` | inferred | no |
| `get_peer_connection_summary` | `tools/orchestrator.py:568` | `ToolOrchestrator.get_peer_connection_summary` | `get_peer_connection_summary(session_id: str)` | inferred | no |
| `get_webrtc_stats` | `tools/orchestrator.py:583` | `ToolOrchestrator.get_webrtc_stats` | `get_webrtc_stats(session_id: str)` | inferred | no |
| `get_environment_snapshot` | `tools/orchestrator.py:657` | `ToolOrchestrator.get_environment_snapshot` | `get_environment_snapshot(session_id: str)` | inferred | no |
| `screenshot` | `tools/orchestrator.py:671` | `ToolOrchestrator.screenshot` | `screenshot(session_id: str, label: str = 'manual-capture')` | inferred | no |
| `collect_browser_logs` | `tools/orchestrator.py:718` | `ToolOrchestrator.collect_browser_logs` | `collect_browser_logs(session_id: str)` | inferred | no |
| `collect_debug_bundle` | `tools/orchestrator.py:605` | `ToolOrchestrator.collect_debug_bundle` | `collect_debug_bundle(session_id: str)` | inferred | no |
| `diagnose_registration_failure` | `tools/orchestrator.py:740` | `ToolOrchestrator.diagnose_registration_failure` | `diagnose_registration_failure(session_id: str)` | inferred | no |
| `diagnose_incoming_call_failure` | `tools/orchestrator.py:765` | `ToolOrchestrator.diagnose_incoming_call_failure` | `diagnose_incoming_call_failure(session_id: str)` | inferred | no |
| `diagnose_answer_failure` | `tools/orchestrator.py:790` | `ToolOrchestrator.diagnose_answer_failure` | `diagnose_answer_failure(session_id: str)` | inferred | no |
| `diagnose_one_way_audio` | `tools/orchestrator.py:816` | `ToolOrchestrator.diagnose_one_way_audio` | `diagnose_one_way_audio(session_id: str)` | inferred | no |

## Static Conclusion

- Current `src` shows one registration strategy and no synthetic `**kwargs` wrapper in the canonical path.
- Registration-to-handler binding is direct and signature-driven.
