from telecom_browser_mcp.runtime_environment_detector import detect_runtime_environment


def test_runtime_detector_honors_operator_override(monkeypatch) -> None:
    monkeypatch.setenv("TELECOM_BROWSER_MCP_RUNTIME_CLASS", "sandbox_runtime")
    payload = detect_runtime_environment()
    assert payload["runtime_class"] == "sandbox_runtime"
    assert payload["runtime_reason"] == "operator_override"
