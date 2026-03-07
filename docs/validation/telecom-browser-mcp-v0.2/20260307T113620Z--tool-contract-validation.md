# Tool Contract Validation (20260307T113620Z)

## Results

- open_app: PASS ()
- login_agent: PASS ()
- wait_for_ready: PASS ()
- list_sessions: PASS ()
- close_session: PASS ()
- reset_session: PASS ()
- get_registration_status: PASS ()
- wait_for_registration: PASS ()
- assert_registered: PASS ()
- wait_for_incoming_call: PASS ()
- answer_call: PASS ()
- hangup_call: PASS ()
- get_ui_call_state: PASS ()
- get_active_session_snapshot: PASS ()
- get_store_snapshot: PASS ()
- get_peer_connection_summary: PASS ()
- get_webrtc_stats: PASS ()
- get_environment_snapshot: FAIL (Tool missing from exposed tool list)
- diagnose_registration_failure: PASS ()
- diagnose_incoming_call_failure: PASS ()
- diagnose_answer_failure: PASS ()
- diagnose_one_way_audio: FAIL (Tool missing from exposed tool list)
- screenshot: FAIL (Tool missing from exposed tool list)
- collect_browser_logs: FAIL (Tool missing from exposed tool list)
- collect_debug_bundle: PASS ()

## Failure-envelope checks
- missing_session: PASS missing=[]