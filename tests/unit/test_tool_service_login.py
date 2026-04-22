from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from telecom_browser_mcp.adapters.apntalk import APNTalkAdapter
from telecom_browser_mcp.adapters.base import AdapterOperationResult
from telecom_browser_mcp.models.session import TelecomStatus
from telecom_browser_mcp.tools.service import ToolService


class _StubLoginAdapter(APNTalkAdapter):
    def __init__(self, result: AdapterOperationResult) -> None:
        self._result = result

    async def login(
        self,
        status: TelecomStatus,
        page: object,
        credentials: dict[str, object],
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, credentials, timeout_ms)
        return self._result


def _runtime(adapter: APNTalkAdapter) -> SimpleNamespace:
    return SimpleNamespace(
        model=SimpleNamespace(
            session_id="session-1",
            lifecycle_state="ready",
            browser_launch_error=None,
            browser_launch_error_classification=None,
            telecom=TelecomStatus(),
        ),
        adapter=adapter,
        browser=SimpleNamespace(page=object(), blocked_requests=[], browser_open=True),
        operation_lock=asyncio.Lock(),
    )


@pytest.mark.asyncio
async def test_login_agent_accepts_adapter_operation_result_success(monkeypatch: pytest.MonkeyPatch) -> None:
    service = ToolService()
    runtime = _runtime(
        _StubLoginAdapter(
            AdapterOperationResult(
                ok=True,
                message="login ok",
                details={"landing_url": "https://s022-067.apntelecom.com/dashboard"},
            )
        )
    )

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)
    monkeypatch.setattr(service, "_require_browser_page", lambda tool, runtime: None)

    result = await service.login_agent(
        {
            "session_id": "session-1",
            "credentials": {"email": "agent@example.test", "password": "secret"},
            "timeout_ms": 100,
        }
    )

    assert result["ok"] is True
    assert result["data"]["login_complete"] is True
    assert result["data"]["landing_url"] == "https://s022-067.apntelecom.com/dashboard"
    assert runtime.model.telecom.login_complete is True


@pytest.mark.asyncio
async def test_login_agent_returns_failure_envelope_for_adapter_operation_result_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    service = ToolService()
    runtime = _runtime(
        _StubLoginAdapter(
            AdapterOperationResult(
                ok=False,
                message="post-login page not confirmed",
                error_code="state_divergence",
                classification="state_divergence",
                retryable=True,
            )
        )
    )

    async def fake_require_runtime_for_action(tool: str, session_id: str):
        _ = (tool, session_id)
        return runtime, None

    monkeypatch.setattr(service, "_require_runtime_for_action", fake_require_runtime_for_action)
    monkeypatch.setattr(service, "_require_browser_page", lambda tool, runtime: None)

    result = await service.login_agent(
        {
            "session_id": "session-1",
            "credentials": {"email": "agent@example.test", "password": "secret"},
            "timeout_ms": 100,
        }
    )

    assert result["ok"] is False
    assert result["error"]["code"] == "state_divergence"
    assert result["error"]["classification"] == "state_divergence"
    assert result["error"]["retryable"] is True
    assert runtime.model.telecom.login_complete is False
