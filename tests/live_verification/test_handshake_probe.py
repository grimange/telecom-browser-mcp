from telecom_browser_mcp.live_verification import classify_mcp_handshake_probe
from telecom_browser_mcp.mcp_handshake_probe import (
    build_initialize_request,
    build_initialized_notification,
    build_tools_list_request,
)


def test_handshake_probe_timeout_no_response_classification() -> None:
    payload = {
        "ok": False,
        "classification": "handshake_timeout",
        "phase": "initialize",
    }
    assert classify_mcp_handshake_probe(payload) == "handshake_timeout"


def test_handshake_probe_success_classification() -> None:
    payload = {"ok": True, "tools_count": 25}
    assert classify_mcp_handshake_probe(payload) == "handshake_passed"


def test_initialize_probe_success_request_shape() -> None:
    request = build_initialize_request(1)
    assert request["method"] == "initialize"
    assert request["params"]["protocolVersion"] == "2024-11-05"
    assert request["params"]["clientInfo"]["name"] == "live-verification"


def test_tools_list_after_initialize_sequence_shape() -> None:
    initialized = build_initialized_notification()
    tools_list = build_tools_list_request(2)
    assert initialized["method"] == "notifications/initialized"
    assert tools_list["method"] == "tools/list"
