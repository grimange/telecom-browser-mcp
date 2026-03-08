from telecom_browser_mcp.mcp_handshake_probe import classify_startup_state


def test_startup_requires_handshake_success_for_ready_state() -> None:
    assert classify_startup_state(handshake_classification="handshake_passed") == "startup_ready_via_handshake"


def test_startup_timeout_without_handshake_classification() -> None:
    assert classify_startup_state(handshake_classification="handshake_timeout") == "startup_timeout_without_handshake"
