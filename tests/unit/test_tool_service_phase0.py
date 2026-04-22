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
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(payload.get(key), dict):
            payload[key] = {**payload[key], **value}
        else:
            payload[key] = value
    return payload


class _BridgePage:
    def __init__(self, bridge_payload: object) -> None:
        self.bridge_payload = bridge_payload

    async def evaluate(self, script: str):
        if "const bridge = window.__apnTalkTestBridge" in script:
            return self.bridge_payload
        if "navigator.permissions?.query" in script:
            return {"available": True, "state": "granted"}
        if "const groups =" in script:
            return {}
        return {}


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
    assert result["data"]["capabilities"]["supports_webrtc_summary"] is False
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
    assert truths["wait_for_incoming_call"]["declared_support"] == "supported_with_runtime_probe"
    assert truths["wait_for_incoming_call"]["live_detection_status"] == "detected"
    assert truths["wait_for_registration"]["declared_support"] == "scaffold_only"


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
