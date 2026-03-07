from fixtures.fakes import FakeDriver, stale_selector_attempt

from telecom_browser_mcp.sessions.fault_injection import LifecycleFaultInjector


def test_dom_replacement_after_selector_resolution_is_normalized() -> None:
    driver = FakeDriver()
    injector = LifecycleFaultInjector()
    injector.register("after_selector_resolved", "stale_selector")

    result = stale_selector_attempt(driver=driver, injector=injector)

    assert result["ok"] is False
    assert result["error_code"] == "UI_SELECTOR_FAILURE"
    assert result["observed"]["selector_stale"] is True
    assert result["retryable"] is True
