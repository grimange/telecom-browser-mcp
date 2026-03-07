from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from telecom_browser_mcp.browser.diagnostics import BrowserDiagnosticsCollector


class FakeTracing:
    def __init__(self) -> None:
        self.started = False

    async def start(self, **kwargs) -> None:
        _ = kwargs
        self.started = True

    async def stop(self, path: str) -> None:
        if not self.started:
            raise RuntimeError("trace was never started")
        Path(path).write_bytes(b"trace")


class FakeContext:
    def __init__(self) -> None:
        self._handlers: dict[str, list] = {}
        self.tracing = FakeTracing()

    def on(self, event: str, callback) -> None:
        self._handlers.setdefault(event, []).append(callback)

    def emit(self, event: str, payload) -> None:
        for callback in self._handlers.get(event, []):
            callback(payload)


class FakePage:
    def __init__(self, *, closed: bool = False) -> None:
        self._handlers: dict[str, list] = {}
        self._closed = closed
        self.url = "http://fixture.local/diagnostics"
        self._last_title = "Diagnostics Fixture"

    def on(self, event: str, callback) -> None:
        self._handlers.setdefault(event, []).append(callback)

    def emit(self, event: str, payload) -> None:
        for callback in self._handlers.get(event, []):
            callback(payload)

    async def screenshot(self, path: str) -> None:
        if self._closed:
            raise RuntimeError("page closed")
        Path(path).write_bytes(b"png")

    async def content(self) -> str:
        if self._closed:
            raise RuntimeError("page closed")
        return "<html><body><h1>dom</h1></body></html>"

    def is_closed(self) -> bool:
        return self._closed


@pytest.mark.asyncio
async def test_console_pageerror_network_and_manifest_capture(tmp_path) -> None:
    collector = BrowserDiagnosticsCollector(trace_enabled=True)
    context = FakeContext()
    page = FakePage()
    await collector.attach(context=context, page=page)

    page.emit("console", SimpleNamespace(type=lambda: "error", text=lambda: "boom", location=lambda: {}))
    page.emit("pageerror", RuntimeError("fixture-page-error"))
    context.emit(
        "request",
        SimpleNamespace(url="http://a.local", method="GET", resource_type=lambda: "document"),
    )
    context.emit(
        "response",
        SimpleNamespace(
            url="http://a.local",
            status=lambda: 200,
            ok=lambda: True,
            request=SimpleNamespace(url="http://a.local"),
        ),
    )
    context.emit(
        "requestfailed",
        SimpleNamespace(
            url="http://bad.local",
            method="GET",
            failure=lambda: {"errorText": "net::ERR_CONNECTION_REFUSED"},
        ),
    )

    bundle = await collector.write_bundle(
        base_dir=str(tmp_path),
        run_id="run-1",
        scenario_id="console-network",
        session_id="sess-1",
        fault_type="lifecycle_fault",
        injection_point="before_click",
        status="failed",
        failure_classification="session",
    )
    manifest = json.loads(Path(bundle["manifest_path"]).read_text(encoding="utf-8"))

    assert manifest["run_id"] == "run-1"
    assert manifest["scenario_id"] == "console-network"
    assert manifest["artifact_paths"]["trace"] is not None
    assert Path(manifest["artifact_paths"]["console"]).exists()
    assert Path(manifest["artifact_paths"]["network"]).exists()
    assert Path(manifest["artifact_paths"]["page_errors"]).exists()


@pytest.mark.asyncio
async def test_screenshot_dom_and_trace_artifacts_exist(tmp_path) -> None:
    collector = BrowserDiagnosticsCollector(trace_enabled=True)
    context = FakeContext()
    page = FakePage()
    await collector.attach(context=context, page=page)

    bundle = await collector.write_bundle(
        base_dir=str(tmp_path),
        run_id="run-2",
        scenario_id="artifact-presence",
        session_id="sess-2",
        fault_type="lifecycle_fault",
        injection_point="after_selector_resolved",
        status="failed",
        failure_classification="session",
    )
    manifest = json.loads(Path(bundle["manifest_path"]).read_text(encoding="utf-8"))

    assert manifest["artifact_paths"]["screenshot"] is not None
    assert manifest["artifact_paths"]["dom_snapshot"] is not None
    assert manifest["artifact_paths"]["trace"] is not None
    assert Path(manifest["artifact_paths"]["screenshot"]).exists()
    assert Path(manifest["artifact_paths"]["dom_snapshot"]).exists()
    assert Path(manifest["artifact_paths"]["trace"]).exists()


@pytest.mark.asyncio
async def test_partial_capture_is_reported_when_page_closed(tmp_path) -> None:
    collector = BrowserDiagnosticsCollector(trace_enabled=False)
    await collector.attach(context=FakeContext(), page=FakePage(closed=True))

    bundle = await collector.write_bundle(
        base_dir=str(tmp_path),
        run_id="run-3",
        scenario_id="partial-capture",
        session_id="sess-3",
        fault_type="lifecycle_fault",
        injection_point="before_click",
        status="failed",
        failure_classification="session",
    )
    manifest = json.loads(Path(bundle["manifest_path"]).read_text(encoding="utf-8"))

    assert manifest["artifact_paths"]["screenshot"] is None
    assert manifest["artifact_paths"]["dom_snapshot"] is None
    assert manifest["collection_gaps"]


@pytest.mark.asyncio
async def test_stdio_safe_collection_writes_no_stdout(tmp_path, capsys) -> None:
    collector = BrowserDiagnosticsCollector(trace_enabled=False)
    await collector.attach(context=None, page=None)
    await collector.write_bundle(
        base_dir=str(tmp_path),
        run_id="run-4",
        scenario_id="stdio-safe",
        session_id="sess-4",
        fault_type="lifecycle_fault",
        injection_point="during_teardown",
        status="failed",
        failure_classification="session",
    )
    captured = capsys.readouterr()
    assert captured.out == ""


@pytest.mark.asyncio
async def test_parallel_bundle_isolation(tmp_path) -> None:
    first = BrowserDiagnosticsCollector(trace_enabled=False)
    second = BrowserDiagnosticsCollector(trace_enabled=False)
    await first.attach(context=None, page=None)
    await second.attach(context=None, page=None)

    bundle_a = await first.write_bundle(
        base_dir=str(tmp_path),
        run_id="run-5",
        scenario_id="parallel-a",
        session_id="sess-a",
        fault_type="lifecycle_fault",
        injection_point="before_wait_for_selector",
        status="failed",
        failure_classification="session",
    )
    bundle_b = await second.write_bundle(
        base_dir=str(tmp_path),
        run_id="run-5",
        scenario_id="parallel-b",
        session_id="sess-b",
        fault_type="lifecycle_fault",
        injection_point="before_wait_for_selector",
        status="ok",
        failure_classification="none",
    )
    assert bundle_a["bundle_dir"] != bundle_b["bundle_dir"]
