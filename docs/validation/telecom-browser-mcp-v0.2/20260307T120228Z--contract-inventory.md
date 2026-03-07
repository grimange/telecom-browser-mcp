# Contract Inventory (20260307T120228Z)

Canonical synthesized contract source:
- `docs/telecom-browser-mcp-implementation-plan-v0.2.md` (explicit tool catalog + contract rules)
- `README.md` (explicit behavior summary)
- `src/telecom_browser_mcp/server/stdio_server.py` (authoritative exposed tool surface)

## Classification rules
- explicit: directly specified in plan/readme
- inferred: required by architecture/test intent
- implementation-only: behavior present in code but not explicitly contracted
- ambiguous: not precise enough to assert pass/fail

## Tool contracts
- TOOL::open_app (explicit)
- TOOL::login_agent (explicit)
- TOOL::wait_for_ready (explicit)
- TOOL::list_sessions (explicit)
- TOOL::close_session (explicit)
- TOOL::reset_session (explicit)
- TOOL::get_registration_status (explicit)
- TOOL::wait_for_registration (explicit)
- TOOL::assert_registered (explicit)
- TOOL::wait_for_incoming_call (explicit)
- TOOL::answer_call (explicit)
- TOOL::hangup_call (explicit)
- TOOL::get_ui_call_state (explicit)
- TOOL::get_active_session_snapshot (explicit)
- TOOL::get_store_snapshot (explicit)
- TOOL::get_peer_connection_summary (explicit)
- TOOL::get_webrtc_stats (explicit)
- TOOL::get_environment_snapshot (explicit)
- TOOL::screenshot (explicit)
- TOOL::collect_browser_logs (explicit)
- TOOL::collect_debug_bundle (explicit)
- TOOL::diagnose_registration_failure (explicit)
- TOOL::diagnose_incoming_call_failure (explicit)
- TOOL::diagnose_answer_failure (explicit)
- TOOL::diagnose_one_way_audio (explicit; depth ambiguous in v0.2/v1 wording)

## Cross-cut contracts
- MCP initialize + tool discovery via stdio (explicit)
- Structured response envelope fields (`ok`, `timestamp`, `duration_ms`, `artifacts`, `warnings`) (explicit)
- Structured failure fields (`error_code`, `failure_category`, `retryable`, `likely_causes`, `next_recommended_tools`) (explicit)
- Browser lifecycle scenarios including crash recovery, stale selector recovery (inferred by pipeline; partially ambiguous in repo tests)
- Telecom scenario families (registration/incoming/answer/diagnostics) (explicit in validation pipeline)
