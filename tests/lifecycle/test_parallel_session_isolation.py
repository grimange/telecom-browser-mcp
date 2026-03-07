from fixtures.fakes import (
    FakeDriver,
    FakeSessionRegistry,
    isolated_parallel_step,
)

from telecom_browser_mcp.sessions.fault_injection import LifecycleFaultInjector


def test_parallel_fault_isolation_keeps_healthy_session_active() -> None:
    registry = FakeSessionRegistry()
    registry.add("sess-failing", FakeDriver())
    registry.add("sess-healthy", FakeDriver())

    failing_injector = LifecycleFaultInjector()
    healthy_injector = LifecycleFaultInjector()
    failing_injector.register("before_wait_for_selector", "close_context")

    failed = isolated_parallel_step(registry, "sess-failing", failing_injector)
    healthy = isolated_parallel_step(registry, "sess-healthy", healthy_injector)

    assert failed["ok"] is False
    assert failed["error_code"] == "BROWSER_SESSION_BROKEN"
    assert failed["cleanup"]["session_removed"] is True
    assert healthy["ok"] is True
    assert registry.get("sess-failing") is None
    assert registry.get("sess-healthy") is not None
