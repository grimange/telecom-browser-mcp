from __future__ import annotations

from telecom_browser_mcp.models.common import DiagnosticItem
from telecom_browser_mcp.sessions.manager import SessionRuntime


class DiagnosticsEngine:
    def diagnose_answer_failure(self, runtime: SessionRuntime) -> list[DiagnosticItem]:
        status = runtime.model.telecom
        diagnostics: list[DiagnosticItem] = []

        if not status.ui_ready:
            diagnostics.append(
                DiagnosticItem(
                    code="session_not_ready",
                    classification="session_not_ready",
                    message="UI readiness was not confirmed before answer attempt",
                    confidence="high",
                )
            )

        if status.registration_state != "registered":
            diagnostics.append(
                DiagnosticItem(
                    code="registration_missing",
                    classification="registration_missing",
                    message="No registered SIP/WebRTC state was observed",
                    confidence="high",
                )
            )

        if status.incoming_call_state != "ringing":
            diagnostics.append(
                DiagnosticItem(
                    code="incoming_call_not_present",
                    classification="incoming_call_not_present",
                    message="No incoming call presentation was observed",
                    confidence="medium",
                )
            )

        if runtime.model.capabilities.supports_answer_action is False:
            diagnostics.append(
                DiagnosticItem(
                    code="adapter_not_supported",
                    classification="adapter_not_supported",
                    message="Resolved adapter does not support answer action",
                    confidence="high",
                )
            )

        if not diagnostics:
            diagnostics.append(
                DiagnosticItem(
                    code="unknown",
                    classification="unknown",
                    message="No explicit failure signal was found",
                    confidence="low",
                )
            )
        return diagnostics
