from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from telecom_browser_mcp.adapters.apntalk import APNTalkAdapter
from telecom_browser_mcp.adapters.apntalk_contract import APNTALK_RUNTIME_BRIDGE_VERSION
from telecom_browser_mcp.models.session import SessionModel, TelecomStatus
from telecom_browser_mcp.tools.service import ToolService


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


class _BridgePage:
    def __init__(
        self,
        bridge_payload: object,
        *,
        answer_bridge_payload: object | None = None,
        hangup_bridge_payload: object | None = None,
        selector_matches: dict[str, list["_SelectorMatch"]] | None = None,
    ) -> None:
        self.bridge_payload = bridge_payload
        self.answer_bridge_payload = answer_bridge_payload if answer_bridge_payload is not None else bridge_payload
        self.hangup_bridge_payload = hangup_bridge_payload if hangup_bridge_payload is not None else bridge_payload
        self.selector_matches = selector_matches or {}

    async def evaluate(self, script: str):
        if "const bridge = window.__apnTalkTestBridge" in script:
            return self.bridge_payload
        if "navigator.permissions?.query" in script:
            return {"available": True, "state": "granted"}
        if "const groups =" in script:
            return {}
        return {}

    def locator(self, selector: str):
        return _LocatorCollection(self.selector_matches.get(selector, []))


class _SelectorMatch:
    def __init__(self, *, visible: bool = True, on_click=None) -> None:
        self._visible = visible
        self._on_click = on_click

    async def is_visible(self) -> bool:
        return self._visible

    async def click(self, timeout: int) -> None:
        _ = timeout
        if self._on_click is not None:
            self._on_click()


class _LocatorCollection:
    def __init__(self, matches: list[_SelectorMatch]) -> None:
        self._matches = matches

    async def count(self) -> int:
        return len(self._matches)

    def nth(self, index: int) -> _SelectorMatch:
        return self._matches[index]


def _apntalk_runtime(page: object | None = None) -> SimpleNamespace:
    adapter = APNTalkAdapter()
    return SimpleNamespace(
        model=SessionModel(
            session_id="session-apntalk",
            adapter_id=adapter.adapter_id,
            adapter_name=adapter.adapter_name,
            adapter_version=adapter.adapter_version,
            contract_version=adapter.contract_version,
            scenario_id=adapter.scenario_id,
            capabilities=adapter.capabilities,
            target_url="https://s022-067.apntelecom.com/agent",
            lifecycle_state="ready",
            artifact_root="artifacts/session-apntalk",
            browser_launch_error=None,
            browser_launch_error_classification=None,
            telecom=TelecomStatus(),
        ),
        adapter=adapter,
        browser=SimpleNamespace(page=page, blocked_requests=[], browser_open=False),
        operation_lock=asyncio.Lock(),
    )


@pytest.mark.asyncio
async def test_open_app_surfaces_apntalk_phase0_truth(monkeypatch: pytest.MonkeyPatch) -> None:
    service = ToolService()
    runtime = _apntalk_runtime()

    async def fake_create(target_url: str, adapter: APNTalkAdapter, headless: bool = True):
        _ = (target_url, adapter, headless)
        return runtime

    monkeypatch.setattr(service.adapters, "resolve", lambda target_url, adapter_id=None: (APNTalkAdapter(), "explicit", 1.0))
    monkeypatch.setattr(service.sessions, "create", fake_create)

    result = await service.open_app(
        {
            "target_url": "https://s022-067.apntelecom.com/agent",
            "adapter_id": "apntalk",
        }
    )

    assert result["ok"] is True
    assert result["data"]["resolved_adapter_id"] == "apntalk"
    assert result["data"]["capabilities"]["supports_webrtc_summary"] is True
    assert result["data"]["support_status"] == "login_ui_plus_bridge_observation"
    assert result["data"]["phase0_observation"]["runtime_bridge"]["status"] == "not_checked"


