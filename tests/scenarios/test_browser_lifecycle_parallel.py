import pytest

from telecom_browser_mcp.config.settings import Settings
from telecom_browser_mcp.tools.orchestrator import ToolOrchestrator


@pytest.mark.asyncio
async def test_parallel_sessions_open_and_close(tmp_path) -> None:
    settings = Settings(default_adapter="harness", artifact_root=str(tmp_path))
    tools = ToolOrchestrator(settings)

    first = await tools.open_app(url="http://fake.local/1", adapter_name="harness")
    second = await tools.open_app(url="http://fake.local/2", adapter_name="harness")

    sid1 = first["data"]["session_id"]
    sid2 = second["data"]["session_id"]

    listed = await tools.list_sessions()
    assert listed["ok"] is True
    ids = {s["session_id"] for s in listed["data"]["sessions"]}
    assert sid1 in ids and sid2 in ids

    closed1 = await tools.close_session(session_id=sid1)
    closed2 = await tools.close_session(session_id=sid2)

    assert closed1["ok"] is True
    assert closed2["ok"] is True
