from telecom_browser_mcp.models.enums import ErrorCode, FailureCategory
from telecom_browser_mcp.models.envelope import failure_response, success_response
from telecom_browser_mcp.models.registration import RegistrationSnapshot


def test_success_envelope_has_required_fields() -> None:
    response = success_response(message="ok")
    assert response["ok"] is True
    assert "timestamp" in response
    assert "duration_ms" in response
    assert "artifacts" in response
    assert "warnings" in response


def test_failure_envelope_has_required_fields() -> None:
    response = failure_response(
        message="failed",
        error_code=ErrorCode.ANSWER_FLOW_FAILED,
        failure_category=FailureCategory.CALL_CONTROL,
        retryable=False,
    )
    assert response["ok"] is False
    assert response["error_code"] == "ANSWER_FLOW_FAILED"
    assert response["failure_category"] == "call_control"
    assert "likely_causes" in response
    assert "next_recommended_tools" in response


def test_registration_snapshot_serialization() -> None:
    snapshot = RegistrationSnapshot()
    payload = snapshot.model_dump(mode="json")
    assert payload["state"] == "unknown"
    assert payload["registered"] is False