@pytest.mark.asyncio
async def test_active_session_snapshot_includes_phase0_observation(monkeypatch: pytest.MonkeyPatch) -> None:
    service = ToolService()
    runtime = _apntalk_runtime()

    async def fake_require_runtime_for_diagnostics(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_diagnostics", fake_require_runtime_for_diagnostics)

    result = await service.get_active_session_snapshot({"session_id": "session-apntalk"})

    assert result["ok"] is True
    assert result["data"]["phase0_observation"]["support_status"] == "login_ui_plus_bridge_observation"
    assert result["data"]["phase0_observation"]["runtime_bridge"]["status"] == "not_checked"


@pytest.mark.asyncio
async def test_open_app_surfaces_valid_bridge_with_ready_and_incoming_observation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    runtime = _apntalk_runtime(_BridgePage(_valid_bridge_payload()))

    async def fake_create(target_url: str, adapter: APNTalkAdapter, headless: bool = True):
        _ = (target_url, adapter, headless)
        return runtime

    monkeypatch.setattr(service.adapters, "resolve", lambda target_url, adapter_id=None: (APNTalkAdapter(), "explicit", 1.0))
    monkeypatch.setattr(service.sessions, "create", fake_create)

    result = await service.open_app(
        {"target_url": "https://s022-067.apntelecom.com/agent", "adapter_id": "apntalk"}
    )

    assert result["ok"] is True
    truths = {item["capability"]: item for item in result["data"]["capability_truth"]}
    assert result["data"]["phase0_observation"]["runtime_bridge"]["validation_verdict"] == "bridge_valid"
    assert truths["wait_for_ready"]["declared_support"] == "supported_with_runtime_probe"
    assert truths["wait_for_ready"]["live_detection_status"] == "detected"
    assert truths["wait_for_registration"]["declared_support"] == "supported_with_runtime_probe"
    assert truths["wait_for_registration"]["live_detection_status"] == "detected"
    assert truths["wait_for_incoming_call"]["declared_support"] == "supported_with_runtime_probe"
    assert truths["wait_for_incoming_call"]["live_detection_status"] == "detected"
    assert truths["get_peer_connection_summary"]["declared_support"] == "supported_with_runtime_probe"
    assert truths["get_peer_connection_summary"]["live_detection_status"] == "detected"
    assert truths["answer_call"]["declared_support"] == "supported_with_selector_binding"
    assert truths["answer_call"]["live_detection_status"] == "detected"
    assert truths["hangup_call"]["declared_support"] == "supported_with_selector_binding"
    assert truths["hangup_call"]["live_detection_status"] == "detected"


@pytest.mark.asyncio
async def test_get_registration_status_uses_bridge_backed_observation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    runtime = _apntalk_runtime(_BridgePage(_valid_bridge_payload()))

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.get_registration_status({"session_id": "session-apntalk"})

    assert result["ok"] is True
    assert result["data"]["registration"]["available"] is True
    assert result["data"]["registration"]["registration_state"] == "registered"


@pytest.mark.asyncio
async def test_wait_for_registration_uses_bridge_backed_observation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    runtime = _apntalk_runtime(_BridgePage(_valid_bridge_payload()))

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.wait_for_registration({"session_id": "session-apntalk", "timeout_ms": 100})

    assert result["ok"] is True
    assert result["data"]["registration_state"] == "registered"


@pytest.mark.asyncio
async def test_wait_for_registration_fails_closed_when_bridge_reports_unregistered(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    runtime = _apntalk_runtime(
        _BridgePage(
            _valid_bridge_payload(
                registration={
                    "availability": "available",
                    "isRegistered": False,
                }
            )
        )
    )

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.wait_for_registration({"session_id": "session-apntalk", "timeout_ms": 100})

    assert result["ok"] is False
    assert result["error"]["code"] == "registration_not_registered"


@pytest.mark.asyncio
async def test_wait_for_ready_uses_bridge_backed_observation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    runtime = _apntalk_runtime(_BridgePage(_valid_bridge_payload()))

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.wait_for_ready({"session_id": "session-apntalk", "timeout_ms": 100})

    assert result["ok"] is True
    assert result["data"]["ui_ready"] is True


@pytest.mark.asyncio
async def test_wait_for_ready_fails_closed_when_bridge_facts_are_insufficient(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    runtime = _apntalk_runtime(
        _BridgePage(
            _valid_bridge_payload(
                readiness={
                    "availability": "partial",
                    "lifecycleStatus": "unknown",
                    "requestedAvailability": "unknown",
                }
            )
        )
    )

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.wait_for_ready({"session_id": "session-apntalk", "timeout_ms": 100})

    assert result["ok"] is False
    assert result["error"]["code"] == "ready_state_not_satisfied"


@pytest.mark.asyncio
async def test_wait_for_incoming_call_uses_bridge_backed_observation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    runtime = _apntalk_runtime(_BridgePage(_valid_bridge_payload()))

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.wait_for_incoming_call({"session_id": "session-apntalk", "timeout_ms": 100})

    assert result["ok"] is True
    assert result["data"]["incoming_call_state"] == "ringing"


@pytest.mark.asyncio
async def test_wait_for_incoming_call_fails_closed_on_ambiguous_bridge_facts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    runtime = _apntalk_runtime(
        _BridgePage(
            _valid_bridge_payload(
                incomingCall={
                    "availability": "partial",
                    "isIncomingPresent": False,
                    "ringingState": "ringing",
                    "direction": "inbound",
                    "ambiguity": "ringing_without_inbound_direction",
                }
            )
        )
    )

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.wait_for_incoming_call({"session_id": "session-apntalk", "timeout_ms": 100})

    assert result["ok"] is False
    assert result["error"]["code"] == "incoming_call_ambiguous"


@pytest.mark.asyncio
async def test_answer_call_uses_visible_ui_control_and_connected_bridge_transition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
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
    page = _BridgePage(_valid_bridge_payload(), answer_bridge_payload=connected_payload)
    selector = '[data-apntalk-bridge-control-id="softphone-main-answer"]'
    page.selector_matches[selector] = [_SelectorMatch(on_click=lambda: setattr(page, "bridge_payload", page.answer_bridge_payload))]
    runtime = _apntalk_runtime(page)
    runtime.model.telecom.incoming_call_state = "ringing"

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.answer_call({"session_id": "session-apntalk", "timeout_ms": 100})

    assert result["ok"] is True
    assert result["data"]["active_call_state"] == "connected"
    assert result["data"]["connected_facts"]["callStatus"] == "TALKING"


@pytest.mark.asyncio
async def test_answer_call_fails_closed_when_control_is_ambiguous(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    runtime = _apntalk_runtime(
        _BridgePage(
            _valid_bridge_payload(
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
        )
    )

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.answer_call({"session_id": "session-apntalk", "timeout_ms": 100})

    assert result["ok"] is False
    assert result["error"]["code"] == "answer_control_ambiguous"


@pytest.mark.asyncio
async def test_answer_call_fails_closed_when_action_is_disallowed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    runtime = _apntalk_runtime(
        _BridgePage(
            _valid_bridge_payload(
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
        )
    )

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.answer_call({"session_id": "session-apntalk", "timeout_ms": 100})

    assert result["ok"] is False
    assert result["error"]["code"] == "answer_action_disallowed"


@pytest.mark.asyncio
async def test_answer_call_fails_closed_when_selector_matches_multiple_controls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    page = _BridgePage(_valid_bridge_payload())
    selector = '[data-apntalk-bridge-control-id="softphone-main-answer"]'
    page.selector_matches[selector] = [_SelectorMatch(), _SelectorMatch()]
    runtime = _apntalk_runtime(page)

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.answer_call({"session_id": "session-apntalk", "timeout_ms": 100})

    assert result["ok"] is False
    assert result["error"]["code"] == "multiple_selector_matches"
    assert result["error"]["classification"] == "ui_drift"


@pytest.mark.asyncio
async def test_answer_call_fails_closed_when_connected_transition_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    page = _BridgePage(_valid_bridge_payload())
    selector = '[data-apntalk-bridge-control-id="softphone-main-answer"]'
    page.selector_matches[selector] = [_SelectorMatch()]
    runtime = _apntalk_runtime(page)
    runtime.model.telecom.incoming_call_state = "ringing"

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.answer_call({"session_id": "session-apntalk", "timeout_ms": 100})

    assert result["ok"] is False
    assert result["error"]["code"] == "answer_connected_transition_missing"
    assert result["error"]["classification"] == "call_delivery_failure"


@pytest.mark.asyncio
async def test_get_peer_connection_summary_uses_bridge_backed_observation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    runtime = _apntalk_runtime(_BridgePage(_valid_bridge_payload()))

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.get_peer_connection_summary({"session_id": "session-apntalk"})

    assert result["ok"] is True
    assert result["data"]["summary"]["available"] is True
    assert result["data"]["summary"]["facts"]["hasPeerConnection"] is True
    assert result["data"]["summary"]["facts"]["connectionState"] == "connected"


@pytest.mark.asyncio
async def test_get_peer_connection_summary_fails_closed_when_bridge_marks_ambiguity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    runtime = _apntalk_runtime(
        _BridgePage(
            _valid_bridge_payload(
                peerConnection={
                    "availability": "partial",
                    "hasPeerConnection": True,
                    "ambiguity": "peer_connection_counts_unavailable",
                    "senderCount": None,
                    "receiverCount": None,
                    "transceiverCount": None,
                }
            )
        )
    )

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.get_peer_connection_summary({"session_id": "session-apntalk"})

    assert result["ok"] is True
    assert result["data"]["summary"]["available"] is False
    assert result["data"]["summary"]["reason_code"] == "peer_connection_ambiguous"


@pytest.mark.asyncio
async def test_hangup_call_uses_visible_ui_control_and_terminal_bridge_transition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
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
    page = _BridgePage(_valid_bridge_payload(), hangup_bridge_payload=terminal_payload)
    selector = '[data-apntalk-bridge-control-id="softphone-main-hangup"]'
    page.selector_matches[selector] = [_SelectorMatch(on_click=lambda: setattr(page, "bridge_payload", page.hangup_bridge_payload))]
    runtime = _apntalk_runtime(page)
    runtime.model.telecom.active_call_state = "active"
    runtime.model.telecom.incoming_call_state = "ringing"

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.hangup_call({"session_id": "session-apntalk", "timeout_ms": 100})

    assert result["ok"] is True
    assert result["data"]["active_call_state"] == "disconnected"
    assert result["data"]["terminal_facts"]["hasActiveCall"] is False


@pytest.mark.asyncio
async def test_hangup_call_fails_closed_when_control_is_ambiguous(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    runtime = _apntalk_runtime(
        _BridgePage(
            _valid_bridge_payload(
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
        )
    )

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.hangup_call({"session_id": "session-apntalk", "timeout_ms": 100})

    assert result["ok"] is False
    assert result["error"]["code"] == "hangup_control_ambiguous"


@pytest.mark.asyncio
async def test_hangup_call_fails_closed_when_selector_matches_multiple_controls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    page = _BridgePage(_valid_bridge_payload())
    selector = '[data-apntalk-bridge-control-id="softphone-main-hangup"]'
    page.selector_matches[selector] = [_SelectorMatch(), _SelectorMatch()]
    runtime = _apntalk_runtime(page)

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.hangup_call({"session_id": "session-apntalk", "timeout_ms": 100})

    assert result["ok"] is False
    assert result["error"]["code"] == "multiple_selector_matches"
    assert result["error"]["classification"] == "ui_drift"


@pytest.mark.asyncio
async def test_hangup_call_fails_closed_when_terminal_transition_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ToolService()
    page = _BridgePage(_valid_bridge_payload())
    selector = '[data-apntalk-bridge-control-id="softphone-main-hangup"]'
    page.selector_matches[selector] = [_SelectorMatch()]
    runtime = _apntalk_runtime(page)

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)

    result = await service.hangup_call({"session_id": "session-apntalk", "timeout_ms": 100})

    assert result["ok"] is False
    assert result["error"]["code"] == "hangup_terminal_transition_missing"
    assert result["error"]["classification"] == "call_delivery_failure"
