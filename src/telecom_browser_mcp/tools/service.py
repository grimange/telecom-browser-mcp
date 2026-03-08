from __future__ import annotations

import asyncio
from typing import Any

from telecom_browser_mcp.adapters.apntalk import APNTalkAdapter
from telecom_browser_mcp.adapters.fake_dialer import FakeDialerAdapter
from telecom_browser_mcp.adapters.registry import AdapterRegistry
from telecom_browser_mcp.contracts import CANONICAL_TOOL_INPUT_MODELS
from telecom_browser_mcp.contracts.envelope import as_dict
from telecom_browser_mcp.diagnostics.engine import DiagnosticsEngine
from telecom_browser_mcp.errors import codes
from telecom_browser_mcp.evidence.bundle import EvidenceCollector
from telecom_browser_mcp.inspectors.session_inspector import SessionInspector
from telecom_browser_mcp.inspectors.webrtc_inspector import WebRTCInspector
from telecom_browser_mcp.models.common import DiagnosticItem, ToolError, ToolResponse
from telecom_browser_mcp.models.tools import (
    CollectDebugBundleInput,
    EmptyInput,
    LoginInput,
    OpenAppInput,
    SessionInput,
    TimeoutInput,
)
from telecom_browser_mcp.sessions.manager import SessionManager, SessionRuntime


