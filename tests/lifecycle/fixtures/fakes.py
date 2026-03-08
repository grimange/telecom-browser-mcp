from __future__ import annotations

from dataclasses import dataclass, field

from telecom_browser_mcp.sessions.fault_injection import LifecycleFaultError, LifecycleFaultInjector


@dataclass
class FakeSelectorHandle:
    selector: str
    dom_epoch: int


@dataclass
class FakePage:
    page_closed: bool = False
    dom_epoch: int = 1

    def resolve_selector(self, selector: str) -> FakeSelectorHandle:
        if self.page_closed:
            raise RuntimeError("page detached before selector lookup")
        return FakeSelectorHandle(selector=selector, dom_epoch=self.dom_epoch)

    def click(self, handle: FakeSelectorHandle) -> None:
        if self.page_closed:
            raise RuntimeError("page detached before click")
        if handle.dom_epoch != self.dom_epoch:
            raise RuntimeError("stale selector handle")


@dataclass
class FakeContext:
    context_closed: bool = False
    page: FakePage = field(default_factory=FakePage)

    def wait_for_selector(self, selector: str) -> FakeSelectorHandle:
        if self.context_closed:
            raise RuntimeError("context closed while waiting for selector")
        return self.page.resolve_selector(selector)


@dataclass
class FakeDriver:
    browser_closed: bool = False
    context: FakeContext = field(default_factory=FakeContext)


@dataclass
class FakeSessionRegistry:
    sessions: dict[str, FakeDriver] = field(default_factory=dict)

    def add(self, session_id: str, driver: FakeDriver) -> None:
        self.sessions[session_id] = driver

    def get(self, session_id: str) -> FakeDriver | None:
        return self.sessions.get(session_id)

    def invalidate(self, session_id: str) -> bool:
        return self.sessions.pop(session_id, None) is not None


def recover_session_reuse(
    registry: FakeSessionRegistry,
    session_id: str,
    injector: LifecycleFaultInjector,
) -> dict:
    driver = registry.get(session_id)
    if driver is None:
        return {
            "ok": False,
            "failure_category": "session",
            "error_code": "SESSION_NOT_FOUND",
            "retryable": False,
            "cleanup": {"session_removed": False},
        }

    injector.emit("before_session_reuse", driver)
    if driver.browser_closed:
        removed = registry.invalidate(session_id)
        return {
            "ok": False,
            "failure_category": "session",
            "error_code": "BROWSER_SESSION_BROKEN",
            "retryable": True,
            "cleanup": {"session_removed": removed},
        }
    return {"ok": True}


def wait_for_ready_with_recovery(driver: FakeDriver, injector: LifecycleFaultInjector) -> dict:
    injector.emit("after_context_created", driver.context)
    try:
        driver.context.wait_for_selector("#dialer-ready")
    except RuntimeError as exc:
        return {
            "ok": False,
            "failure_category": "session",
            "error_code": "BROWSER_SESSION_BROKEN",
            "retryable": True,
            "cleanup": {"context_closed": driver.context.context_closed},
            "reason": str(exc),
        }
    return {"ok": True}


def click_answer_button(driver: FakeDriver, injector: LifecycleFaultInjector) -> dict:
    page = driver.context.page
    handle = page.resolve_selector("#answer")
    injector.emit("before_click", page)
    try:
        page.click(handle)
    except RuntimeError as exc:
        # Bounded recovery: reacquire page/selector once, then retry click.
        if "page detached before click" not in str(exc):
            return {
                "ok": False,
                "failure_category": "session",
                "error_code": "UI_SELECTOR_FAILURE",
                "retryable": True,
                "recovery_attempted": True,
                "reason": str(exc),
            }
        page.page_closed = False
        retry_handle = page.resolve_selector("#answer")
        page.click(retry_handle)
        return {"ok": True, "recovery_attempted": True, "recovery_strategy": "reacquire_page_and_retry"}
    return {"ok": True, "recovery_attempted": False}


def stale_selector_attempt(driver: FakeDriver, injector: LifecycleFaultInjector) -> dict:
    page = driver.context.page
    handle = page.resolve_selector("#answer")
    injector.emit("after_selector_resolved", page)
    try:
        page.click(handle)
    except RuntimeError as exc:
        if "stale selector handle" not in str(exc):
            return {
                "ok": False,
                "failure_category": "session",
                "error_code": "UI_SELECTOR_FAILURE",
                "retryable": True,
                "reason": str(exc),
                "observed": {"selector_stale": False},
            }
        retry_handle = page.resolve_selector("#answer")
        page.click(retry_handle)
        return {
            "ok": True,
            "recovery_attempted": True,
            "recovery_strategy": "refresh_selector_handle_and_retry",
            "observed": {"selector_stale": True},
        }
    return {"ok": True, "recovery_attempted": False}


def isolated_parallel_step(
    registry: FakeSessionRegistry,
    session_id: str,
    injector: LifecycleFaultInjector,
) -> dict:
    driver = registry.get(session_id)
    if driver is None:
        return {"ok": False, "error_code": "SESSION_NOT_FOUND"}

    try:
        injector.emit("before_wait_for_selector", driver.context)
        driver.context.wait_for_selector("#call-state")
    except (RuntimeError, LifecycleFaultError):
        registry.invalidate(session_id)
        return {
            "ok": False,
            "failure_category": "session",
            "error_code": "BROWSER_SESSION_BROKEN",
            "cleanup": {"session_removed": True},
        }
    return {"ok": True}
