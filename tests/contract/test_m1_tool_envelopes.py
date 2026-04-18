from __future__ import annotations

import pytest

from telecom_browser_mcp.tools.service import ToolService


def _assert_base_envelope(payload: dict, tool: str) -> None:
    assert payload["tool"] == tool
    assert "ok" in payload
    assert "data" in payload
    assert "diagnostics" in payload
    assert isinstance(payload["diagnostics"], list)
    assert "artifacts" in payload
    assert isinstance(payload["artifacts"], list)
    assert "meta" in payload
    assert payload["meta"]["contract_version"]
    if payload["ok"] is False:
        assert payload["error"] is not None
        assert payload["error"]["code"]


@pytest.mark.asyncio
async def test_all_m1_tools_return_canonical_envelope() -> None:
    service = ToolService()

    health_result = await service.health({})
    _assert_base_envelope(health_result, "health")

    capabilities_result = await service.capabilities({})
    _assert_base_envelope(capabilities_result, "capabilities")

    open_result = await service.open_app({"target_url": "https://example.com"})
    _assert_base_envelope(open_result, "open_app")
    session_id = open_result["data"]["session_id"]

    list_result = await service.list_sessions({})
    _assert_base_envelope(list_result, "list_sessions")

    login_result = await service.login_agent(
        {"session_id": session_id, "credentials": {}, "timeout_ms": 100}
    )
    _assert_base_envelope(login_result, "login_agent")

    ready_result = await service.wait_for_ready({"session_id": session_id, "timeout_ms": 100})
    _assert_base_envelope(ready_result, "wait_for_ready")

    registration_result = await service.wait_for_registration(
        {"session_id": session_id, "timeout_ms": 100}
    )
    _assert_base_envelope(registration_result, "wait_for_registration")

    incoming_result = await service.wait_for_incoming_call(
        {"session_id": session_id, "timeout_ms": 100}
    )
    _assert_base_envelope(incoming_result, "wait_for_incoming_call")

    answer_result = await service.answer_call({"session_id": session_id, "timeout_ms": 100})
    _assert_base_envelope(answer_result, "answer_call")

    hangup_result = await service.hangup_call({"session_id": session_id, "timeout_ms": 100})
    _assert_base_envelope(hangup_result, "hangup_call")

    registration_status_result = await service.get_registration_status({"session_id": session_id})
    _assert_base_envelope(registration_status_result, "get_registration_status")

    snapshot_result = await service.get_active_session_snapshot({"session_id": session_id})
    _assert_base_envelope(snapshot_result, "get_active_session_snapshot")

    store_result = await service.get_store_snapshot({"session_id": session_id})
    _assert_base_envelope(store_result, "get_store_snapshot")

    peer_result = await service.get_peer_connection_summary({"session_id": session_id})
    _assert_base_envelope(peer_result, "get_peer_connection_summary")

    bundle_result = await service.collect_debug_bundle({"session_id": session_id, "reason": "contract"})
    _assert_base_envelope(bundle_result, "collect_debug_bundle")

    diagnosis_result = await service.diagnose_answer_failure({"session_id": session_id})
    _assert_base_envelope(diagnosis_result, "diagnose_answer_failure")

    close_result = await service.close_session({"session_id": session_id})
    _assert_base_envelope(close_result, "close_session")


@pytest.mark.asyncio
async def test_error_envelope_includes_code_for_missing_session_tools() -> None:
    service = ToolService()
    missing = "missing-session"

    tools_and_payloads = [
        ("close_session", {"session_id": missing}),
        ("login_agent", {"session_id": missing, "credentials": {}, "timeout_ms": 100}),
        ("wait_for_ready", {"session_id": missing, "timeout_ms": 100}),
        ("wait_for_registration", {"session_id": missing, "timeout_ms": 100}),
        ("wait_for_incoming_call", {"session_id": missing, "timeout_ms": 100}),
        ("answer_call", {"session_id": missing, "timeout_ms": 100}),
        ("hangup_call", {"session_id": missing, "timeout_ms": 100}),
        ("get_registration_status", {"session_id": missing}),
        ("get_active_session_snapshot", {"session_id": missing}),
        ("get_store_snapshot", {"session_id": missing}),
        ("get_peer_connection_summary", {"session_id": missing}),
        ("collect_debug_bundle", {"session_id": missing, "reason": "missing"}),
        ("diagnose_answer_failure", {"session_id": missing}),
    ]

    for tool_name, payload in tools_and_payloads:
        result = await getattr(service, tool_name)(payload)
        _assert_base_envelope(result, tool_name)
        assert result["ok"] is False
        assert result["error"]["code"] == "session_not_found"


@pytest.mark.asyncio
async def test_session_bound_envelopes_include_adapter_identity_fields() -> None:
    service = ToolService()
    open_result = await service.open_app({"target_url": "https://example.com"})
    session_id = open_result["data"]["session_id"]

    snapshot_result = await service.get_active_session_snapshot({"session_id": session_id})

    _assert_base_envelope(snapshot_result, "get_active_session_snapshot")
    assert snapshot_result["meta"]["adapter_id"] == open_result["meta"]["adapter_id"]
    assert snapshot_result["meta"]["adapter_name"] == open_result["meta"]["adapter_name"]
    assert snapshot_result["meta"]["adapter_version"] == open_result["meta"]["adapter_version"]
    assert snapshot_result["meta"]["scenario_id"] == open_result["meta"]["scenario_id"]
