from fixtures.fakes import FakeDriver, stale_selector_attempt

from telecom_browser_mcp.sessions.fault_injection import LifecycleFaultInjector


def test_dom_replacement_after_selector_resolution_is_normalized() -> None:
    driver = FakeDriver()
    injector = LifecycleFaultInjector()
    injector.register("after_selector_resolved", "stale_selector")

    result = stale_selector_attempt(driver=driver, injector=injector)

    assert result["ok"] is True
    assert result["observed"]["selector_stale"] is True
    assert result["recovery_attempted"] is True
    assert result["recovery_strategy"] == "refresh_selector_handle_and_retry"
