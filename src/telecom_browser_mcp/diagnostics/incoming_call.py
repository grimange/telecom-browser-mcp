from telecom_browser_mcp.models.diagnostic import DiagnosticResult
from telecom_browser_mcp.models.enums import FailureCategory


def diagnose_incoming_call(call_snapshot, artifacts=None) -> DiagnosticResult:
    artifacts = artifacts or []
    findings = [f"call_state={call_snapshot.state.value}"]
    likely_causes = []
    if not call_snapshot.available:
        likely_causes.append(call_snapshot.reason or "incoming call UI/runtime not detected")
    if call_snapshot.state.value == "idle":
        likely_causes.append("no inbound call signal reached the frontend")

    return DiagnosticResult(
        summary="Incoming call detection did not reach ringing state",
        findings=findings,
        likely_causes=likely_causes,
        severity="high",
        failure_category=FailureCategory.CALL_CONTROL,
        retryable=True,
        artifacts=artifacts,
        next_recommended_tools=["collect_debug_bundle", "get_active_session_snapshot"],
    )
