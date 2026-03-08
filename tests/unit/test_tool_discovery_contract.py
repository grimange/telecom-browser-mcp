from telecom_browser_mcp.server.stdio_server import TOOL_NAMES

EXPECTED_V02_TOOLS = {
    "health",
    "capabilities",
    "open_app",
    "login_agent",
    "wait_for_ready",
    "list_sessions",
    "close_session",
    "reset_session",
    "get_registration_status",
    "wait_for_registration",
    "assert_registered",
    "wait_for_incoming_call",
    "answer_call",
    "hangup_call",
    "get_ui_call_state",
    "get_active_session_snapshot",
    "get_store_snapshot",
    "get_peer_connection_summary",
    "get_webrtc_stats",
    "get_environment_snapshot",
    "diagnose_registration_failure",
    "diagnose_incoming_call_failure",
    "diagnose_answer_failure",
    "diagnose_one_way_audio",
    "screenshot",
    "collect_browser_logs",
    "collect_debug_bundle",
}


def test_v02_tool_catalog_is_exposed() -> None:
    assert set(TOOL_NAMES) == EXPECTED_V02_TOOLS
