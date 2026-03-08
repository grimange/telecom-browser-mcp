from __future__ import annotations

import asyncio

import pytest

from telecom_browser_mcp.tools.service import ToolService


@pytest.mark.asyncio
async def test_close_session_waits_for_inflight_operation_lock() -> None:
    service = ToolService()
    opened = await service.open_app({"target_url": "https://example.com"})
    session_id = opened["data"]["session_id"]
    runtime = service.sessions.get(session_id)
    assert runtime is not None

    await runtime.operation_lock.acquire()
    close_task = asyncio.create_task(service.close_session({"session_id": session_id}))
    await asyncio.sleep(0.05)
    assert close_task.done() is False

    runtime.operation_lock.release()
    closed = await close_task
    assert closed["ok"] is True
    assert closed["data"]["closed"] is True


@pytest.mark.asyncio
async def test_session_broken_errors_include_session_state_diagnostics() -> None:
    service = ToolService()
    opened = await service.open_app({"target_url": "https://example.com"})
    session_id = opened["data"]["session_id"]
    runtime = service.sessions.get(session_id)
    assert runtime is not None

    runtime.browser.page = None
    runtime.model.browser_launch_error = "browser page missing"
    runtime.model.browser_launch_error_classification = "session_not_ready"
    runtime.model.telecom.browser_open = False

    result = await service.wait_for_registration({"session_id": session_id, "timeout_ms": 100})
    assert result["ok"] is False
    assert result["error"]["code"] == "session_broken"
    codes = {item["code"] for item in result["diagnostics"]}
    assert "session_state" in codes
    assert "browser_state" in codes
    assert "browser_launch_error" in codes


@pytest.mark.asyncio
async def test_session_busy_error_when_operation_lock_times_out() -> None:
    service = ToolService(operation_lock_timeout_ms=50)
    opened = await service.open_app({"target_url": "https://example.com"})
    session_id = opened["data"]["session_id"]
    runtime = service.sessions.get(session_id)
    assert runtime is not None

    await runtime.operation_lock.acquire()
    result = await service.wait_for_ready({"session_id": session_id, "timeout_ms": 100})
    runtime.operation_lock.release()

    assert result["ok"] is False
    assert result["error"]["code"] == "not_ready"
    assert result["error"]["classification"] == "session_busy"
    assert result["error"]["retryable"] is True
    codes = {item["code"] for item in result["diagnostics"]}
    assert "session_busy" in codes
