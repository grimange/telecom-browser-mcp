from __future__ import annotations

import functools
import http.server
import socketserver
import threading
from pathlib import Path

import pytest

from telecom_browser_mcp.tools.service import ToolService

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "fake_dialer.html"


class _ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


@pytest.fixture(scope="module")
def fake_dialer_base_url() -> str:
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=str(FIXTURE_PATH.parent),
    )
    with _ReusableTCPServer(("127.0.0.1", 0), handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_address[1]}/fake_dialer.html"
        finally:
            server.shutdown()
            thread.join(timeout=5)


@pytest.fixture(autouse=True)
def allow_fake_dialer_harness(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELECOM_BROWSER_MCP_ALLOWED_HOSTS", "127.0.0.1")
    monkeypatch.setenv("TELECOM_BROWSER_MCP_ALLOW_LOCAL_TARGETS", "1")


def _scenario_url(base_url: str, name: str) -> str:
    return f"{base_url}?scenario={name}"


async def _open_fake_session(service: ToolService, base_url: str, scenario: str) -> str:
    result = await service.open_app(
        {
            "target_url": _scenario_url(base_url, scenario),
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
async def test_inbound_answer_success(fake_dialer_base_url: str) -> None:
    service = ToolService()
    session_id = await _open_fake_session(service, fake_dialer_base_url, "success")

    ready = await service.wait_for_ready({"session_id": session_id, "timeout_ms": 3000})
    registration = await service.wait_for_registration({"session_id": session_id, "timeout_ms": 3000})
    incoming = await service.wait_for_incoming_call({"session_id": session_id, "timeout_ms": 3000})
    answer = await service.answer_call({"session_id": session_id, "timeout_ms": 3000})

    assert ready["ok"] is True
    assert registration["ok"] is True
    assert incoming["ok"] is True
    assert answer["ok"] is True
    assert answer["data"]["active_call_state"] == "connected"

    hangup = await service.hangup_call({"session_id": session_id, "timeout_ms": 3000})
    assert hangup["ok"] is True
    assert hangup["data"]["active_call_state"] == "disconnected"

    await service.close_session({"session_id": session_id})


@pytest.mark.asyncio
@pytest.mark.host_required
async def test_inbound_answer_failure_generates_diagnostics_and_bundle(fake_dialer_base_url: str) -> None:
    service = ToolService()
    session_id = await _open_fake_session(service, fake_dialer_base_url, "answer_fails")

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
async def test_registration_missing_scenario(fake_dialer_base_url: str) -> None:
    service = ToolService()
    session_id = await _open_fake_session(service, fake_dialer_base_url, "no_registration")

    ready = await service.wait_for_ready({"session_id": session_id, "timeout_ms": 3000})
    registration = await service.wait_for_registration({"session_id": session_id, "timeout_ms": 700})

    assert ready["ok"] is True
    assert registration["ok"] is False
    assert registration["error"]["code"] == "registration_not_detected"

    await service.close_session({"session_id": session_id})


@pytest.mark.asyncio
@pytest.mark.host_required
async def test_peer_connection_missing_scenario(fake_dialer_base_url: str) -> None:
    service = ToolService()
    session_id = await _open_fake_session(service, fake_dialer_base_url, "no_peer")

    summary = await service.get_peer_connection_summary({"session_id": session_id})
    assert summary["ok"] is True
    assert summary["data"]["summary"]["available"] is False

    await service.close_session({"session_id": session_id})


@pytest.mark.asyncio
@pytest.mark.host_required
async def test_missing_answer_control_scenario(fake_dialer_base_url: str) -> None:
    service = ToolService()
    session_id = await _open_fake_session(service, fake_dialer_base_url, "missing_answer")

    await service.wait_for_ready({"session_id": session_id, "timeout_ms": 3000})
    await service.wait_for_registration({"session_id": session_id, "timeout_ms": 3000})
    await service.wait_for_incoming_call({"session_id": session_id, "timeout_ms": 3000})
    answer = await service.answer_call({"session_id": session_id, "timeout_ms": 3000})

    assert answer["ok"] is False
    assert answer["error"]["code"] == "action_failed"
    assert "answer control not found" in answer["error"]["message"]

    await service.close_session({"session_id": session_id})


@pytest.mark.asyncio
@pytest.mark.host_required
async def test_delayed_registration_scenario(fake_dialer_base_url: str) -> None:
    service = ToolService()
    session_id = await _open_fake_session(service, fake_dialer_base_url, "delayed_registration")

    registration = await service.wait_for_registration({"session_id": session_id, "timeout_ms": 1500})

    assert registration["ok"] is True
    assert registration["data"]["registration_state"] == "registered"

    await service.close_session({"session_id": session_id})


@pytest.mark.asyncio
@pytest.mark.host_required
async def test_missing_incoming_call_scenario(fake_dialer_base_url: str) -> None:
    service = ToolService()
    session_id = await _open_fake_session(service, fake_dialer_base_url, "missing_incoming_call")

    await service.wait_for_registration({"session_id": session_id, "timeout_ms": 1000})
    incoming = await service.wait_for_incoming_call({"session_id": session_id, "timeout_ms": 700})

    assert incoming["ok"] is False
    assert incoming["error"]["code"] == "call_delivery_failure"

    await service.close_session({"session_id": session_id})


@pytest.mark.asyncio
@pytest.mark.host_required
async def test_duplicate_incoming_call_summary(fake_dialer_base_url: str) -> None:
    service = ToolService()
    session_id = await _open_fake_session(service, fake_dialer_base_url, "duplicate_incoming_call")

    await service.wait_for_registration({"session_id": session_id, "timeout_ms": 1000})
    await service.wait_for_incoming_call({"session_id": session_id, "timeout_ms": 1000})
    summary = await service.get_peer_connection_summary({"session_id": session_id})

    assert summary["ok"] is True
    assert summary["data"]["summary"]["incoming_delivery_count"] >= 2

    await service.close_session({"session_id": session_id})


@pytest.mark.asyncio
@pytest.mark.host_required
async def test_connected_no_remote_audio_summary(fake_dialer_base_url: str) -> None:
    service = ToolService()
    session_id = await _open_fake_session(service, fake_dialer_base_url, "connected_no_remote_audio")

    await service.wait_for_registration({"session_id": session_id, "timeout_ms": 1000})
    await service.wait_for_incoming_call({"session_id": session_id, "timeout_ms": 1000})
    await service.answer_call({"session_id": session_id, "timeout_ms": 1000})
    summary = await service.get_peer_connection_summary({"session_id": session_id})

    assert summary["ok"] is True
    assert summary["data"]["summary"]["media_status"]["remote_audio"] is False

    await service.close_session({"session_id": session_id})


@pytest.mark.asyncio
@pytest.mark.host_required
async def test_registration_and_store_snapshots(fake_dialer_base_url: str) -> None:
    service = ToolService()
    session_id = await _open_fake_session(service, fake_dialer_base_url, "store_ui_divergence")

    await service.wait_for_registration({"session_id": session_id, "timeout_ms": 1000})
    registration = await service.get_registration_status({"session_id": session_id})
    store = await service.get_store_snapshot({"session_id": session_id})

    assert registration["ok"] is True
    assert registration["data"]["registration"]["registration_state"] == "registered"
    assert store["ok"] is True
    assert store["data"]["store_snapshot"]["store"]["registration"] == "pending"

    await service.close_session({"session_id": session_id})
