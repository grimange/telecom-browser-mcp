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
