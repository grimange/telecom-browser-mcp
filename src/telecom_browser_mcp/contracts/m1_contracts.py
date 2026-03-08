from __future__ import annotations

from pydantic import BaseModel

from telecom_browser_mcp.models.common import ToolResponse
from telecom_browser_mcp.models.tools import (
    CollectDebugBundleInput,
    EmptyInput,
    LoginInput,
    OpenAppInput,
    SessionInput,
    TimeoutInput,
)

M1_TOOL_INPUT_MODELS: dict[str, type[BaseModel]] = {
    "open_app": OpenAppInput,
    "list_sessions": EmptyInput,
    "close_session": SessionInput,
    "login_agent": LoginInput,
    "wait_for_ready": TimeoutInput,
    "wait_for_registration": TimeoutInput,
    "wait_for_incoming_call": TimeoutInput,
    "answer_call": TimeoutInput,
    "get_active_session_snapshot": SessionInput,
    "get_peer_connection_summary": SessionInput,
    "collect_debug_bundle": CollectDebugBundleInput,
    "diagnose_answer_failure": SessionInput,
}


def generate_m1_schemas() -> dict[str, dict]:
    schemas: dict[str, dict] = {}
    response_schema = ToolResponse.model_json_schema()
    for tool_name, model in M1_TOOL_INPUT_MODELS.items():
        schemas[tool_name] = {
            "tool": tool_name,
            "input_schema": model.model_json_schema(),
            "response_schema": response_schema,
        }
    return schemas