class ToolService:
    def __init__(self, operation_lock_timeout_ms: int = 5000) -> None:
        self.sessions = SessionManager()
        self.adapters = AdapterRegistry()
        self.adapters.register(APNTalkAdapter, domains=["app.apntalk.com", "apntalk.com"])
        self.adapters.register(FakeDialerAdapter, domains=["fake-dialer.local"])
        self.session_inspector = SessionInspector()
        self.webrtc_inspector = WebRTCInspector()
        self.evidence = EvidenceCollector()
        self.diagnostics = DiagnosticsEngine()
        self._operation_lock_timeout_ms = operation_lock_timeout_ms

    def _ok(
        self,
        tool: str,
        data: dict[str, Any],
        session_id: str | None = None,
        adapter_id: str | None = None,
        diagnostics: list[DiagnosticItem] | None = None,
        artifacts: list | None = None,
    ) -> dict:
        return as_dict(
            ToolResponse(
                ok=True,
                tool=tool,
                session_id=session_id,
                data=data,
                diagnostics=diagnostics or [],
                artifacts=artifacts or [],
                meta={"contract_version": "v1", "adapter_id": adapter_id},
            )
        )

    def _err(
        self,
        tool: str,
        code: str,
        message: str,
        classification: str = "unknown",
        retryable: bool = False,
        session_id: str | None = None,
        diagnostics: list | None = None,
        artifacts: list | None = None,
    ) -> dict:
        return as_dict(
            ToolResponse(
                ok=False,
                tool=tool,
                session_id=session_id,
                data={},
                error=ToolError(
                    code=code,
                    message=message,
                    classification=classification,
                    retryable=retryable,
                ),
                diagnostics=diagnostics or [],
                artifacts=artifacts or [],
                meta={"contract_version": "v1"},
            )
        )

    def _require_runtime(self, tool: str, session_id: str) -> tuple[SessionRuntime | None, dict | None]:
        runtime = self.sessions.get(session_id)
        if runtime is None:
            return None, self._err(
                tool,
                codes.ERROR_SESSION_NOT_FOUND,
                f"session not found: {session_id}",
                session_id=session_id,
            )
        if runtime.model.lifecycle_state in {"closed", "closing"}:
            return None, self._err(
                tool,
                codes.ERROR_SESSION_CLOSED,
                f"session is not active: {session_id}",
                classification="session_not_ready",
                session_id=session_id,
                diagnostics=[
                    DiagnosticItem(
                        code="session_not_ready",
                        classification="session_not_ready",
                        message=f"session lifecycle_state={runtime.model.lifecycle_state}",
                        confidence="high",
                    )
                ],
            )
        return runtime, None

    def _session_state_diagnostics(self, runtime: SessionRuntime) -> list[DiagnosticItem]:
        diagnostics = [
            DiagnosticItem(
                code="session_state",
                classification="session_state",
                message=f"lifecycle_state={runtime.model.lifecycle_state}",
                confidence="high",
            ),
            DiagnosticItem(
                code="browser_state",
                classification="session_not_ready",
                message=f"browser_open={runtime.model.telecom.browser_open}",
                confidence="high",
            ),
        ]
        if runtime.model.browser_launch_error:
            diagnostics.append(
                DiagnosticItem(
                    code="browser_launch_error",
                    classification=runtime.model.browser_launch_error_classification or "unknown",
                    message=runtime.model.browser_launch_error,
                    confidence="high",
                )
            )
        return diagnostics

    def _require_browser_page(self, tool: str, runtime: SessionRuntime) -> dict | None:
        if runtime.browser.page is None:
            self.sessions.mark_broken(runtime.model.session_id)
            message = runtime.model.browser_launch_error or "browser page is unavailable"
            classification = runtime.model.browser_launch_error_classification or "session_not_ready"
            return self._err(
                tool,
                codes.ERROR_SESSION_BROKEN,
                message,
                classification=classification,
                retryable=True,
                session_id=runtime.model.session_id,
                diagnostics=self._session_state_diagnostics(runtime),
            )
        return None

    async def _acquire_operation_lock(self, tool: str, runtime: SessionRuntime) -> dict | None:
        try:
            await asyncio.wait_for(
                runtime.operation_lock.acquire(),
                timeout=max(self._operation_lock_timeout_ms, 1) / 1000,
            )
            return None
        except TimeoutError:
            return self._err(
                tool,
                codes.ERROR_NOT_READY,
                "session is busy with another operation",
                classification="session_busy",
                retryable=True,
                session_id=runtime.model.session_id,
                diagnostics=[
                    DiagnosticItem(
                        code="session_busy",
                        classification="session_busy",
                        message=(
                            "operation lock acquisition timed out "
                            f"after {self._operation_lock_timeout_ms}ms"
                        ),
                        confidence="high",
                    )
                ],
            )

    async def health(self, payload: dict[str, Any]) -> dict:
        tool = "health"
        try:
            EmptyInput.model_validate(payload)
        except Exception as exc:
            return self._err(tool, codes.ERROR_INVALID_INPUT, str(exc))
        return self._ok(tool, {"service": "telecom-browser-mcp", "status": "ok"})

    async def capabilities(self, payload: dict[str, Any]) -> dict:
        tool = "capabilities"
        try:
            EmptyInput.model_validate(payload)
        except Exception as exc:
            return self._err(tool, codes.ERROR_INVALID_INPUT, str(exc))
        return self._ok(
            tool,
            {
                "tools": list(CANONICAL_TOOL_INPUT_MODELS.keys()),
                "contract_version": "v1",
            },
        )

    async def open_app(self, payload: dict[str, Any]) -> dict:
        tool = "open_app"
        try:
            req = OpenAppInput.model_validate(payload)
        except Exception as exc:
            return self._err(tool, codes.ERROR_INVALID_INPUT, str(exc), classification="unknown")

        try:
            adapter, source, confidence = self.adapters.resolve(req.target_url, req.adapter_id)
        except KeyError:
            return self._err(
                tool,
                codes.ERROR_ADAPTER_NOT_FOUND,
                f"adapter not found: {req.adapter_id}",
                classification="adapter_not_supported",
            )

        runtime = await self.sessions.create(
            target_url=req.target_url,
            adapter=adapter,
            headless=req.headless,
        )

        diagnostics: list[DiagnosticItem] = []
        if not runtime.browser.browser_open:
            diagnostics.append(
                DiagnosticItem(
                    code="session_not_ready",
                    classification=runtime.model.browser_launch_error_classification or "session_not_ready",
                    message=runtime.model.browser_launch_error or "browser launch blocked by environment",
                    confidence="high",
                )
            )
            diagnostics.extend(self._session_state_diagnostics(runtime))

        ready_for_actions = runtime.browser.browser_open and runtime.browser.page is not None
        return self._ok(
            tool,
            {
                "session_id": runtime.model.session_id,
                "resolved_adapter_id": adapter.adapter_id,
                "adapter_resolution_source": source,
                "adapter_resolution_confidence": confidence,
                "capabilities": runtime.model.capabilities.model_dump(mode="json"),
                "lifecycle_state": runtime.model.lifecycle_state,
                "ready_for_actions": ready_for_actions,
            },
            session_id=runtime.model.session_id,
            adapter_id=adapter.adapter_id,
            diagnostics=diagnostics,
        )

    async def list_sessions(self, payload: dict[str, Any]) -> dict:
        tool = "list_sessions"
        try:
            EmptyInput.model_validate(payload)
        except Exception as exc:
            return self._err(tool, codes.ERROR_INVALID_INPUT, str(exc))
        sessions = [s.model_dump(mode="json") for s in self.sessions.list()]
        return self._ok(tool, {"count": len(sessions), "sessions": sessions})

    async def close_session(self, payload: dict[str, Any]) -> dict:
        tool = "close_session"
        try:
            req = SessionInput.model_validate(payload)
        except Exception as exc:
            return self._err(tool, codes.ERROR_INVALID_INPUT, str(exc))
        runtime, error_response = self._require_runtime(tool, req.session_id)
        if error_response is not None:
            return error_response

        lock_error = await self._acquire_operation_lock(tool, runtime)
        if lock_error is not None:
            return lock_error
        try:
            closed = await self.sessions.close(req.session_id)
        finally:
            runtime.operation_lock.release()
        if not closed:
            return self._err(
                tool,
                codes.ERROR_SESSION_NOT_FOUND,
                f"session not found: {req.session_id}",
                classification="session_not_ready",
            )
        return self._ok(tool, {"closed": True}, session_id=req.session_id)

    async def login_agent(self, payload: dict[str, Any]) -> dict:
        tool = "login_agent"
        try:
            req = LoginInput.model_validate(payload)
        except Exception as exc:
            return self._err(tool, codes.ERROR_INVALID_INPUT, str(exc))

        runtime, error_response = self._require_runtime(tool, req.session_id)
        if error_response is not None:
            return error_response
        lock_error = await self._acquire_operation_lock(tool, runtime)
        if lock_error is not None:
            return lock_error
        try:
            browser_error = self._require_browser_page(tool, runtime)
            if browser_error is not None:
                return browser_error

            ok, message = await runtime.adapter.login(
                runtime.model.telecom,
                runtime.browser.page,
                req.credentials,
                req.timeout_ms,
            )
            if not ok:
                return self._err(
                    tool,
                    codes.ERROR_ADAPTER_UNSUPPORTED,
                    message,
                    classification="adapter_not_supported",
                    session_id=req.session_id,
                    diagnostics=self._session_state_diagnostics(runtime),
                )
            runtime.model.telecom.login_complete = True
            return self._ok(
                tool,
                {"login_complete": True, "message": message},
                session_id=req.session_id,
                adapter_id=runtime.adapter.adapter_id,
            )
        finally:
            runtime.operation_lock.release()

    async def wait_for_ready(self, payload: dict[str, Any]) -> dict:
        return await self._wait_state("wait_for_ready", payload)

    async def wait_for_registration(self, payload: dict[str, Any]) -> dict:
        return await self._wait_state("wait_for_registration", payload)

    async def wait_for_incoming_call(self, payload: dict[str, Any]) -> dict:
        return await self._wait_state("wait_for_incoming_call", payload)

    async def _wait_state(self, tool: str, payload: dict[str, Any]) -> dict:
        try:
            req = TimeoutInput.model_validate(payload)
        except Exception as exc:
            return self._err(tool, codes.ERROR_INVALID_INPUT, str(exc))

        runtime, error_response = self._require_runtime(tool, req.session_id)
        if error_response is not None:
            return error_response
        lock_error = await self._acquire_operation_lock(tool, runtime)
        if lock_error is not None:
            return lock_error
        try:
            browser_error = self._require_browser_page(tool, runtime)
            if browser_error is not None:
                return browser_error

            if tool == "wait_for_ready":
                ok, message = await runtime.adapter.wait_for_ready(
                    runtime.model.telecom,
                    runtime.browser.page,
                    req.timeout_ms,
                )
                if ok:
                    runtime.model.telecom.ui_ready = True
                    return self._ok(
                        tool,
                        {"ui_ready": True, "message": message},
                        session_id=req.session_id,
                        adapter_id=runtime.adapter.adapter_id,
                    )
                return self._err(
                    tool,
                    codes.ERROR_TIMEOUT,
                    message,
                    classification="session_not_ready",
                    retryable=True,
                    session_id=req.session_id,
                    diagnostics=self._session_state_diagnostics(runtime),
                )

            if tool == "wait_for_registration":
                ok, message = await runtime.adapter.wait_for_registration(
                    runtime.model.telecom,
                    runtime.browser.page,
                    req.timeout_ms,
                )
                if ok:
                    runtime.model.telecom.registration_state = "registered"
                    return self._ok(
                        tool,
                        {"registration_state": "registered", "message": message},
                        session_id=req.session_id,
                        adapter_id=runtime.adapter.adapter_id,
                    )
                runtime.model.telecom.registration_state = "not_detected"
                return self._err(
                    tool,
                    codes.ERROR_REGISTRATION_NOT_DETECTED,
                    message,
                    classification="registration_missing",
                    retryable=True,
                    session_id=req.session_id,
                    diagnostics=self._session_state_diagnostics(runtime),
                )

            ok, message = await runtime.adapter.wait_for_incoming_call(
                runtime.model.telecom,
                runtime.browser.page,
                req.timeout_ms,
            )
            if ok:
                runtime.model.telecom.incoming_call_state = "ringing"
                return self._ok(
                    tool,
                    {"incoming_call_state": "ringing", "message": message},
                    session_id=req.session_id,
                    adapter_id=runtime.adapter.adapter_id,
                )
            runtime.model.telecom.incoming_call_state = "not_detected"
            return self._err(
                tool,
                codes.ERROR_INCOMING_CALL_NOT_DETECTED,
                message,
                classification="incoming_call_not_present",
                retryable=True,
                session_id=req.session_id,
                diagnostics=self._session_state_diagnostics(runtime),
            )
        finally:
            runtime.operation_lock.release()

    async def answer_call(self, payload: dict[str, Any]) -> dict:
        tool = "answer_call"
        try:
            req = TimeoutInput.model_validate(payload)
        except Exception as exc:
            return self._err(tool, codes.ERROR_INVALID_INPUT, str(exc))

        runtime, error_response = self._require_runtime(tool, req.session_id)
        if error_response is not None:
            return error_response
        lock_error = await self._acquire_operation_lock(tool, runtime)
        if lock_error is not None:
            return lock_error
        try:
            browser_error = self._require_browser_page(tool, runtime)
            if browser_error is not None:
                return browser_error

            ok, message = await runtime.adapter.answer_call(
                runtime.model.telecom,
                runtime.browser.page,
                req.timeout_ms,
            )
            if ok:
                runtime.model.telecom.active_call_state = "connected"
                return self._ok(
                    tool,
                    {"active_call_state": "connected", "message": message},
                    session_id=req.session_id,
                    adapter_id=runtime.adapter.adapter_id,
                )

            runtime.model.telecom.active_call_state = "failed"
            diagnostics = self.diagnostics.diagnose_answer_failure(runtime)
            bundle_path, artifacts = await self.evidence.collect(
                runtime,
                trigger_tool=tool,
                reason=message,
                diagnostics=[d.model_dump(mode="json") for d in diagnostics],
            )
            err = self._err(
                tool,
                codes.ERROR_ACTION_FAILED,
                message,
                classification="answer_action_failed",
                retryable=False,
                session_id=req.session_id,
                diagnostics=diagnostics,
                artifacts=artifacts,
            )
            err["data"] = {"bundle_path": bundle_path}
            return err
        finally:
            runtime.operation_lock.release()

    async def get_active_session_snapshot(self, payload: dict[str, Any]) -> dict:
        tool = "get_active_session_snapshot"
        try:
            req = SessionInput.model_validate(payload)
        except Exception as exc:
            return self._err(tool, codes.ERROR_INVALID_INPUT, str(exc))

        runtime, error_response = self._require_runtime(tool, req.session_id)
        if error_response is not None:
            return error_response
        return self._ok(
            tool,
            self.session_inspector.snapshot(runtime),
            session_id=req.session_id,
            adapter_id=runtime.adapter.adapter_id,
        )

    async def get_peer_connection_summary(self, payload: dict[str, Any]) -> dict:
        tool = "get_peer_connection_summary"
        try:
            req = SessionInput.model_validate(payload)
        except Exception as exc:
            return self._err(tool, codes.ERROR_INVALID_INPUT, str(exc))

        runtime, error_response = self._require_runtime(tool, req.session_id)
        if error_response is not None:
            return error_response
        lock_error = await self._acquire_operation_lock(tool, runtime)
        if lock_error is not None:
            return lock_error
        try:
            browser_error = self._require_browser_page(tool, runtime)
            if browser_error is not None:
                return browser_error

            summary = await self.webrtc_inspector.summary(runtime)
            return self._ok(
                tool,
                summary,
                session_id=req.session_id,
                adapter_id=runtime.adapter.adapter_id,
            )
        finally:
            runtime.operation_lock.release()

    async def collect_debug_bundle(self, payload: dict[str, Any]) -> dict:
        tool = "collect_debug_bundle"
        try:
            req = CollectDebugBundleInput.model_validate(payload)
        except Exception as exc:
            return self._err(tool, codes.ERROR_INVALID_INPUT, str(exc))

        runtime, error_response = self._require_runtime(tool, req.session_id)
        if error_response is not None:
            return error_response

        lock_error = await self._acquire_operation_lock(tool, runtime)
        if lock_error is not None:
            return lock_error
        try:
            bundle_path, artifacts = await self.evidence.collect(
                runtime,
                trigger_tool=tool,
                reason=req.reason,
                diagnostics=[],
            )
            result = self._ok(
                tool,
                {"bundle_path": bundle_path},
                session_id=req.session_id,
                adapter_id=runtime.adapter.adapter_id,
            )
            result["artifacts"] = [a.model_dump(mode="json") for a in artifacts]
            return result
        finally:
            runtime.operation_lock.release()

    async def diagnose_answer_failure(self, payload: dict[str, Any]) -> dict:
        tool = "diagnose_answer_failure"
        try:
            req = SessionInput.model_validate(payload)
        except Exception as exc:
            return self._err(tool, codes.ERROR_INVALID_INPUT, str(exc))

        runtime, error_response = self._require_runtime(tool, req.session_id)
        if error_response is not None:
            return error_response
        diagnostics = self.diagnostics.diagnose_answer_failure(runtime)
        response = self._ok(
            tool,
            {"diagnosis": "answer_failure_analysis_complete"},
            session_id=req.session_id,
            adapter_id=runtime.adapter.adapter_id,
        )
        response["diagnostics"] = [d.model_dump(mode="json") for d in diagnostics]
        return response
