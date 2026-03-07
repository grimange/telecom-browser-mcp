# Contract Inventory (20260307T113620Z)

Canonical contract source: `docs/telecom-browser-mcp-implementation-plan-v0.2.md` (explicit tool catalog + contract rules).

## Tool Contract Inventory

- TOOL::open_app: status_type=explicit implemented=True validation_status=PASS
- TOOL::login_agent: status_type=explicit implemented=True validation_status=PASS
- TOOL::wait_for_ready: status_type=explicit implemented=True validation_status=PASS
- TOOL::list_sessions: status_type=explicit implemented=True validation_status=PASS
- TOOL::close_session: status_type=explicit implemented=True validation_status=PASS
- TOOL::reset_session: status_type=explicit implemented=True validation_status=PASS
- TOOL::get_registration_status: status_type=explicit implemented=True validation_status=PASS
- TOOL::wait_for_registration: status_type=explicit implemented=True validation_status=PASS
- TOOL::assert_registered: status_type=explicit implemented=True validation_status=PASS
- TOOL::wait_for_incoming_call: status_type=explicit implemented=True validation_status=PASS
- TOOL::answer_call: status_type=explicit implemented=True validation_status=PASS
- TOOL::hangup_call: status_type=explicit implemented=True validation_status=PASS
- TOOL::get_ui_call_state: status_type=explicit implemented=True validation_status=PASS
- TOOL::get_active_session_snapshot: status_type=explicit implemented=True validation_status=PASS
- TOOL::get_store_snapshot: status_type=explicit implemented=True validation_status=PASS
- TOOL::get_peer_connection_summary: status_type=explicit implemented=True validation_status=PASS
- TOOL::get_webrtc_stats: status_type=explicit implemented=True validation_status=PASS
- TOOL::get_environment_snapshot: status_type=explicit implemented=False validation_status=FAIL
- TOOL::diagnose_registration_failure: status_type=explicit implemented=True validation_status=PASS
- TOOL::diagnose_incoming_call_failure: status_type=explicit implemented=True validation_status=PASS
- TOOL::diagnose_answer_failure: status_type=explicit implemented=True validation_status=PASS
- TOOL::diagnose_one_way_audio: status_type=explicit implemented=False validation_status=FAIL
- TOOL::screenshot: status_type=explicit implemented=False validation_status=FAIL
- TOOL::collect_browser_logs: status_type=explicit implemented=False validation_status=FAIL
- TOOL::collect_debug_bundle: status_type=explicit implemented=True validation_status=PASS