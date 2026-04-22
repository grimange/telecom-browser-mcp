import pytest
from pydantic import ValidationError

from telecom_browser_mcp.models.common import ToolResponse
from telecom_browser_mcp.models.tools import (
    CollectDebugBundleInput,
    LoginInput,
    OpenAppInput,
    TimeoutInput,
)


def test_tool_response_contract_version_required() -> None:
    response = ToolResponse(ok=True, tool="x")
    dumped = response.model_dump(mode="json")
    assert dumped["meta"]["contract_version"] == "v1"
    assert dumped["tool"] == "x"
    assert dumped["ok"] is True


@pytest.mark.parametrize("timeout_ms", [0, 99, 120001])
def test_timeout_bounds_reject_invalid_values(timeout_ms: int) -> None:
    with pytest.raises(ValidationError):
        TimeoutInput.model_validate({"session_id": "session-1", "timeout_ms": timeout_ms})


def test_overlong_labels_and_reasons_are_rejected() -> None:
    with pytest.raises(ValidationError):
        OpenAppInput.model_validate({"target_url": "https://example.com", "session_label": "x" * 121})
    with pytest.raises(ValidationError):
        CollectDebugBundleInput.model_validate({"session_id": "session-1", "reason": "x" * 241})


def test_login_credentials_default_does_not_leak_between_instances() -> None:
    first = LoginInput.model_validate({"session_id": "session-1"})
    second = LoginInput.model_validate({"session_id": "session-2"})

    first.credentials["token"] = "synthetic"

    assert second.credentials == {}
