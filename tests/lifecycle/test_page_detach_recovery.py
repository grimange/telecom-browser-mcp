from fixtures.fakes import FakeDriver, click_answer_button

from telecom_browser_mcp.sessions.fault_injection import LifecycleFaultInjector


def test_page_detach_before_action_returns_selector_failure() -> None:
    driver = FakeDriver()
    injector = LifecycleFaultInjector()
    injector.register("before_click", "close_page")

    result = click_answer_button(driver=driver, injector=injector)

    assert result["ok"] is True
    assert result["recovery_attempted"] is True
    assert result["recovery_strategy"] == "reacquire_page_and_retry"
