from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class BrowserDiagnosticsCollector:
    """Capture browser boundary signals and emit normalized diagnostics bundles."""

    def __init__(self, *, trace_enabled: bool = True) -> None:
        self.trace_enabled = trace_enabled
        self.console_events: list[dict[str, Any]] = []
        self.page_errors: list[dict[str, Any]] = []
        self.network_requests: list[dict[str, Any]] = []
        self.network_responses: list[dict[str, Any]] = []
        self.network_failures: list[dict[str, Any]] = []
        self.collection_gaps: list[str] = []
        self.timing_markers: list[dict[str, str]] = []
        self._trace_started = False
        self._context: Any | None = None
        self._page: Any | None = None

    async def attach(self, *, context: Any | None, page: Any | None) -> None:
        self._context = context
        self._page = page
        self.mark("collector_attached")

        if context is None:
            self.collection_gaps.append("context unavailable; request/response tracing not attached")
        else:
            self._attach_context_events(context)
            await self._start_trace(context)

        if page is None:
            self.collection_gaps.append("page unavailable; console and pageerror listeners not attached")
        else:
            self._attach_page_events(page)

    def mark(self, name: str) -> None:
        self.timing_markers.append(
            {"name": name, "timestamp": datetime.now(timezone.utc).isoformat()}
        )

    async def write_bundle(
        self,
        *,
        base_dir: str,
        run_id: str,
        scenario_id: str,
        session_id: str,
        fault_type: str,
        injection_point: str,
        status: str,
        failure_classification: str,
        attempted_selector: str | None = None,
    ) -> dict[str, Any]:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        bundle_dir = Path(base_dir) / "browser-diagnostics" / timestamp / scenario_id
        bundle_dir.mkdir(parents=True, exist_ok=True)

        self.mark("bundle_write_started")

        console_path = bundle_dir / "console.json"
        page_errors_path = bundle_dir / "page-errors.json"
        network_path = bundle_dir / "network.json"
        metadata_path = bundle_dir / "metadata.json"
        manifest_path = bundle_dir / "manifest.json"
        summary_path = bundle_dir / "summary.md"
        dom_path = bundle_dir / "dom.html"
        screenshot_path = bundle_dir / "screenshot.png"
        trace_path = bundle_dir / "trace.zip"

        self._write_json(console_path, {"events": self.console_events})
        self._write_json(page_errors_path, {"events": self.page_errors})
        self._write_json(
            network_path,
            {
                "requests": self.network_requests,
                "responses": self.network_responses,
                "failures": self.network_failures,
            },
        )

        metadata_payload = self._build_metadata(
            run_id=run_id,
            session_id=session_id,
            scenario_id=scenario_id,
            fault_type=fault_type,
            injection_point=injection_point,
            status=status,
            failure_classification=failure_classification,
            attempted_selector=attempted_selector,
        )
        self._write_json(metadata_path, metadata_payload)

        dom_ok = await self._capture_dom(dom_path)
        screenshot_ok = await self._capture_screenshot(screenshot_path)
        trace_ok = await self._stop_trace(trace_path)

        manifest = {
            "run_id": run_id,
            "scenario_id": scenario_id,
            "session_id": session_id,
            "page_id": metadata_payload["page_id"],
            "context_id": metadata_payload["context_id"],
            "fault_type": fault_type,
            "injection_point": injection_point,
            "status": status,
            "failure_classification": failure_classification,
            "timestamps": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "timing_markers": self.timing_markers,
            },
            "artifact_paths": {
                "manifest": str(manifest_path),
                "summary": str(summary_path),
                "console": str(console_path),
                "network": str(network_path),
                "page_errors": str(page_errors_path),
                "metadata": str(metadata_path),
                "screenshot": str(screenshot_path) if screenshot_ok else None,
                "dom_snapshot": str(dom_path) if dom_ok else None,
                "trace": str(trace_path) if trace_ok else None,
            },
            "collection_gaps": self.collection_gaps,
        }
        self._write_json(manifest_path, manifest)
        summary_path.write_text(self._render_summary(manifest), encoding="utf-8")

        self.mark("bundle_write_completed")
        return {
            "bundle_dir": str(bundle_dir),
            "manifest_path": str(manifest_path),
            "summary_path": str(summary_path),
            "collection_gaps": self.collection_gaps,
            "artifact_paths": manifest["artifact_paths"],
        }

    def _attach_page_events(self, page: Any) -> None:
        if not hasattr(page, "on"):
            self.collection_gaps.append("page listener API unavailable")
            return
        page.on("console", self._on_console)
        page.on("pageerror", self._on_pageerror)

    def _attach_context_events(self, context: Any) -> None:
        if not hasattr(context, "on"):
            self.collection_gaps.append("context listener API unavailable")
            return
        context.on("request", self._on_request)
        context.on("response", self._on_response)
        context.on("requestfailed", self._on_request_failed)

    async def _start_trace(self, context: Any) -> None:
        if not self.trace_enabled:
            self.collection_gaps.append("trace capture disabled by configuration")
            return
        tracing = getattr(context, "tracing", None)
        if tracing is None or not hasattr(tracing, "start"):
            self.collection_gaps.append("trace API unavailable on context")
            return
        try:
            await tracing.start(screenshots=True, snapshots=True, sources=True)
            self._trace_started = True
            self.mark("trace_started")
        except Exception as exc:
            self.collection_gaps.append(f"trace start failed: {exc}")

    async def _stop_trace(self, trace_path: Path) -> bool:
        if not self._trace_started:
            return False
        context = self._context
        tracing = getattr(context, "tracing", None) if context is not None else None
        if tracing is None or not hasattr(tracing, "stop"):
            self.collection_gaps.append("trace stop unavailable after trace start")
            return False
        try:
            await tracing.stop(path=str(trace_path))
            self.mark("trace_stopped")
            return True
        except Exception as exc:
            self.collection_gaps.append(f"trace stop failed: {exc}")
            return False

    async def _capture_screenshot(self, screenshot_path: Path) -> bool:
        page = self._page
        if page is None:
            self.collection_gaps.append("screenshot skipped: page unavailable")
            return False
        try:
            if hasattr(page, "is_closed") and page.is_closed():
                self.collection_gaps.append("screenshot skipped: page already closed")
                return False
            await page.screenshot(path=str(screenshot_path))
            return True
        except Exception as exc:
            self.collection_gaps.append(f"screenshot capture failed: {exc}")
            return False

    async def _capture_dom(self, dom_path: Path) -> bool:
        page = self._page
        if page is None:
            self.collection_gaps.append("dom snapshot skipped: page unavailable")
            return False
        try:
            if hasattr(page, "is_closed") and page.is_closed():
                self.collection_gaps.append("dom snapshot skipped: page already closed")
                return False
            content = await page.content()
            dom_path.write_text(content, encoding="utf-8")
            return True
        except Exception as exc:
            self.collection_gaps.append(f"dom snapshot capture failed: {exc}")
            return False

    def _build_metadata(
        self,
        *,
        run_id: str,
        session_id: str,
        scenario_id: str,
        fault_type: str,
        injection_point: str,
        status: str,
        failure_classification: str,
        attempted_selector: str | None,
    ) -> dict[str, Any]:
        page = self._page
        context = self._context
        url: str | None = None
        title: str | None = None
        if page is not None:
            url = getattr(page, "url", None)
            title = getattr(page, "_last_title", None)
        return {
            "run_id": run_id,
            "session_id": session_id,
            "scenario_id": scenario_id,
            "fault_type": fault_type,
            "injection_point": injection_point,
            "status": status,
            "failure_classification": failure_classification,
            "attempted_selector": attempted_selector,
            "context_id": str(id(context)) if context is not None else None,
            "page_id": str(id(page)) if page is not None else None,
            "page_url": url,
            "page_title": title,
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    @staticmethod
    def _render_summary(manifest: dict[str, Any]) -> str:
        gaps = manifest.get("collection_gaps", [])
        lines = [
            "# Browser Diagnostics Bundle",
            "",
            f"- run_id: {manifest['run_id']}",
            f"- scenario_id: {manifest['scenario_id']}",
            f"- session_id: {manifest['session_id']}",
            f"- fault_type: {manifest['fault_type']}",
            f"- injection_point: {manifest['injection_point']}",
            f"- status: {manifest['status']}",
            f"- failure_classification: {manifest['failure_classification']}",
            "",
            "## Collection Gaps",
            "",
        ]
        if not gaps:
            lines.append("- none")
        else:
            for gap in gaps:
                lines.append(f"- {gap}")
        lines.append("")
        return "\n".join(lines)

    def _on_console(self, message: Any) -> None:
        level = _safe_get(message, "type")
        text = _safe_get(message, "text")
        location = _safe_get(message, "location")
        self.console_events.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": level,
                "text": text,
                "location": location,
            }
        )

    def _on_pageerror(self, error: Any) -> None:
        self.page_errors.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": str(error),
            }
        )

    def _on_request(self, request: Any) -> None:
        self.network_requests.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "url": getattr(request, "url", None),
                "method": getattr(request, "method", None),
                "resource_type": _safe_get(request, "resource_type"),
            }
        )

    def _on_response(self, response: Any) -> None:
        request = getattr(response, "request", None)
        request_url = getattr(request, "url", None) if request is not None else None
        self.network_responses.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "url": getattr(response, "url", None),
                "status": _safe_get(response, "status"),
                "ok": _safe_get(response, "ok"),
                "request_url": request_url,
            }
        )

    def _on_request_failed(self, request: Any) -> None:
        failure = _safe_get(request, "failure")
        self.network_failures.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "url": getattr(request, "url", None),
                "method": getattr(request, "method", None),
                "failure": failure,
            }
        )


def _safe_get(obj: Any, attr: str) -> Any:
    value = getattr(obj, attr, None)
    if callable(value):
        try:
            return value()
        except Exception:
            return None
    return value
