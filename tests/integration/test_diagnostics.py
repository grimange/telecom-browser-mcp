import pytest

from telecom_browser_mcp.config.settings import Settings
from telecom_browser_mcp.tools.orchestrator import ToolOrchestrator


@pytest.mark.asyncio
async def test_answer_diagnosis_shape(tmp_path) -> None:
    settings = Settings(default_adapter="harness", artifact_root=str(tmp_path))
    tools = ToolOrchestrator(settings)

    opened = await tools.open_app(url="http://fake.local", adapter_name="harness")
    session_id = opened["data"]["session_id"]

    diagnosis = await tools.diagnose_answer_failure(session_id=session_id)
    assert diagnosis["ok"] is True
    assert "summary" in diagnosis["data"]
    assert "likely_causes" in diagnosis["data"]
    assert "browser_diagnostics" in diagnosis["data"]
    assert diagnosis["artifacts"]

    registration = await tools.diagnose_registration_failure(session_id=session_id)
    assert registration["ok"] is True
    assert "summary" in registration["data"]
    assert "browser_diagnostics" in registration["data"]
    assert registration["artifacts"]

    incoming = await tools.diagnose_incoming_call_failure(session_id=session_id)
    assert incoming["ok"] is True
    assert "summary" in incoming["data"]
    assert "browser_diagnostics" in incoming["data"]
    assert incoming["artifacts"]
