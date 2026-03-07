import pytest

from telecom_browser_mcp.config.settings import Settings
from telecom_browser_mcp.tools.orchestrator import ToolOrchestrator


@pytest.mark.asyncio
async def test_registration_flapping_scenario(tmp_path) -> None:
    settings = Settings(default_adapter="harness", artifact_root=str(tmp_path))
    tools = ToolOrchestrator(settings)

    opened = await tools.open_app(url="http://fake.local", adapter_name="harness")
    session_id = opened["data"]["session_id"]
    await tools.login_agent(session_id=session_id, username="agent", password="secret", tenant="registration_flapping")
    await tools.wait_for_registration(session_id=session_id)

    snap1 = await tools.get_registration_status(session_id=session_id)
    snap2 = await tools.get_registration_status(session_id=session_id)

    assert snap1["ok"] is True
    assert snap2["ok"] is True
    assert snap1["data"]["state"] != snap2["data"]["state"]


@pytest.mark.asyncio
async def test_duplicate_incoming_and_ui_mismatch_scenarios(tmp_path) -> None:
    settings = Settings(default_adapter="harness", artifact_root=str(tmp_path))
    tools = ToolOrchestrator(settings)

    opened = await tools.open_app(url="http://fake.local", adapter_name="harness")
    session_id = opened["data"]["session_id"]
    await tools.login_agent(
        session_id=session_id,
        username="agent",
        password="secret",
        tenant="incoming_duplicate,answer_ui_mismatch",
    )
    await tools.wait_for_registration(session_id=session_id)

    incoming = await tools.wait_for_incoming_call(session_id=session_id)
    assert incoming["ok"] is True
    assert incoming["data"]["correlation_keys"]["duplicate_events"] == "2"

    answered = await tools.answer_call(session_id=session_id)
    assert answered["ok"] is True
    assert "UI and store call state mismatch detected after answer" in answered["warnings"]


@pytest.mark.asyncio
async def test_screenshot_fallback_artifact(tmp_path) -> None:
    settings = Settings(default_adapter="harness", artifact_root=str(tmp_path))
    tools = ToolOrchestrator(settings)

    opened = await tools.open_app(url="http://fake.local", adapter_name="harness")
    session_id = opened["data"]["session_id"]

    capture = await tools.screenshot(session_id=session_id, label="fallback")
    assert capture["ok"] is True
    assert capture["artifacts"]
    assert "placeholder screenshot artifact" in " ".join(capture["warnings"])


@pytest.mark.asyncio
async def test_delayed_registration_then_success(tmp_path) -> None:
    settings = Settings(default_adapter="harness", artifact_root=str(tmp_path))
    tools = ToolOrchestrator(settings)

    opened = await tools.open_app(url="http://fake.local", adapter_name="harness")
    session_id = opened["data"]["session_id"]
    await tools.login_agent(
        session_id=session_id,
        username="agent",
        password="secret",
        tenant="registration_delayed",
    )

    first = await tools.wait_for_registration(session_id=session_id)
    second = await tools.wait_for_registration(session_id=session_id)

    assert first["ok"] is False
    assert first["error_code"] == "REGISTRATION_TIMEOUT"
    assert second["ok"] is True
    assert second["data"]["state"] == "registered"


@pytest.mark.asyncio
async def test_incoming_absent_and_answer_timeout_scenarios(tmp_path) -> None:
    settings = Settings(default_adapter="harness", artifact_root=str(tmp_path))
    tools = ToolOrchestrator(settings)

    opened = await tools.open_app(url="http://fake.local", adapter_name="harness")
    session_id = opened["data"]["session_id"]
    await tools.login_agent(
        session_id=session_id,
        username="agent",
        password="secret",
        tenant="incoming_absent,answer_timeout",
    )
    await tools.wait_for_registration(session_id=session_id)

    incoming = await tools.wait_for_incoming_call(session_id=session_id, timeout_ms=1)
    assert incoming["ok"] is False
    assert incoming["error_code"] == "INCOMING_CALL_TIMEOUT"

    answered = await tools.answer_call(session_id=session_id, timeout_ms=1)
    assert answered["ok"] is False
    assert answered["error_code"] == "ANSWER_FLOW_FAILED"
