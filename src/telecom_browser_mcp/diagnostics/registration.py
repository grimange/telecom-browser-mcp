from telecom_browser_mcp.models.diagnostic import DiagnosticResult
from telecom_browser_mcp.models.enums import FailureCategory


def diagnose_registration(snapshot, artifacts=None) -> DiagnosticResult:
    artifacts = artifacts or []
    findings = [f"registration_state={snapshot.state.value}"]
    if not snapshot.available and snapshot.reason:
        findings.append(f"unavailable_reason={snapshot.reason}")

    likely_causes = []
    retryable = False
    if snapshot.state.value in {"unknown", "connecting", "initializing"}:
        likely_causes.append("registration pending or runtime hook unavailable")
        retryable = True
    if snapshot.state.value == "failed":
        likely_causes.append("app failed to register with SIP backend")

    return DiagnosticResult(
        summary="Registration did not satisfy expected state",
        findings=findings,
        likely_causes=likely_causes,
        severity="medium",
        failure_category=FailureCategory.REGISTRATION,
        retryable=retryable,
        artifacts=artifacts,
        next_recommended_tools=["get_registration_status", "collect_debug_bundle"],
    )
