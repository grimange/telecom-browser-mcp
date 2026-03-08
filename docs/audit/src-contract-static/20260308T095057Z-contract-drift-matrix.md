# Contract Drift Matrix

- Timestamp: `20260308T095057Z`
- Scope: exposed tools in `TOOL_NAMES` (`src/telecom_browser_mcp/server/stdio_server.py:15-43`)
- Registration site for all rows: `src/telecom_browser_mcp/server/stdio_server.py:46-59`

Legend:

- Canonical public path = FastMCP registration and invocation.
- Internal helper path = `TelecomBrowserApp.dispatch(tool_name, **kwargs)` (`src/telecom_browser_mcp/server/app.py:72-78`).

| Tool | Registration Site | Public Signature | Wrapper Signature | Runtime Signature | Drift Type | Severity |
|---|---|---|---|---|---|---|
| `health` | `stdio_server.py:46-59` | `health()` | direct handler (none) | `health()` | none (canonical); internal compatibility path is validated | low-medium |
| `capabilities` | `stdio_server.py:46-59` | `capabilities(include_groups: bool = True)` | direct handler (none) | `capabilities(include_groups: bool = True)` | none (canonical); internal compatibility path is validated | low |
| `open_app` | `stdio_server.py:46-59` | `open_app(url: str, adapter_name: str | None = None)` | direct handler (none) | `open_app(url: str, adapter_name: str | None = None)` | none (canonical); internal compatibility path is validated | low |
| `login_agent` | `stdio_server.py:46-59` | `login_agent(session_id: str, username: str, password: str, tenant: str | None = None)` | direct handler (none) | `login_agent(session_id: str, username: str, password: str, tenant: str | None = None)` | none (canonical); internal compatibility path is validated | low |
| `wait_for_ready` | `stdio_server.py:46-59` | `wait_for_ready(session_id: str, timeout_ms: int = 30000)` | direct handler (none) | `wait_for_ready(session_id: str, timeout_ms: int = 30000)` | none (canonical); internal compatibility path is validated | low |
| `list_sessions` | `stdio_server.py:46-59` | `list_sessions()` | direct handler (none) | `list_sessions()` | none (canonical); internal compatibility path is validated | low-medium |
| `close_session` | `stdio_server.py:46-59` | `close_session(session_id: str)` | direct handler (none) | `close_session(session_id: str)` | none (canonical); internal compatibility path is validated | low |
| `reset_session` | `stdio_server.py:46-59` | `reset_session(session_id: str)` | direct handler (none) | `reset_session(session_id: str)` | none (canonical); internal compatibility path is validated | low |
| `get_registration_status` | `stdio_server.py:46-59` | `get_registration_status(session_id: str)` | direct handler (none) | `get_registration_status(session_id: str)` | none (canonical); internal compatibility path is validated | low |
| `wait_for_registration` | `stdio_server.py:46-59` | `wait_for_registration(session_id: str, expected: str = 'registered', timeout_ms: int = 30000)` | direct handler (none) | `wait_for_registration(session_id: str, expected: str = 'registered', timeout_ms: int = 30000)` | none (canonical); internal compatibility path is validated | low |
| `assert_registered` | `stdio_server.py:46-59` | `assert_registered(session_id: str, timeout_ms: int = 30000)` | direct handler (none) | `assert_registered(session_id: str, timeout_ms: int = 30000)` | none (canonical); internal compatibility path is validated | low |
| `wait_for_incoming_call` | `stdio_server.py:46-59` | `wait_for_incoming_call(session_id: str, timeout_ms: int = 30000)` | direct handler (none) | `wait_for_incoming_call(session_id: str, timeout_ms: int = 30000)` | none (canonical); internal compatibility path is validated | low |
| `answer_call` | `stdio_server.py:46-59` | `answer_call(session_id: str, timeout_ms: int = 15000)` | direct handler (none) | `answer_call(session_id: str, timeout_ms: int = 15000)` | none (canonical); internal compatibility path is validated | low |
| `hangup_call` | `stdio_server.py:46-59` | `hangup_call(session_id: str, timeout_ms: int = 15000)` | direct handler (none) | `hangup_call(session_id: str, timeout_ms: int = 15000)` | none (canonical); internal compatibility path is validated | low |
| `get_ui_call_state` | `stdio_server.py:46-59` | `get_ui_call_state(session_id: str)` | direct handler (none) | `get_ui_call_state(session_id: str)` | none (canonical); internal compatibility path is validated | low |
| `get_active_session_snapshot` | `stdio_server.py:46-59` | `get_active_session_snapshot(session_id: str)` | direct handler (none) | `get_active_session_snapshot(session_id: str)` | none (canonical); internal compatibility path is validated | low |
| `get_store_snapshot` | `stdio_server.py:46-59` | `get_store_snapshot(session_id: str)` | direct handler (none) | `get_store_snapshot(session_id: str)` | none (canonical); internal compatibility path is validated | low |
| `get_peer_connection_summary` | `stdio_server.py:46-59` | `get_peer_connection_summary(session_id: str)` | direct handler (none) | `get_peer_connection_summary(session_id: str)` | none (canonical); internal compatibility path is validated | low |
| `get_webrtc_stats` | `stdio_server.py:46-59` | `get_webrtc_stats(session_id: str)` | direct handler (none) | `get_webrtc_stats(session_id: str)` | none (canonical); internal compatibility path is validated | low |
| `get_environment_snapshot` | `stdio_server.py:46-59` | `get_environment_snapshot(session_id: str)` | direct handler (none) | `get_environment_snapshot(session_id: str)` | none (canonical); internal compatibility path is validated | low |
| `screenshot` | `stdio_server.py:46-59` | `screenshot(session_id: str, label: str = 'manual-capture')` | direct handler (none) | `screenshot(session_id: str, label: str = 'manual-capture')` | none (canonical); internal compatibility path is validated | low |
| `collect_browser_logs` | `stdio_server.py:46-59` | `collect_browser_logs(session_id: str)` | direct handler (none) | `collect_browser_logs(session_id: str)` | none (canonical); internal compatibility path is validated | low |
| `collect_debug_bundle` | `stdio_server.py:46-59` | `collect_debug_bundle(session_id: str)` | direct handler (none) | `collect_debug_bundle(session_id: str)` | none (canonical); internal compatibility path is validated | low |
| `diagnose_registration_failure` | `stdio_server.py:46-59` | `diagnose_registration_failure(session_id: str)` | direct handler (none) | `diagnose_registration_failure(session_id: str)` | none (canonical); internal compatibility path is validated | low |
| `diagnose_incoming_call_failure` | `stdio_server.py:46-59` | `diagnose_incoming_call_failure(session_id: str)` | direct handler (none) | `diagnose_incoming_call_failure(session_id: str)` | none (canonical); internal compatibility path is validated | low |
| `diagnose_answer_failure` | `stdio_server.py:46-59` | `diagnose_answer_failure(session_id: str)` | direct handler (none) | `diagnose_answer_failure(session_id: str)` | none (canonical); internal compatibility path is validated | low |
| `diagnose_one_way_audio` | `stdio_server.py:46-59` | `diagnose_one_way_audio(session_id: str)` | direct handler (none) | `diagnose_one_way_audio(session_id: str)` | none (canonical); internal compatibility path is validated | low |

## Cross-Cutting Drift Observation

| Tool | Registration Site | Public Signature | Wrapper Signature | Runtime Signature | Drift Type | Severity |
|---|---|---|---|---|---|---|
| All tools via internal helper path | N/A (not public FastMCP registration) | explicit per-tool signatures | `dispatch(tool_name: str, **kwargs)` | forwarded as `handler(**normalized_kwargs)` after `_validate_dispatch_kwargs` | synthetic envelope compatibility risk (contained) | low |

## Static Verdict

- No active public schema/runtime drift found in canonical tool registration path.
- Residual drift surface is internal compatibility logic in `server/app.py`, protected by strict validation.
