from __future__ import annotations

from pathlib import Path

import pytest

from telecom_browser_mcp.tools.service import ToolService

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "fake_dialer.html"


def _scenario_url(name: str) -> str:
    return f"{FIXTURE_PATH.resolve().as_uri()}?scenario={name}"


async def _open_fake_session(service: ToolService, scenario: str) -> str:
    result = await service.open_app(
        {
            "target_url": _scenario_url(scenario),
            "adapter_id": "fake_dialer",
            "headless": True,
        }
    )
    assert result["ok"] is True
    session_id = result["data"]["session_id"]
    runtime = service.sessions.get(session_id)
    assert runtime is not None
    if runtime.browser.page is None:
        reason = runtime.model.browser_launch_error or "Playwright browser unavailable"
        pytest.skip(f"environment limitation: {reason}")
    return session_id


@pytest.mark.asyncio
@pytest.mark.host_required
async def test_inbound_answer_success() -> None:
    service = ToolService()
    session_id = await _open_fake_session(service, "success")

    ready = await service.wait_for_ready({"session_id": session_id, "timeout_ms": 3000})
    registration = await service.wait_for_registration({"session_id": session_id, "timeout_ms": 3000})
    incoming = await service.wait_for_incoming_call({"session_id": session_id, "timeout_ms": 3000})
    answer = await service.answer_call({"session_id": session_id, "timeout_ms": 3000})

    assert ready["ok"] is True
    assert registration["ok"] is True
    assert incoming["ok"] is True
    assert answer["ok"] is True
    assert answer["data"]["active_call_state"] == "connected"

    await service.close_session({"session_id": session_id})


@pytest.mark.asyncio
@pytest.mark.host_required
async def test_inbound_answer_failure_generates_diagnostics_and_bundle() -> None:
    service = ToolService()
    session_id = await _open_fake_session(service, "answer_fails")

    await service.wait_for_ready({"session_id": session_id, "timeout_ms": 3000})
    await service.wait_for_registration({"session_id": session_id, "timeout_ms": 3000})
    await service.wait_for_incoming_call({"session_id": session_id, "timeout_ms": 3000})
    answer = await service.answer_call({"session_id": session_id, "timeout_ms": 3000})

    assert answer["ok"] is False
    assert answer["error"]["code"] == "action_failed"
    assert answer["diagnostics"]
    assert answer["artifacts"]
    assert "bundle_path" in answer["data"]

    await service.close_session({"session_id": session_id})


@pytest.mark.asyncio
@pytest.mark.host_required
async def test_registration_missing_scenario() -> None:
    service = ToolService()
    session_id = await _open_fake_session(service, "no_registration")

    ready = await service.wait_for_ready({"session_id": session_id, "timeout_ms": 3000})
    registration = await service.wait_for_registration({"session_id": session_id, "timeout_ms": 700})

    assert ready["ok"] is True
    assert registration["ok"] is False
    assert registration["error"]["code"] == "registration_not_detected"

    await service.close_session({"session_id": session_id})


@pytest.mark.asyncio
@pytest.mark.host_required
async def test_peer_connection_missing_scenario() -> None:
    service = ToolService()
    session_id = await _open_fake_session(service, "no_peer")

    summary = await service.get_peer_connection_summary({"session_id": session_id})
    assert summary["ok"] is True
    assert summary["data"]["summary"]["available"] is False

    await service.close_session({"session_id": session_id})


@pytest.mark.asyncio
@pytest.mark.host_required
async def test_missing_answer_control_scenario() -> None:
    service = ToolService()
    session_id = await _open_fake_session(service, "missing_answer")

    await service.wait_for_ready({"session_id": session_id, "timeout_ms": 3000})
    await service.wait_for_registration({"session_id": session_id, "timeout_ms": 3000})
    await service.wait_for_incoming_call({"session_id": session_id, "timeout_ms": 3000})
    answer = await service.answer_call({"session_id": session_id, "timeout_ms": 3000})

    assert answer["ok"] is False
    assert answer["error"]["code"] == "action_failed"
    assert "answer control not found" in answer["error"]["message"]

    await service.close_session({"session_id": session_id})
