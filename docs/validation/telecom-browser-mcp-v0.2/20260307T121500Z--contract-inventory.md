# Contract Inventory (20260307T121500Z)

Canonical synthesized contract source:
- `docs/telecom-browser-mcp-implementation-plan-v0.2.md`
- `README.md`
- `src/telecom_browser_mcp/server/stdio_server.py` (`TOOL_NAMES`)

Contract classifications used:
- explicit
- inferred
- implementation-only
- ambiguous

Tool inventory (explicit):
- open_app, login_agent, wait_for_ready, list_sessions, close_session, reset_session
- get_registration_status, wait_for_registration, assert_registered
- wait_for_incoming_call, answer_call, hangup_call, get_ui_call_state
- get_active_session_snapshot, get_store_snapshot, get_peer_connection_summary, get_webrtc_stats, get_environment_snapshot
- diagnose_registration_failure, diagnose_incoming_call_failure, diagnose_answer_failure, diagnose_one_way_audio
- screenshot, collect_browser_logs, collect_debug_bundle

Ambiguous items:
- minimum required depth of `diagnose_one_way_audio` for v0.2 signoff
- minimum required protocol proof for interop PASS in this environment
