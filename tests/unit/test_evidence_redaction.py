from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from telecom_browser_mcp.adapters.generic import GenericAdapter
from telecom_browser_mcp.browser.manager import BrowserHandle
from telecom_browser_mcp.evidence.bundle import EvidenceCollector
from telecom_browser_mcp.models.session import SessionModel
from telecom_browser_mcp.sessions.manager import SessionRuntime


def test_redact_text_masks_common_secrets() -> None:
    raw = (
        "password=abc token:xyz Authorization: Bearer abc123 cookie=foo "
        "api_key=k1 secret=s1 sip:alice@example.com"
    )
    redacted = EvidenceCollector._redact_text(raw)
    assert "abc" not in redacted
    assert "xyz" not in redacted
    assert "abc123" not in redacted
    assert "cookie=foo" not in redacted
    assert "k1" not in redacted
    assert "s1" not in redacted
    assert "sip:alice@" not in redacted
    assert "[REDACTED]" in redacted


def test_redact_obj_masks_nested_payloads() -> None:
    payload = {
        "message": "token=abc",
        "nested": [{"line": "password:xyz"}, "sip:bob@example.org"],
    }
    redacted = EvidenceCollector._redact_obj(payload)
    assert "abc" not in str(redacted)
    assert "xyz" not in str(redacted)
    assert "bob@" not in str(redacted)


class _FakePage:
    def __init__(self) -> None:
        self.screenshot_calls = 0

    async def content(self) -> str:
        return (
            "<html>Authorization: Bearer html-token cookie=html-cookie "
            "sip:alice@example.test +15551234567 10.1.2.3 "
            "https://example.test/app?token=query-token</html>"
        )

    async def evaluate(self, *_args, **_kwargs):
        return {"title": "token=page-token", "host": "10.1.2.3"}

    async def screenshot(self, **_kwargs) -> None:
        self.screenshot_calls += 1


@pytest.mark.asyncio
async def test_generated_text_artifacts_are_redacted(tmp_path: Path) -> None:
    sensitive_values = [
        "manifest-token",
        "diag-secret",
        "html-token",
        "html-cookie",
        "alice@",
        "+15551234567",
        "10.1.2.3",
        "query-token",
        "11111111-2222-4333-8444-555555555555",
    ]
    model = SessionModel(
        session_id="11111111-2222-4333-8444-555555555555",
        adapter_id="generic",
        adapter_name="Generic",
        target_url="https://example.test/app?token=manifest-token",
        lifecycle_state="ready",
        artifact_root=str(tmp_path),
    )
    runtime = SessionRuntime(
        model=model,
        adapter=GenericAdapter(),
        browser=BrowserHandle(browser_open=True, target_url=model.target_url, page=_FakePage()),
        created_at=datetime.now(UTC),
        last_touched_at=datetime.now(UTC),
        operation_lock=SimpleNamespace(),
    )

    bundle_path, _artifacts = await EvidenceCollector().collect(
        runtime,
        trigger_tool="collect_debug_bundle",
        reason="secret=diag-secret",
        diagnostics=[{"message": "password=diag-secret Authorization: Bearer diag-secret"}],
    )

    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path(bundle_path).rglob("*")
        if path.suffix in {".json", ".html"}
    )
    for raw in sensitive_values:
        assert raw not in text
    assert "[REDACTED]" in text


@pytest.mark.asyncio
async def test_non_harness_screenshots_are_disabled_by_default(tmp_path: Path) -> None:
    page = _FakePage()
    model = SessionModel(
        session_id="session-1",
        adapter_id="generic",
        adapter_name="Generic",
        target_url="https://example.test/app",
        lifecycle_state="ready",
        artifact_root=str(tmp_path),
    )
    runtime = SessionRuntime(
        model=model,
        adapter=GenericAdapter(),
        browser=BrowserHandle(browser_open=True, target_url=model.target_url, page=page),
        created_at=datetime.now(UTC),
        last_touched_at=datetime.now(UTC),
        operation_lock=SimpleNamespace(),
    )

    bundle_path, artifacts = await EvidenceCollector().collect(runtime, "collect_debug_bundle")

    screenshot = next(item for item in artifacts if item.type == "screenshot")
    manifest = (Path(bundle_path) / "manifest.json").read_text(encoding="utf-8")
    assert screenshot.captured is False
    assert "screenshot capture disabled by default" in (screenshot.message or "")
    assert page.screenshot_calls == 0
    assert '"screenshot_capture_enabled": false' in manifest
    assert '"screenshot_pixel_redaction": false' in manifest


@pytest.mark.asyncio
async def test_harness_screenshots_remain_enabled_by_default(tmp_path: Path) -> None:
    page = _FakePage()
    model = SessionModel(
        session_id="session-2",
        adapter_id="fake_dialer",
        adapter_name="Fake Dialer",
        target_url="http://127.0.0.1/fake",
        lifecycle_state="ready",
        artifact_root=str(tmp_path),
    )
    runtime = SessionRuntime(
        model=model,
        adapter=GenericAdapter(),
        browser=BrowserHandle(browser_open=True, target_url=model.target_url, page=page),
        created_at=datetime.now(UTC),
        last_touched_at=datetime.now(UTC),
        operation_lock=SimpleNamespace(),
    )

    bundle_path, artifacts = await EvidenceCollector().collect(runtime, "collect_debug_bundle")

    screenshot = next(item for item in artifacts if item.type == "screenshot")
    manifest = (Path(bundle_path) / "manifest.json").read_text(encoding="utf-8")
    assert screenshot.captured is True
    assert page.screenshot_calls == 1
    assert "sensitive visual artifact" in (screenshot.message or "")
    assert '"screenshot_capture_enabled": true' in manifest
