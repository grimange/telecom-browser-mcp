import pytest

from telecom_browser_mcp.browser.manager import BlockedBrowserRequest
from telecom_browser_mcp.tools.service import ToolService


def test_mark_broken_ignores_missing_session() -> None:
    service = ToolService()
    service.sessions.mark_broken("missing")


@pytest.mark.asyncio
async def test_mark_broken_sets_state_for_active_session() -> None:
    service = ToolService()
    opened = await service.open_app({"target_url": "https://example.com"})
    session_id = opened["data"]["session_id"]
    runtime = service.sessions.get(session_id)
    assert runtime is not None
    runtime.model.lifecycle_state = "ready"
    service.sessions.mark_broken(session_id)
    assert runtime.model.lifecycle_state == "broken"


@pytest.mark.asyncio
async def test_broken_session_rejects_browser_actions_but_allows_diagnostics() -> None:
    service = ToolService()
    opened = await service.open_app({"target_url": "https://example.com"})
    session_id = opened["data"]["session_id"]
    runtime = service.sessions.get(session_id)
    assert runtime is not None

    runtime.model.lifecycle_state = "broken"

    action = await service.wait_for_ready({"session_id": session_id, "timeout_ms": 100})
    snapshot = await service.get_active_session_snapshot({"session_id": session_id})
    diagnosis = await service.diagnose_answer_failure({"session_id": session_id})

    assert action["ok"] is False
    assert action["error"]["code"] == "session_broken"
    assert snapshot["ok"] is True
    assert diagnosis["ok"] is True


@pytest.mark.asyncio
async def test_blocked_secondary_browser_request_rejects_next_action() -> None:
    service = ToolService()
    opened = await service.open_app({"target_url": "https://example.com"})
    session_id = opened["data"]["session_id"]
    runtime = service.sessions.get(session_id)
    assert runtime is not None

    runtime.browser.blocked_requests.append(
        BlockedBrowserRequest(
            url="http://127.0.0.1/private",
            reason_code="unsafe_resolved_address",
            resource_type="fetch",
            is_navigation_request=False,
        )
    )

    action = await service.wait_for_ready({"session_id": session_id, "timeout_ms": 100})

    assert action["ok"] is False
    assert action["error"]["code"] == "target_url_blocked"
    assert action["error"]["classification"] == "security_policy"
    assert action["diagnostics"][0]["classification"] == "session_state"
    assert any(item["code"] == "unsafe_resolved_address" for item in action["diagnostics"])
