from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from telecom_browser_mcp.adapters.registry import AdapterRegistry
from telecom_browser_mcp.browser.diagnostics import BrowserDiagnosticsCollector
from telecom_browser_mcp.config.settings import Settings
from telecom_browser_mcp.diagnostics.answer_flow import diagnose_answer_flow
from telecom_browser_mcp.diagnostics.incoming_call import diagnose_incoming_call
from telecom_browser_mcp.diagnostics.registration import diagnose_registration
from telecom_browser_mcp.evidence.bundle_writer import EvidenceBundleWriter
from telecom_browser_mcp.evidence.markdown_report import write_markdown_report
from telecom_browser_mcp.inspectors.environment_inspector import EnvironmentInspector
from telecom_browser_mcp.models.enums import ErrorCode, FailureCategory
from telecom_browser_mcp.models.envelope import failure_response, success_response
from telecom_browser_mcp.sessions.manager import SessionManager


class ToolOrchestrator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.registry = AdapterRegistry()
        self.session_manager = SessionManager(artifact_root=__import__("pathlib").Path(settings.artifact_root))
        self.bundle_writer = EvidenceBundleWriter(redact=settings.redact)
        self.environment_inspector = EnvironmentInspector()
        self._adapter_for_session: dict[str, object] = {}

    def _timer(self) -> float:
        return perf_counter()

    @staticmethod
    def _duration_ms(start: float) -> int:
        return int((perf_counter() - start) * 1000)

    def _session_missing(self, session_id: str, start: float) -> dict:
        return failure_response(
            message=f"session not found: {session_id}",
            error_code=ErrorCode.SESSION_NOT_FOUND,
            failure_category=FailureCategory.SESSION,
            retryable=False,
            likely_causes=["invalid session id", "session already closed"],
            next_recommended_tools=["list_sessions", "open_app"],
            duration_ms=self._duration_ms(start),
        )

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    async def _collect_browser_diagnostics_bundle(
        self,
        *,
        session,
        scenario_id: str,
        fault_type: str,
        injection_point: str,
        status: str,
        failure_classification: str,
    ) -> tuple[list[dict], list[str], dict]:
        if session.driver is not None and hasattr(session.driver, "collect_diagnostics_bundle"):
            result = await session.driver.collect_diagnostics_bundle(
                base_dir=session.artifacts_dir,
                run_id=session.run_id,
                scenario_id=scenario_id,
                session_id=session.session_id,
                fault_type=fault_type,
                injection_point=injection_point,
                status=status,
                failure_classification=failure_classification,
            )
        else:
            collector = BrowserDiagnosticsCollector(trace_enabled=False)
            collector.collection_gaps.append(
                "no active Playwright runtime bound to session; captured bundle with explicit gaps"
            )
            result = await collector.write_bundle(
                base_dir=session.artifacts_dir,
                run_id=session.run_id,
                scenario_id=scenario_id,
                session_id=session.session_id,
                fault_type=fault_type,
                injection_point=injection_point,
                status=status,
                failure_classification=failure_classification,
            )

        artifacts = [
            {
                "type": "manifest",
                "label": "browser-diagnostics-manifest",
                "path": result["manifest_path"],
                "redacted": self.settings.redact,
                "created_at": self._now(),
            },
            {
                "type": "report",
                "label": "browser-diagnostics-summary",
                "path": result["summary_path"],
                "redacted": self.settings.redact,
                "created_at": self._now(),
            },
        ]
        data = {
            "bundle_dir": result["bundle_dir"],
            "manifest_path": result["manifest_path"],
            "summary_path": result["summary_path"],
            "artifact_paths": result["artifact_paths"],
        }
        return artifacts, result["collection_gaps"], data

    async def open_app(self, url: str, adapter_name: str | None = None) -> dict:
        start = self._timer()
        name = adapter_name or self.settings.default_adapter
        try:
            adapter = self.registry.create(name)
        except ValueError as exc:
            return failure_response(
                message=str(exc),
                error_code=ErrorCode.ADAPTER_CONTRACT_ERROR,
                failure_category=FailureCategory.ADAPTER,
                retryable=False,
                likely_causes=["adapter name is not registered"],
                next_recommended_tools=[],
                duration_ms=self._duration_ms(start),
            )

        session = self.session_manager.create_session(
            adapter_name=adapter.name,
            adapter_version=adapter.version,
            headless=self.settings.headless,
        )
        self._adapter_for_session[session.session_id] = adapter
        result = await adapter.open_app(session, url)

        if not result.get("ok"):
            return failure_response(
                message=str(result.get("message", "failed to open app")),
                error_code=ErrorCode.ENVIRONMENT_LIMITATION,
                failure_category=FailureCategory.ENVIRONMENT,
                retryable=True,
                likely_causes=[
                    "browser binary missing",
                    "sandbox prevented browser launch",
                    "target url unreachable",
                ],
                next_recommended_tools=["open_app"],
                duration_ms=self._duration_ms(start),
                session_id=session.session_id,
            )

        return success_response(
            message="application opened",
            duration_ms=self._duration_ms(start),
            session_id=session.session_id,
            data={
                "session_id": session.session_id,
                "run_id": session.run_id,
                "adapter": session.adapter_name,
                "current_page_url": session.current_page_url,
                "page_title": session.page_title,
            },
        )

    async def list_sessions(self) -> dict:
        start = self._timer()
        sessions = [
            {
                "session_id": s.session_id,
                "run_id": s.run_id,
                "status": s.status.value,
                "adapter_name": s.adapter_name,
                "current_page_url": s.current_page_url,
                "artifacts_dir": s.artifacts_dir,
            }
            for s in self.session_manager.list_sessions()
        ]
        return success_response(
            message="sessions listed",
            duration_ms=self._duration_ms(start),
            data={"sessions": sessions, "count": len(sessions)},
        )

    async def close_session(self, session_id: str) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        await self.session_manager.close_session(session_id)
        return success_response(
            message="session closed",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
        )

    async def reset_session(self, session_id: str) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        await self.session_manager.reset_session(session_id)
        return success_response(
            message="session reset",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
        )

    async def login_agent(
        self, session_id: str, username: str, password: str, tenant: str | None = None
    ) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]
        result = await adapter.login_agent(session, username=username, password=password, tenant=tenant)
        return success_response(
            message=result.get("message", "login completed"),
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            warnings=result.get("warnings", []),
            data={"tenant": tenant},
        )

    async def wait_for_ready(self, session_id: str, timeout_ms: int = 30_000) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]
        result = await adapter.wait_for_ready(session, timeout_ms=timeout_ms)
        if not result.get("ok"):
            return failure_response(
                message=result.get("message", "app not ready"),
                error_code=ErrorCode.APP_NOT_READY,
                failure_category=FailureCategory.SESSION,
                retryable=True,
                likely_causes=[result.get("reason", "application bootstrap incomplete")],
                next_recommended_tools=["reset_session", "open_app"],
                duration_ms=self._duration_ms(start),
                session_id=session_id,
            )
        return success_response(
            message=result.get("message", "app ready"),
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data={"ready": True},
        )

    async def get_registration_status(self, session_id: str) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]
        snapshot = await adapter.get_registration_snapshot(session)
        return success_response(
            message="registration snapshot",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data=snapshot.model_dump(mode="json"),
            warnings=[snapshot.reason] if snapshot.reason else [],
        )

    async def wait_for_registration(
        self, session_id: str, expected: str = "registered", timeout_ms: int = 30_000
    ) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]
        snapshot = await adapter.wait_for_registration(session, expected=expected, timeout_ms=timeout_ms)
        if snapshot.state.value != expected:
            diagnosis = diagnose_registration(snapshot)
            artifacts = self.bundle_writer.collect(
                session=session,
                registration=snapshot.model_dump(mode="json"),
                environment={"generated_by": "wait_for_registration"},
            )
            return failure_response(
                message="registration did not reach expected state",
                error_code=ErrorCode.REGISTRATION_TIMEOUT,
                failure_category=FailureCategory.REGISTRATION,
                retryable=diagnosis.retryable,
                likely_causes=diagnosis.likely_causes,
                next_recommended_tools=diagnosis.next_recommended_tools,
                duration_ms=self._duration_ms(start),
                session_id=session_id,
                artifacts=artifacts,
                warnings=[snapshot.reason] if snapshot.reason else [],
                data={"observed": snapshot.model_dump(mode="json")},
            )
        return success_response(
            message="registration reached expected state",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data=snapshot.model_dump(mode="json"),
        )

    async def assert_registered(self, session_id: str, timeout_ms: int = 30_000) -> dict:
        return await self.wait_for_registration(session_id, expected="registered", timeout_ms=timeout_ms)

    async def wait_for_incoming_call(self, session_id: str, timeout_ms: int = 30_000) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]
        snapshot = await adapter.wait_for_incoming_call(session, timeout_ms=timeout_ms)
        if snapshot.state.value != "ringing":
            diagnosis = diagnose_incoming_call(snapshot)
            artifacts = self.bundle_writer.collect(
                session=session,
                active_session=snapshot.model_dump(mode="json"),
                environment={"generated_by": "wait_for_incoming_call"},
            )
            return failure_response(
                message="incoming call not detected",
                error_code=ErrorCode.INCOMING_CALL_TIMEOUT,
                failure_category=FailureCategory.CALL_CONTROL,
                retryable=diagnosis.retryable,
                likely_causes=diagnosis.likely_causes,
                next_recommended_tools=diagnosis.next_recommended_tools,
                duration_ms=self._duration_ms(start),
                session_id=session_id,
                artifacts=artifacts,
                warnings=[snapshot.reason] if snapshot.reason else [],
                data={"observed": snapshot.model_dump(mode="json")},
            )
        return success_response(
            message="incoming call detected",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data=snapshot.model_dump(mode="json"),
        )

    async def answer_call(self, session_id: str, timeout_ms: int = 15_000) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]
        call_snapshot = await adapter.answer_call(session, timeout_ms=timeout_ms)
        webrtc_snapshot = await adapter.get_peer_connection_summary(session)

        if call_snapshot.state.value != "connected":
            diagnosis = diagnose_answer_flow(call_snapshot, webrtc_snapshot)
            artifacts = self.bundle_writer.collect(
                session=session,
                active_session=call_snapshot.model_dump(mode="json"),
                webrtc=webrtc_snapshot.model_dump(mode="json"),
                environment={"generated_by": "answer_call", "timestamp": self._now()},
            )
            write_markdown_report(
                session,
                {
                    "summary": diagnosis.summary,
                    "likely_causes": diagnosis.likely_causes,
                    "session_id": session_id,
                },
            )
            return failure_response(
                message="answer did not become connected",
                error_code=ErrorCode.ANSWER_FLOW_FAILED,
                failure_category=FailureCategory.CALL_CONTROL,
                retryable=diagnosis.retryable,
                likely_causes=diagnosis.likely_causes,
                next_recommended_tools=diagnosis.next_recommended_tools,
                duration_ms=self._duration_ms(start),
                session_id=session_id,
                artifacts=artifacts,
                warnings=[call_snapshot.reason] if call_snapshot.reason else [],
                data={
                    "call": call_snapshot.model_dump(mode="json"),
                    "webrtc": webrtc_snapshot.model_dump(mode="json"),
                },
            )

        warnings = []
        if not webrtc_snapshot.peer_connection_present:
            warnings.append("No RTCPeerConnection found after connected state")
        if call_snapshot.ui_state and call_snapshot.store_state and call_snapshot.ui_state != call_snapshot.store_state:
            warnings.append("UI and store call state mismatch detected after answer")

        return success_response(
            message="call answered",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data={
                "call": call_snapshot.model_dump(mode="json"),
                "webrtc": webrtc_snapshot.model_dump(mode="json"),
            },
            warnings=warnings,
        )

    async def hangup_call(self, session_id: str, timeout_ms: int = 15_000) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]
        snapshot = await adapter.hangup_call(session, timeout_ms=timeout_ms)
        return success_response(
            message="call hangup executed",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data=snapshot.model_dump(mode="json"),
        )

    async def get_ui_call_state(self, session_id: str) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]
        state = await adapter.get_ui_call_state(session)
        return success_response(
            message="ui call state",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data=state,
            warnings=[state["reason"]] if state.get("reason") else [],
        )

    async def get_active_session_snapshot(self, session_id: str) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]
        snapshot = await adapter.get_active_session_snapshot(session)
        return success_response(
            message="active session snapshot",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data=snapshot.model_dump(mode="json"),
            warnings=[snapshot.reason] if snapshot.reason else [],
        )

    async def get_store_snapshot(self, session_id: str) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]
        snapshot = await adapter.get_store_snapshot(session)
        return success_response(
            message="store snapshot",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data=snapshot,
            warnings=[snapshot["reason"]] if snapshot.get("reason") else [],
        )

    async def get_peer_connection_summary(self, session_id: str) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]
        snapshot = await adapter.get_peer_connection_summary(session)
        return success_response(
            message="peer connection summary",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data=snapshot.model_dump(mode="json"),
            warnings=[snapshot.reason] if snapshot.reason else [],
        )

    async def get_webrtc_stats(self, session_id: str) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]
        snapshot = await adapter.get_peer_connection_summary(session)
        stats = {
            "peer_connection_present": snapshot.peer_connection_present,
            "inbound_rtp_audio_packets": snapshot.inbound_rtp_audio_packets,
            "outbound_rtp_audio_packets": snapshot.outbound_rtp_audio_packets,
            "connection_state": snapshot.connection_state,
            "timestamp": snapshot.timestamp,
        }
        return success_response(
            message="webrtc stats",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data=stats,
            warnings=[snapshot.reason] if snapshot.reason else [],
        )

    async def collect_debug_bundle(self, session_id: str) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]

        registration = (await adapter.get_registration_snapshot(session)).model_dump(mode="json")
        active = (await adapter.get_active_session_snapshot(session)).model_dump(mode="json")
        webrtc = (await adapter.get_peer_connection_summary(session)).model_dump(mode="json")
        environment = {
            "generated_by": "collect_debug_bundle",
            "session_environment_classification": session.environment_classification,
        }

        artifacts = self.bundle_writer.collect(
            session=session,
            registration=registration,
            active_session=active,
            webrtc=webrtc,
            environment=environment,
        )
        diag_artifacts, diag_warnings, diag_data = await self._collect_browser_diagnostics_bundle(
            session=session,
            scenario_id="collect-debug-bundle",
            fault_type="manual_collection",
            injection_point="collect_debug_bundle",
            status="ok",
            failure_classification="diagnostic",
        )
        report_path = write_markdown_report(
            session,
            {
                "registration_state": registration.get("state"),
                "call_state": active.get("state"),
                "peer_connection_present": webrtc.get("peer_connection_present"),
            },
        )

        return success_response(
            message="debug bundle collected",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            artifacts=artifacts + diag_artifacts,
            warnings=diag_warnings,
            data={
                "artifacts_dir": session.artifacts_dir,
                "report_path": report_path,
                "browser_diagnostics": diag_data,
            },
        )

    async def get_environment_snapshot(self, session_id: str) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)

        payload = self.environment_inspector.get_snapshot(session)
        return success_response(
            message="environment snapshot",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data=payload,
        )

    async def screenshot(self, session_id: str, label: str = "manual-capture") -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)

        screenshot_dir = Path(session.artifacts_dir) / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{label}.png"
        path = screenshot_dir / filename
        warnings: list[str] = []
        if session.driver is None:
            png_bytes = bytes.fromhex(
                "89504E470D0A1A0A0000000D4948445200000001000000010802000000907753DE"
                "0000000C4944415408D763F8FFFF3F0005FE02FEA7DDA2B50000000049454E44AE426082"
            )
            path.write_bytes(png_bytes)
            warnings.append("active browser page unavailable; wrote placeholder screenshot artifact")
        else:
            captured = await session.driver.screenshot(str(path))
            if not captured:
                return failure_response(
                    message="screenshot capture returned false",
                    error_code=ErrorCode.BROWSER_SESSION_BROKEN,
                    failure_category=FailureCategory.SESSION,
                    retryable=True,
                    likely_causes=["page is unavailable", "browser context closed unexpectedly"],
                    next_recommended_tools=["reset_session", "open_app"],
                    duration_ms=self._duration_ms(start),
                    session_id=session_id,
                )
        artifact = {
            "type": "screenshot",
            "label": label,
            "path": str(path),
            "redacted": self.settings.redact,
            "created_at": self._now(),
        }
        return success_response(
            message="screenshot captured",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data={"path": str(path), "label": label},
            artifacts=[artifact],
            warnings=warnings,
        )

    async def collect_browser_logs(self, session_id: str) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        artifacts, warnings, data = await self._collect_browser_diagnostics_bundle(
            session=session,
            scenario_id="collect-browser-logs",
            fault_type="manual_collection",
            injection_point="collect_browser_logs",
            status="ok",
            failure_classification="diagnostic",
        )
        return success_response(
            message="browser logs collected",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            artifacts=artifacts,
            warnings=warnings,
            data=data,
        )

    async def diagnose_registration_failure(self, session_id: str) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]
        snapshot = await adapter.get_registration_snapshot(session)
        diagnosis = diagnose_registration(snapshot)
        return success_response(
            message="registration diagnosis",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data=diagnosis.model_dump(mode="json"),
        )

    async def diagnose_incoming_call_failure(self, session_id: str) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]
        snapshot = await adapter.wait_for_incoming_call(session, timeout_ms=1)
        diagnosis = diagnose_incoming_call(snapshot)
        return success_response(
            message="incoming call diagnosis",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data=diagnosis.model_dump(mode="json"),
        )

    async def diagnose_answer_failure(self, session_id: str) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]
        call_snapshot = await adapter.get_active_session_snapshot(session)
        webrtc_snapshot = await adapter.get_peer_connection_summary(session)
        diagnosis = diagnose_answer_flow(call_snapshot, webrtc_snapshot)
        return success_response(
            message="answer flow diagnosis",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data=diagnosis.model_dump(mode="json"),
        )

    async def diagnose_one_way_audio(self, session_id: str) -> dict:
        start = self._timer()
        session = self.session_manager.get(session_id)
        if session is None:
            return self._session_missing(session_id, start)
        adapter = self._adapter_for_session[session_id]
        snapshot = await adapter.get_peer_connection_summary(session)
        likely_causes: list[str] = []
        severity = "medium"
        if not snapshot.peer_connection_present:
            likely_causes.append("peer connection is missing; media path was not established")
            severity = "high"
        elif snapshot.remote_audio_tracks == 0:
            likely_causes.append("remote audio tracks are missing while call may be connected")
            severity = "high"
        elif snapshot.inbound_rtp_audio_packets in (None, 0):
            likely_causes.append("inbound RTP audio counters are absent or not moving")
        else:
            likely_causes.append("no one-way-audio signal detected from available browser metrics")

        return success_response(
            message="one-way-audio diagnosis",
            duration_ms=self._duration_ms(start),
            session_id=session_id,
            data={
                "summary": "One-way audio diagnosis from browser-side media signals",
                "severity": severity,
                "likely_causes": likely_causes,
                "peer_connection_present": snapshot.peer_connection_present,
                "remote_audio_tracks": snapshot.remote_audio_tracks,
                "inbound_rtp_audio_packets": snapshot.inbound_rtp_audio_packets,
                "next_recommended_tools": [
                    "get_peer_connection_summary",
                    "get_webrtc_stats",
                    "collect_debug_bundle",
                ],
            },
            warnings=[snapshot.reason] if snapshot.reason else [],
        )
