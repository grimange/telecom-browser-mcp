import pytest

from telecom_browser_mcp.config.settings import Settings
from telecom_browser_mcp.tools.orchestrator import ToolOrchestrator


@pytest.mark.asyncio
async def test_harness_inbound_answer_flow(tmp_path) -> None:
    settings = Settings(default_adapter="harness", artifact_root=str(tmp_path))
    tools = ToolOrchestrator(settings)

    opened = await tools.open_app(url="http://fake.local", adapter_name="harness")
    assert opened["ok"] is True
    session_id = opened["data"]["session_id"]

    registration = await tools.wait_for_registration(session_id=session_id)
    assert registration["ok"] is True

    incoming = await tools.wait_for_incoming_call(session_id=session_id)
    assert incoming["ok"] is True
    assert incoming["data"]["state"] == "ringing"

    answered = await tools.answer_call(session_id=session_id)
    assert answered["ok"] is True
    assert answered["data"]["call"]["state"] == "connected"

    debug_bundle = await tools.collect_debug_bundle(session_id=session_id)
    assert debug_bundle["ok"] is True
    assert debug_bundle["artifacts"]

    environment = await tools.get_environment_snapshot(session_id=session_id)
    assert environment["ok"] is True
    assert "platform" in environment["data"]

    browser_logs = await tools.collect_browser_logs(session_id=session_id)
    assert browser_logs["ok"] is True
    assert len(browser_logs["artifacts"]) == 2

    one_way = await tools.diagnose_one_way_audio(session_id=session_id)
    assert one_way["ok"] is True
    assert "likely_causes" in one_way["data"]
