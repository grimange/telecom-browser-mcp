from __future__ import annotations

import json
from pathlib import Path

import pytest

from telecom_browser_mcp.contracts.m1_contracts import M1_TOOL_INPUT_MODELS, generate_m1_schemas
from telecom_browser_mcp.tools.service import ToolService


def _contracts_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "docs" / "contracts" / "m1"


def test_generated_schemas_match_published_contract_artifacts() -> None:
    generated = generate_m1_schemas()
    for tool_name, payload in generated.items():
        schema_path = _contracts_dir() / f"{tool_name}.schema.json"
        assert schema_path.exists(), f"missing published schema for {tool_name}"
        on_disk = json.loads(schema_path.read_text(encoding="utf-8"))
        assert on_disk == payload, f"schema drift detected for {tool_name}"


@pytest.mark.asyncio
async def test_runtime_validation_rejects_undeclared_fields_for_each_tool() -> None:
    service = ToolService()

    # Create a valid session for tools that require session_id
    open_result = await service.open_app({"target_url": "https://example.com"})
    assert open_result["ok"] is True
    session_id = open_result["data"]["session_id"]

    valid_payloads: dict[str, dict] = {
        "open_app": {"target_url": "https://example.com"},
        "list_sessions": {},
        "close_session": {"session_id": session_id},
        "login_agent": {"session_id": session_id, "credentials": {}, "timeout_ms": 200},
        "wait_for_ready": {"session_id": session_id, "timeout_ms": 200},
        "wait_for_registration": {"session_id": session_id, "timeout_ms": 200},
        "wait_for_incoming_call": {"session_id": session_id, "timeout_ms": 200},
        "answer_call": {"session_id": session_id, "timeout_ms": 200},
        "get_active_session_snapshot": {"session_id": session_id},
        "get_peer_connection_summary": {"session_id": session_id},
        "collect_debug_bundle": {"session_id": session_id, "reason": "parity"},
        "diagnose_answer_failure": {"session_id": session_id},
    }

    for tool_name, model in M1_TOOL_INPUT_MODELS.items():
        payload = {**valid_payloads[tool_name], "undeclared_field": "x"}
        # EmptyInput forbids any fields, so list_sessions still fails correctly with undeclared field.
        result = await getattr(service, tool_name)(payload)
        assert result["ok"] is False, f"{tool_name} accepted undeclared field"
        assert result["error"]["code"] == "invalid_input", f"{tool_name} must surface invalid_input"

        # Canonical model must also reject same payload to prove parity.
        with pytest.raises(Exception):
            model.model_validate(payload)

