from fixtures.fakes import FakeDriver, wait_for_ready_with_recovery

from telecom_browser_mcp.sessions.fault_injection import LifecycleFaultInjector


def test_context_closure_during_wait_returns_bounded_failure() -> None:
    driver = FakeDriver()
    injector = LifecycleFaultInjector()
    injector.register("after_context_created", "close_context")

    result = wait_for_ready_with_recovery(driver=driver, injector=injector)

    assert result["ok"] is False
    assert result["error_code"] == "BROWSER_SESSION_BROKEN"
    assert result["failure_category"] == "session"
    assert result["retryable"] is True
    assert result["cleanup"]["context_closed"] is True
