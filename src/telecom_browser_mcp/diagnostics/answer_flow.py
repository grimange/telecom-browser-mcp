from telecom_browser_mcp.models.diagnostic import DiagnosticResult
from telecom_browser_mcp.models.enums import FailureCategory


def diagnose_answer_flow(call_snapshot, webrtc_snapshot, artifacts=None) -> DiagnosticResult:
    artifacts = artifacts or []
    findings = [
        f"call_state={call_snapshot.state.value}",
        f"peer_connection_present={webrtc_snapshot.peer_connection_present}",
    ]

    likely_causes = []
    retryable = False
    if call_snapshot.state.value != "connected":
        likely_causes.append("frontend answer transition did not complete")
        retryable = True
    if not webrtc_snapshot.peer_connection_present:
        likely_causes.append("peer connection was not created after answer")
    if webrtc_snapshot.peer_connection_present and not webrtc_snapshot.remote_audio_tracks:
        likely_causes.append("peer connection exists but remote media tracks are missing")

    return DiagnosticResult(
        summary="Answer flow did not converge to connected media state",
        findings=findings,
        likely_causes=likely_causes,
        severity="high",
        failure_category=FailureCategory.CALL_CONTROL,
        retryable=retryable,
        artifacts=artifacts,
        next_recommended_tools=[
            "get_active_session_snapshot",
            "get_peer_connection_summary",
            "collect_debug_bundle",
        ],
    )
