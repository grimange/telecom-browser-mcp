from fixtures.fakes import FakeDriver, FakeSessionRegistry, recover_session_reuse

from telecom_browser_mcp.sessions.fault_injection import LifecycleFaultInjector


def test_closed_browser_on_session_reuse_is_invalidated() -> None:
    registry = FakeSessionRegistry()
    registry.add("sess-a", FakeDriver())
    injector = LifecycleFaultInjector()
    injector.register("before_session_reuse", "close_browser")

    result = recover_session_reuse(registry=registry, session_id="sess-a", injector=injector)

    assert result["ok"] is False
    assert result["error_code"] == "BROWSER_SESSION_BROKEN"
    assert result["failure_category"] == "session"
    assert result["cleanup"]["session_removed"] is True
    assert registry.get("sess-a") is None
