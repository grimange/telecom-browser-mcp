from __future__ import annotations

import pytest

from telecom_browser_mcp.adapters.apntalk import APNTalkAdapter
from telecom_browser_mcp.adapters.apntalk_contract import (
    APNTALK_SURFACE_CONTRACTS,
    apntalk_contract_drift_report,
)
from telecom_browser_mcp.models.session import TelecomStatus


class _FakeLocator:
    def __init__(self, *, visible: bool = True) -> None:
        self._visible = visible
        self.filled: list[str] = []
        self.clicked = False

    @property
    def first(self) -> "_FakeLocator":
        return self

    async def count(self) -> int:
        return 1

    async def is_visible(self) -> bool:
        return self._visible

    async def fill(self, value: str, timeout: int) -> None:
        _ = timeout
        self.filled.append(value)

    async def click(self, timeout: int) -> None:
        _ = timeout
        self.clicked = True


class _MissingLocator(_FakeLocator):
    async def count(self) -> int:
        return 0


class _FakePage:
    def __init__(
        self,
        *,
        success: bool = True,
        error_text: str | None = None,
        missing: set[str] | None = None,
    ) -> None:
        self.success = success
        self.error_text = error_text
        self._missing = missing or set()
        self.email_locator = _FakeLocator()
        self.password_locator = _FakeLocator()
        self.submit_locator = _FakeLocator()

    def locator(self, selector: str):
        if selector in self._missing:
            return _MissingLocator()
        if selector == "input[type='email']":
            return self.email_locator
        if selector == "input[type='password']":
            return self.password_locator
        if selector == "button[type='submit']":
            return self.submit_locator
        return _MissingLocator()

    async def wait_for_load_state(self, state: str, timeout: int) -> None:
        _ = (state, timeout)

    async def wait_for_function(self, script: str, timeout: int) -> None:
        _ = (script, timeout)
        if not self.success:
            raise RuntimeError("not authenticated")

    async def evaluate(self, script: str):
        if "querySelectorAll" in script:
            return self.error_text
        return {
            "success": self.success,
            "url": "https://s022-067.apntelecom.com/dashboard",
            "title": "Agent Dashboard",
            "away_from_login": self.success,
            "auth_text": self.success,
            "has_password_field": not self.success,
        }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method_name", "expected_code", "expected_classification"),
    [
        ("wait_for_ready", "selector_contract_missing", "ui_drift"),
        ("wait_for_registration", "runtime_probe_unavailable", "adapter_contract_failure"),
        ("wait_for_incoming_call", "runtime_probe_unavailable", "adapter_contract_failure"),
        ("answer_call", "adapter_contract_unimplemented", "adapter_contract_failure"),
        ("hangup_call", "adapter_contract_unimplemented", "adapter_contract_failure"),
    ],
)
async def test_apntalk_operations_fail_closed(
    method_name: str,
    expected_code: str,
    expected_classification: str,
) -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()

    result = await getattr(adapter, method_name)(status, page=object(), timeout_ms=100)

    assert result.ok is False
    assert result.error_code == expected_code
    assert result.classification == expected_classification
    assert result.details["missing_requirements"]


@pytest.mark.asyncio
async def test_apntalk_wait_for_ready_does_not_inherit_scaffold_success() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()

    result = await adapter.wait_for_ready(status, page=object(), timeout_ms=100)

    assert result.ok is False
    assert result.error_code == "selector_contract_missing"
    assert status.ui_ready is False
    assert result.details["missing_requirements"] == ["selector:agent_ready_indicator"]


@pytest.mark.asyncio
async def test_apntalk_login_uses_visible_ui_and_sets_login_state() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()
    page = _FakePage(success=True)

    result = await adapter.login(
        status,
        page=page,
        credentials={"email": "agent@example.test", "password": "secret"},
        timeout_ms=100,
    )

    assert result.ok is True
    assert status.login_complete is True
    assert result.details["login_complete"] is True
    assert result.details["landing_title"] == "Agent Dashboard"
    assert page.email_locator.filled == ["agent@example.test"]
    assert page.password_locator.filled == ["secret"]
    assert page.submit_locator.clicked is True


@pytest.mark.asyncio
async def test_apntalk_login_fails_closed_when_login_controls_are_missing() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()
    page = _FakePage(missing={"input[type='email']"})

    result = await adapter.login(
        status,
        page=page,
        credentials={"email": "agent@example.test", "password": "secret"},
        timeout_ms=100,
    )

    assert result.ok is False
    assert result.error_code == "selector_contract_missing"
    assert result.classification == "ui_drift"
    assert result.details["missing_selectors"] == ["email_input"]
    assert status.login_complete is False


@pytest.mark.asyncio
async def test_apntalk_login_fails_closed_when_post_login_page_is_not_confirmed() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()
    page = _FakePage(success=False, error_text="Invalid username or password")

    result = await adapter.login(
        status,
        page=page,
        credentials={"email": "agent@example.test", "password": "bad-secret"},
        timeout_ms=100,
    )

    assert result.ok is False
    assert result.error_code == "state_divergence"
    assert result.classification == "state_divergence"
    assert "Invalid username or password" in result.message
    assert status.login_complete is False


def test_apntalk_contract_drift_report_tracks_unimplemented_surfaces() -> None:
    report = apntalk_contract_drift_report()

    assert set(report) == set(APNTALK_SURFACE_CONTRACTS) - {"login_agent"}
    assert report["wait_for_registration"] == [
        "selector:registration_badge",
        "runtime_probe:registration_snapshot",
    ]


@pytest.mark.asyncio
async def test_apntalk_snapshot_surfaces_fail_closed() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()

    registration = await adapter.registration_snapshot(status, page=object())
    store = await adapter.store_snapshot(status, page=object())

    assert registration["available"] is False
    assert registration["reason_code"] == "runtime_probe_unavailable"
    assert store["available"] is False
    assert store["reason_code"] == "runtime_probe_unavailable"
