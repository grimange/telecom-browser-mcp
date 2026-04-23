from __future__ import annotations

import pytest

from telecom_browser_mcp.adapters.apntalk import APNTalkAdapter
from telecom_browser_mcp.adapters.apntalk_contract import (
    APNTALK_RUNTIME_BRIDGE_VERSION,
    APNTALK_SURFACE_CONTRACTS,
    apntalk_contract_drift_report,
    validate_apntalk_runtime_bridge,
)
from telecom_browser_mcp.models.session import TelecomStatus


def _valid_bridge_payload(**overrides):
    payload = {
        "version": APNTALK_RUNTIME_BRIDGE_VERSION,
        "readOnly": True,
        "mode": "observation-only",
        "sessionAuth": {
            "availability": "available",
            "isAuthenticated": True,
            "hasUser": True,
            "hasSelectedCampaign": True,
            "hasCampaigns": True,
        },
        "agent": {
            "availability": "available",
            "lifecycleStatus": "READY",
            "sessionInitialized": True,
            "hasUserId": True,
            "hasSessionId": True,
            "hasExtension": True,
        },
        "registration": {
            "availability": "available",
            "isRegistered": True,
            "callStatus": "ringing",
            "hasRegisterer": True,
            "hasSession": True,
            "hasCallerInfo": True,
        },
        "call": {
            "availability": "available",
            "hasActiveCall": True,
            "callStatus": "RINGING",
            "direction": "inbound",
            "isMuted": False,
            "isOnHold": False,
            "durationSeconds": None,
            "hasBridgeId": False,
        },
        "readiness": {
            "availability": "available",
            "isAuthenticated": True,
            "sessionInitialized": True,
            "lifecycleStatus": "READY",
            "isRegistered": True,
            "requestedAvailability": "READY",
            "effectiveAvailability": "AVAILABLE",
        },
        "incomingCall": {
            "availability": "available",
            "isIncomingPresent": True,
            "ringingState": "ringing",
            "direction": "incoming",
            "ambiguity": "none",
        },
        "webRTC": {
            "availability": "partial",
            "hasRemoteAudioElement": True,
            "remoteAudioAttached": False,
            "hasRingtoneElement": False,
        },
        "peerConnection": {
            "availability": "available",
            "hasPeerConnection": True,
            "ambiguity": "none",
            "signalingState": "stable",
            "iceConnectionState": "connected",
            "connectionState": "connected",
            "hasLocalDescription": True,
            "hasRemoteDescription": True,
            "senderCount": 1,
            "receiverCount": 1,
            "transceiverCount": 1,
        },
        "controls": {
            "answer": {
                "availability": "available",
                "visible": True,
                "enabled": True,
                "actionAllowed": True,
                "ambiguity": "none",
                "controlKind": "answer",
                "controlScope": "incoming-call",
                "stableControlId": "softphone-main-answer",
                "selectorContract": '[data-apntalk-bridge-control-id="softphone-main-answer"]',
            },
            "hangup": {
                "availability": "available",
                "visible": True,
                "enabled": True,
                "actionAllowed": True,
                "ambiguity": "none",
                "controlKind": "hangup",
                "controlScope": "main-call",
                "stableControlId": "softphone-main-hangup",
                "selectorContract": '[data-apntalk-bridge-control-id="softphone-main-hangup"]',
            }
        },
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(payload.get(key), dict):
            payload[key] = {**payload[key], **value}
        else:
            payload[key] = value
    return payload


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


class _FakeLocatorCollection:
    def __init__(self, locators: list[_FakeLocator]) -> None:
        self._locators = locators

    @property
    def first(self) -> _FakeLocator:
        return self._locators[0] if self._locators else _MissingLocator()

    async def count(self) -> int:
        return len(self._locators)

    def nth(self, index: int) -> _FakeLocator:
        return self._locators[index]


class _MissingLocator(_FakeLocator):
    async def count(self) -> int:
        return 0


class _TransitioningBridgeLocator(_FakeLocator):
    def __init__(self, page: "_FakePage", bridge_payload_attr: str, *, visible: bool = True) -> None:
        super().__init__(visible=visible)
        self._page = page
        self._bridge_payload_attr = bridge_payload_attr

    async def click(self, timeout: int) -> None:
        await super().click(timeout=timeout)
        self._page.bridge_payload = getattr(self._page, self._bridge_payload_attr)


class _FakePage:
    def __init__(
        self,
        *,
        success: bool = True,
        error_text: str | None = None,
        missing: set[str] | None = None,
        bridge_payload: object | None = None,
        answer_bridge_payload: object | None = None,
        hangup_bridge_payload: object | None = None,
        control_selectors: dict[str, list[_FakeLocator]] | None = None,
    ) -> None:
        self.success = success
        self.error_text = error_text
        self._missing = missing or set()
        self.bridge_payload = bridge_payload
        self.answer_bridge_payload = answer_bridge_payload if answer_bridge_payload is not None else bridge_payload
        self.hangup_bridge_payload = hangup_bridge_payload if hangup_bridge_payload is not None else bridge_payload
        self.email_locator = _FakeLocator()
        self.password_locator = _FakeLocator()
        self.submit_locator = _FakeLocator()
        self._control_selectors = control_selectors or {}

    def locator(self, selector: str):
        if selector in self._missing:
            return _MissingLocator()
        if selector == "input[type='email']":
            return self.email_locator
        if selector == "input[type='password']":
            return self.password_locator
        if selector == "button[type='submit']":
            return self.submit_locator
        if selector in self._control_selectors:
            return _FakeLocatorCollection(self._control_selectors[selector])
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
        if "const bridge = window.__apnTalkTestBridge" in script:
            return self.bridge_payload
        if "navigator.permissions?.query" in script:
            return {"available": True, "state": "prompt"}
        if "const groups =" in script:
            return {
                "email_input": {
                    "status": "selector_present",
                    "matched_selector": "input[type='email']",
                },
                "password_input": {
                    "status": "selector_present",
                    "matched_selector": "input[type='password']",
                },
                "submit_button": {
                    "status": "selector_present",
                    "matched_selector": "button[type='submit']",
                },
            }
        return {
            "success": self.success,
            "url": "https://s022-067.apntelecom.com/dashboard",
            "title": "Agent Dashboard",
            "away_from_login": self.success,
            "auth_text": self.success,
            "has_password_field": not self.success,
        }


@pytest.mark.asyncio
async def test_apntalk_wait_for_ready_succeeds_with_precise_bridge_facts() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()

    result = await adapter.wait_for_ready(
        status,
        page=_FakePage(bridge_payload=_valid_bridge_payload()),
        timeout_ms=100,
    )

    assert result.ok is True
    assert result.details["ui_ready"] is True
    assert status.ui_ready is True


@pytest.mark.asyncio
async def test_apntalk_wait_for_registration_succeeds_with_precise_bridge_facts() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()

    result = await adapter.wait_for_registration(
        status,
        page=_FakePage(bridge_payload=_valid_bridge_payload()),
        timeout_ms=100,
    )

    assert result.ok is True
    assert result.details["registration_state"] == "registered"
    assert status.registration_state == "registered"


@pytest.mark.asyncio
async def test_apntalk_wait_for_registration_fails_closed_when_bridge_reports_unregistered() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()

    result = await adapter.wait_for_registration(
        status,
        page=_FakePage(
            bridge_payload=_valid_bridge_payload(
                registration={
                    "availability": "available",
                    "isRegistered": False,
                }
            )
        ),
        timeout_ms=100,
    )

    assert result.ok is False
    assert result.error_code == "registration_not_registered"
    assert result.classification == "registration_missing"
    assert status.registration_state == "unknown"


@pytest.mark.asyncio
async def test_apntalk_wait_for_ready_fails_closed_when_readiness_facts_are_partial() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()

    result = await adapter.wait_for_ready(
        status,
        page=_FakePage(
            bridge_payload=_valid_bridge_payload(
                readiness={
                    "availability": "partial",
                    "lifecycleStatus": "unknown",
                    "requestedAvailability": "unknown",
                }
            )
        ),
        timeout_ms=100,
    )

    assert result.ok is False
    assert result.error_code == "ready_state_not_satisfied"
    assert result.classification == "session_not_ready"
    assert status.ui_ready is False


@pytest.mark.asyncio
async def test_apntalk_wait_for_incoming_call_succeeds_with_safe_bridge_facts() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()

    result = await adapter.wait_for_incoming_call(
        status,
        page=_FakePage(bridge_payload=_valid_bridge_payload()),
        timeout_ms=100,
    )

    assert result.ok is True
    assert result.details["incoming_call_state"] == "ringing"
    assert status.incoming_call_state == "ringing"


@pytest.mark.asyncio
async def test_apntalk_wait_for_incoming_call_fails_closed_when_bridge_marks_ambiguity() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()

    result = await adapter.wait_for_incoming_call(
        status,
        page=_FakePage(
            bridge_payload=_valid_bridge_payload(
                incomingCall={
                    "availability": "partial",
                    "isIncomingPresent": False,
                    "ringingState": "ringing",
                    "direction": "inbound",
                    "ambiguity": "ringing_without_inbound_direction",
                }
            )
        ),
        timeout_ms=100,
    )

    assert result.ok is False
    assert result.error_code == "incoming_call_ambiguous"
    assert result.classification == "incoming_call_not_present"
    assert status.incoming_call_state == "unknown"


@pytest.mark.asyncio
async def test_apntalk_answer_call_succeeds_with_visible_main_control_and_connected_transition() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus(incoming_call_state="ringing")
    connected_payload = _valid_bridge_payload(
        call={
            "availability": "available",
            "hasActiveCall": True,
            "callStatus": "TALKING",
            "direction": "incoming",
            "hasBridgeId": True,
        },
        incomingCall={
            "availability": "available",
            "isIncomingPresent": False,
            "ringingState": "idle",
            "direction": "unknown",
            "ambiguity": "none",
        },
        controls={
            "answer": {
                "availability": "unavailable",
                "visible": False,
                "enabled": False,
                "actionAllowed": False,
                "ambiguity": "none",
                "controlKind": "answer",
                "controlScope": "incoming-call",
                "stableControlId": "softphone-main-answer",
                "selectorContract": '[data-apntalk-bridge-control-id="softphone-main-answer"]',
            },
            "hangup": _valid_bridge_payload()["controls"]["hangup"],
        },
    )
    page = _FakePage(bridge_payload=_valid_bridge_payload(), answer_bridge_payload=connected_payload)
    selector = '[data-apntalk-bridge-control-id="softphone-main-answer"]'
    page._control_selectors[selector] = [_TransitioningBridgeLocator(page, "answer_bridge_payload")]

    result = await adapter.answer_call(status, page=page, timeout_ms=100)

    assert result.ok is True
    assert result.details["active_call_state"] == "connected"
    assert result.details["incoming_call_state"] == "idle"
    assert result.details["connected_facts"]["callStatus"] == "TALKING"
    assert status.active_call_state == "connected"
    assert status.incoming_call_state == "idle"


@pytest.mark.asyncio
async def test_apntalk_answer_call_fails_closed_when_control_is_ambiguous() -> None:
    adapter = APNTalkAdapter()

    result = await adapter.answer_call(
        TelecomStatus(incoming_call_state="ringing"),
        page=_FakePage(
            bridge_payload=_valid_bridge_payload(
                controls={
                    "answer": {
                        "availability": "partial",
                        "visible": True,
                        "enabled": True,
                        "actionAllowed": True,
                        "ambiguity": "multiple_answer_contexts",
                        "controlKind": "answer",
                        "controlScope": "incoming-call",
                        "stableControlId": "softphone-main-answer",
                        "selectorContract": '[data-apntalk-bridge-control-id="softphone-main-answer"]',
                    },
                    "hangup": _valid_bridge_payload()["controls"]["hangup"],
                }
            )
        ),
        timeout_ms=100,
    )

    assert result.ok is False
    assert result.error_code == "answer_control_ambiguous"
    assert result.classification == "adapter_contract_failure"


@pytest.mark.asyncio
async def test_apntalk_answer_call_fails_closed_when_action_is_disallowed() -> None:
    adapter = APNTalkAdapter()

    result = await adapter.answer_call(
        TelecomStatus(incoming_call_state="ringing"),
        page=_FakePage(
            bridge_payload=_valid_bridge_payload(
                controls={
                    "answer": {
                        "availability": "available",
                        "visible": True,
                        "enabled": True,
                        "actionAllowed": False,
                        "ambiguity": "none",
                        "controlKind": "answer",
                        "controlScope": "incoming-call",
                        "stableControlId": "softphone-main-answer",
                        "selectorContract": '[data-apntalk-bridge-control-id="softphone-main-answer"]',
                    },
                    "hangup": _valid_bridge_payload()["controls"]["hangup"],
                }
            )
        ),
        timeout_ms=100,
    )

    assert result.ok is False
    assert result.error_code == "answer_action_disallowed"
    assert result.classification == "adapter_contract_failure"


@pytest.mark.asyncio
async def test_apntalk_answer_call_fails_closed_when_selector_contract_matches_multiple_controls() -> None:
    adapter = APNTalkAdapter()
    page = _FakePage(bridge_payload=_valid_bridge_payload())
    selector = '[data-apntalk-bridge-control-id="softphone-main-answer"]'
    page._control_selectors[selector] = [_FakeLocator(), _FakeLocator()]

    result = await adapter.answer_call(
        TelecomStatus(incoming_call_state="ringing"),
        page=page,
        timeout_ms=100,
    )

    assert result.ok is False
    assert result.error_code == "multiple_selector_matches"
    assert result.classification == "ui_drift"


@pytest.mark.asyncio
async def test_apntalk_answer_call_fails_closed_when_connected_transition_is_not_observed() -> None:
    adapter = APNTalkAdapter()
    page = _FakePage(bridge_payload=_valid_bridge_payload())
    selector = '[data-apntalk-bridge-control-id="softphone-main-answer"]'
    page._control_selectors[selector] = [_FakeLocator()]

    result = await adapter.answer_call(
        TelecomStatus(incoming_call_state="ringing"),
        page=page,
        timeout_ms=100,
    )

    assert result.ok is False
    assert result.error_code == "answer_connected_transition_missing"
    assert result.classification == "call_delivery_failure"


@pytest.mark.asyncio
async def test_apntalk_peer_connection_summary_uses_precise_bridge_facts() -> None:
    adapter = APNTalkAdapter()

    summary = await adapter.peer_connection_summary(
        TelecomStatus(),
        page=_FakePage(bridge_payload=_valid_bridge_payload()),
    )

    assert summary["available"] is True
    assert summary["facts"]["hasPeerConnection"] is True
    assert summary["facts"]["signalingState"] == "stable"
    assert summary["facts"]["senderCount"] == 1


@pytest.mark.asyncio
async def test_apntalk_peer_connection_summary_fails_closed_when_bridge_marks_ambiguity() -> None:
    adapter = APNTalkAdapter()

    summary = await adapter.peer_connection_summary(
        TelecomStatus(),
        page=_FakePage(
            bridge_payload=_valid_bridge_payload(
                peerConnection={
                    "availability": "partial",
                    "hasPeerConnection": True,
                    "ambiguity": "peer_connection_counts_unavailable",
                    "senderCount": None,
                    "receiverCount": None,
                    "transceiverCount": None,
                }
            )
        ),
    )

    assert summary["available"] is False
    assert summary["reason_code"] == "peer_connection_ambiguous"


@pytest.mark.asyncio
async def test_apntalk_hangup_call_succeeds_with_visible_main_control_and_terminal_transition() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus(active_call_state="active", incoming_call_state="ringing")
    terminal_payload = _valid_bridge_payload(
        call={
            "availability": "available",
            "hasActiveCall": False,
            "callStatus": "DISCONNECTED",
            "direction": "unknown",
        },
        incomingCall={
            "availability": "available",
            "isIncomingPresent": False,
            "ringingState": "idle",
            "direction": "unknown",
            "ambiguity": "none",
        },
        peerConnection={
            "availability": "unavailable",
            "hasPeerConnection": False,
            "ambiguity": "no_active_session",
            "signalingState": None,
            "iceConnectionState": None,
            "connectionState": None,
            "hasLocalDescription": False,
            "hasRemoteDescription": False,
            "senderCount": 0,
            "receiverCount": 0,
            "transceiverCount": 0,
        },
        controls={
            "hangup": {
                "availability": "unavailable",
                "visible": False,
                "enabled": False,
                "actionAllowed": False,
                "ambiguity": "none",
                "controlKind": "hangup",
                "controlScope": "main-call",
                "stableControlId": "softphone-main-hangup",
                "selectorContract": '[data-apntalk-bridge-control-id="softphone-main-hangup"]',
            }
        },
    )
    page = _FakePage(
        bridge_payload=_valid_bridge_payload(),
        hangup_bridge_payload=terminal_payload,
    )
    selector = '[data-apntalk-bridge-control-id="softphone-main-hangup"]'
    page._control_selectors[selector] = [_TransitioningBridgeLocator(page, "hangup_bridge_payload")]

    result = await adapter.hangup_call(status, page=page, timeout_ms=100)

    assert result.ok is True
    assert result.details["active_call_state"] == "disconnected"
    assert result.details["incoming_call_state"] == "idle"
    assert result.details["terminal_facts"]["hasActiveCall"] is False
    assert status.active_call_state == "disconnected"
    assert status.incoming_call_state == "idle"


@pytest.mark.asyncio
async def test_apntalk_hangup_call_fails_closed_when_control_is_ambiguous() -> None:
    adapter = APNTalkAdapter()

    result = await adapter.hangup_call(
        TelecomStatus(active_call_state="active"),
        page=_FakePage(
            bridge_payload=_valid_bridge_payload(
                controls={
                    "hangup": {
                        "availability": "partial",
                        "visible": True,
                        "enabled": True,
                        "actionAllowed": True,
                        "ambiguity": "multiple_hangup_contexts",
                        "controlKind": "hangup",
                        "controlScope": "main-call",
                        "stableControlId": "softphone-main-hangup",
                        "selectorContract": '[data-apntalk-bridge-control-id="softphone-main-hangup"]',
                    }
                }
            )
        ),
        timeout_ms=100,
    )

    assert result.ok is False
    assert result.error_code == "hangup_control_ambiguous"
    assert result.classification == "adapter_contract_failure"


@pytest.mark.asyncio
async def test_apntalk_hangup_call_fails_closed_when_action_is_disallowed() -> None:
    adapter = APNTalkAdapter()

    result = await adapter.hangup_call(
        TelecomStatus(active_call_state="active"),
        page=_FakePage(
            bridge_payload=_valid_bridge_payload(
                controls={
                    "hangup": {
                        "availability": "available",
                        "visible": True,
                        "enabled": True,
                        "actionAllowed": False,
                        "ambiguity": "none",
                        "controlKind": "hangup",
                        "controlScope": "main-call",
                        "stableControlId": "softphone-main-hangup",
                        "selectorContract": '[data-apntalk-bridge-control-id="softphone-main-hangup"]',
                    }
                }
            )
        ),
        timeout_ms=100,
    )

    assert result.ok is False
    assert result.error_code == "hangup_action_disallowed"
    assert result.classification == "adapter_contract_failure"


@pytest.mark.asyncio
async def test_apntalk_hangup_call_fails_closed_when_selector_contract_matches_multiple_controls() -> None:
    adapter = APNTalkAdapter()
    page = _FakePage(bridge_payload=_valid_bridge_payload())
    selector = '[data-apntalk-bridge-control-id="softphone-main-hangup"]'
    page._control_selectors[selector] = [_FakeLocator(), _FakeLocator()]

    result = await adapter.hangup_call(
        TelecomStatus(active_call_state="active"),
        page=page,
        timeout_ms=100,
    )

    assert result.ok is False
    assert result.error_code == "multiple_selector_matches"
    assert result.classification == "ui_drift"


@pytest.mark.asyncio
async def test_apntalk_hangup_call_fails_closed_when_terminal_transition_is_not_observed() -> None:
    adapter = APNTalkAdapter()
    page = _FakePage(bridge_payload=_valid_bridge_payload())
    selector = '[data-apntalk-bridge-control-id="softphone-main-hangup"]'
    page._control_selectors[selector] = [_FakeLocator()]

    result = await adapter.hangup_call(
        TelecomStatus(active_call_state="active"),
        page=page,
        timeout_ms=100,
    )

    assert result.ok is False
    assert result.error_code == "hangup_terminal_transition_missing"
    assert result.classification == "call_delivery_failure"


@pytest.mark.asyncio
async def test_apntalk_wait_for_ready_fails_closed_on_bridge_version_mismatch() -> None:
    adapter = APNTalkAdapter()
    result = await adapter.wait_for_ready(
        TelecomStatus(),
        page=_FakePage(bridge_payload=_valid_bridge_payload(version="2.0.0")),
        timeout_ms=100,
    )
    assert result.ok is False
    assert result.error_code == "bridge_version_mismatch"


@pytest.mark.asyncio
async def test_apntalk_wait_for_registration_fails_closed_on_bridge_version_mismatch() -> None:
    adapter = APNTalkAdapter()
    result = await adapter.wait_for_registration(
        TelecomStatus(),
        page=_FakePage(bridge_payload=_valid_bridge_payload(version="2.0.0")),
        timeout_ms=100,
    )
    assert result.ok is False
    assert result.error_code == "bridge_version_mismatch"


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
    assert "Invalid username or password" in result.message
    assert status.login_complete is False


def test_apntalk_contract_drift_report_tracks_unimplemented_surfaces() -> None:
    report = apntalk_contract_drift_report()
    assert set(report) == set(APNTALK_SURFACE_CONTRACTS) - {
        "login_agent",
        "wait_for_ready",
        "wait_for_registration",
        "wait_for_incoming_call",
        "answer_call",
        "hangup_call",
        "get_registration_status",
        "get_peer_connection_summary",
    }


def test_apntalk_capability_truth_matches_supported_bridge_observation_scope() -> None:
    adapter = APNTalkAdapter()
    truths = {item["capability"]: item for item in adapter.capability_truth()}

    assert truths["apntalk_runtime_bridge_contract"]["declared_support"] == "supported_with_runtime_probe"
    assert truths["wait_for_ready"]["declared_support"] == "supported_with_runtime_probe"
    assert truths["wait_for_incoming_call"]["declared_support"] == "supported_with_runtime_probe"
    assert truths["wait_for_registration"]["declared_support"] == "supported_with_runtime_probe"
    assert truths["answer_call"]["declared_support"] == "supported_with_selector_binding"
    assert truths["answer_call"]["binding_status"] == "selector_bound"
    assert truths["hangup_call"]["declared_support"] == "supported_with_selector_binding"
    assert truths["hangup_call"]["binding_status"] == "selector_bound"
    assert truths["get_peer_connection_summary"]["declared_support"] == "supported_with_runtime_probe"


@pytest.mark.parametrize(
    ("payload", "expected_verdict"),
    [
        (None, "bridge_absent"),
        ("bad", "bridge_malformed"),
        (
            {
                "version": APNTALK_RUNTIME_BRIDGE_VERSION,
                "readOnly": True,
                "mode": "observation-only",
                "sessionAuth": {"availability": "available"},
                "agent": {"availability": "available"},
                "registration": {"availability": "available"},
                "call": {"availability": "available"},
                "readiness": {"availability": "available"},
                "incomingCall": {"availability": "available"},
                "webRTC": {"availability": "available"},
            },
            "bridge_partial",
        ),
        (
            {
                **_valid_bridge_payload(),
                "version": "2.0.0",
            },
            "bridge_version_mismatch",
        ),
        (_valid_bridge_payload(), "bridge_valid"),
    ],
)
def test_validate_apntalk_runtime_bridge_classifies_expected_verdicts(
    payload: object,
    expected_verdict: str,
) -> None:
    assert validate_apntalk_runtime_bridge(payload).verdict == expected_verdict


@pytest.mark.asyncio
async def test_apntalk_snapshot_surfaces_fail_closed() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()

    registration = await adapter.registration_snapshot(status, page=_FakePage(bridge_payload=None))
    store = await adapter.store_snapshot(status, page=object())

    assert registration["available"] is False
    assert registration["reason_code"] == "bridge_absent"
    assert store["available"] is False
    assert store["reason_code"] == "runtime_probe_unavailable"


@pytest.mark.asyncio
async def test_apntalk_registration_snapshot_uses_valid_bridge_state() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()

    snapshot = await adapter.registration_snapshot(
        status,
        page=_FakePage(bridge_payload=_valid_bridge_payload()),
    )

    assert snapshot["available"] is True
    assert snapshot["registration_state"] == "registered"
    assert snapshot["missing_requirements"] == []
    assert status.registration_state == "registered"


@pytest.mark.asyncio
async def test_apntalk_phase0_observation_reports_bridge_and_detected_observation_states() -> None:
    adapter = APNTalkAdapter()
    observation = await adapter.phase0_observation(
        TelecomStatus(),
        page=_FakePage(bridge_payload=_valid_bridge_payload()),
    )

    assert observation["runtime_bridge"]["validation_verdict"] == "bridge_valid"
    assert observation["ready_observation"]["available"] is True
    assert observation["registration_wait_observation"]["available"] is True
    assert observation["registration_observation"]["available"] is True
    assert observation["incoming_call_observation"]["available"] is True
    assert observation["answer_control_observation"]["available"] is True
    assert observation["peer_connection_observation"]["available"] is True
    assert observation["hangup_control_observation"]["available"] is True
    truths = {item["capability"]: item for item in observation["capability_truth"]}
    assert truths["wait_for_ready"]["live_detection_status"] == "detected"
    assert truths["wait_for_registration"]["live_detection_status"] == "detected"
    assert truths["wait_for_incoming_call"]["live_detection_status"] == "detected"
    assert truths["wait_for_registration"]["declared_support"] == "supported_with_runtime_probe"
    assert truths["answer_call"]["live_detection_status"] == "detected"
    assert truths["get_peer_connection_summary"]["live_detection_status"] == "detected"
    assert truths["hangup_call"]["live_detection_status"] == "detected"


@pytest.mark.asyncio
async def test_apntalk_phase0_observation_surfaces_ambiguous_incoming_as_fail_closed() -> None:
    adapter = APNTalkAdapter()
    observation = await adapter.phase0_observation(
        TelecomStatus(),
        page=_FakePage(
            bridge_payload=_valid_bridge_payload(
                incomingCall={
                    "availability": "partial",
                    "isIncomingPresent": False,
                    "ringingState": "ringing",
                    "direction": "inbound",
                    "ambiguity": "ringing_without_inbound_direction",
                }
            )
        ),
    )

    assert observation["incoming_call_observation"]["available"] is False
    assert observation["incoming_call_observation"]["reason_code"] == "incoming_call_ambiguous"
    truths = {item["capability"]: item for item in observation["capability_truth"]}
    assert truths["wait_for_incoming_call"]["live_detection_status"] == "bridge_present"


@pytest.mark.asyncio
async def test_apntalk_phase0_observation_surfaces_hangup_control_refusal_when_action_is_disallowed() -> None:
    adapter = APNTalkAdapter()
    observation = await adapter.phase0_observation(
        TelecomStatus(),
        page=_FakePage(
            bridge_payload=_valid_bridge_payload(
                controls={
                    "hangup": {
                        "availability": "available",
                        "visible": True,
                        "enabled": True,
                        "actionAllowed": False,
                        "ambiguity": "none",
                        "controlKind": "hangup",
                        "controlScope": "main-call",
                        "stableControlId": "softphone-main-hangup",
                        "selectorContract": '[data-apntalk-bridge-control-id="softphone-main-hangup"]',
                    }
                }
            )
        ),
    )

    assert observation["hangup_control_observation"]["available"] is False
    assert observation["hangup_control_observation"]["reason_code"] == "hangup_action_disallowed"
    truths = {item["capability"]: item for item in observation["capability_truth"]}
    assert truths["hangup_call"]["live_detection_status"] == "bridge_present"


@pytest.mark.asyncio
async def test_apntalk_phase0_observation_surfaces_answer_control_refusal_when_action_is_disallowed() -> None:
    adapter = APNTalkAdapter()
    observation = await adapter.phase0_observation(
        TelecomStatus(),
        page=_FakePage(
            bridge_payload=_valid_bridge_payload(
                controls={
                    "answer": {
                        "availability": "available",
                        "visible": True,
                        "enabled": True,
                        "actionAllowed": False,
                        "ambiguity": "none",
                        "controlKind": "answer",
                        "controlScope": "incoming-call",
                        "stableControlId": "softphone-main-answer",
                        "selectorContract": '[data-apntalk-bridge-control-id="softphone-main-answer"]',
                    },
                    "hangup": _valid_bridge_payload()["controls"]["hangup"],
                }
            )
        ),
    )

    assert observation["answer_control_observation"]["available"] is False
    assert observation["answer_control_observation"]["reason_code"] == "answer_action_disallowed"
    truths = {item["capability"]: item for item in observation["capability_truth"]}
    assert truths["answer_call"]["live_detection_status"] == "bridge_present"
