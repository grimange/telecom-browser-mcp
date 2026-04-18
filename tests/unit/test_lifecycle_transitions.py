import pytest

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
