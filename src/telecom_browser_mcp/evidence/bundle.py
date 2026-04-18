from __future__ import annotations

import json
import platform
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from telecom_browser_mcp.models.common import ArtifactRef
from telecom_browser_mcp.diagnostics.taxonomy import classify_target, summarize_verdict
from telecom_browser_mcp.sessions.manager import SessionRuntime


class EvidenceCollector:
    def __init__(self, max_bundles_per_session: int = 5) -> None:
        self._max_bundles_per_session = max_bundles_per_session

    @staticmethod
    async def _media_capability_findings(runtime: SessionRuntime) -> dict[str, Any]:
        if runtime.browser.page is None:
            return {
                "available": False,
                "reason": "browser page unavailable",
            }
        try:
            return await runtime.browser.page.evaluate(
                """
                () => ({
                  available: true,
                  has_media_devices: !!navigator.mediaDevices,
                  has_get_user_media: typeof navigator.mediaDevices?.getUserMedia === 'function',
                  has_enumerate_devices: typeof navigator.mediaDevices?.enumerateDevices === 'function'
                })
                """
            )
        except Exception as exc:
            return {
                "available": False,
                "reason": f"media capability probe failed: {exc}",
            }

    @staticmethod
    async def _app_metadata(runtime: SessionRuntime) -> dict[str, Any]:
        host = (urlparse(runtime.model.target_url).hostname or "").lower()
        if runtime.browser.page is None:
            return {"host": host, "title": None, "app_version": None}
        try:
            return await runtime.browser.page.evaluate(
                """
                ({ host }) => ({
                  host,
                  title: document.title || null,
                  app_version:
                    document.querySelector('meta[name="app-version"]')?.content ||
                    document.querySelector('[data-app-version]')?.getAttribute('data-app-version') ||
                    null
                })
                """,
                {"host": host},
            )
        except Exception:
            return {"host": host, "title": None, "app_version": None}

    @staticmethod
    def _redact_text(value: str) -> str:
        redacted = value
        patterns = [
            (
                r"(?i)(authorization\s*[=:]\s*bearer\s+)([^\s\"'<>;,]+)",
                r"\1[REDACTED]",
            ),
            (r"(?i)(password\s*[=:]\s*)([^\s\"'<>]+)", r"\1[REDACTED]"),
            (r"(?i)(token\s*[=:]\s*)([^\s\"'<>]+)", r"\1[REDACTED]"),
            (r"(?i)(authorization\s*[=:]\s*)([^\s\"'<>]+)", r"\1[REDACTED]"),
            (r"(?i)(cookie\s*[=:]\s*)([^\s\"'<>]+)", r"\1[REDACTED]"),
            (r"(?i)(api[_-]?key\s*[=:]\s*)([^\s\"'<>]+)", r"\1[REDACTED]"),
            (r"(?i)(secret\s*[=:]\s*)([^\s\"'<>]+)", r"\1[REDACTED]"),
            (r"(?i)(sip:[^@\s\"'<>]+@)", "sip:[REDACTED]@"),
        ]
        for pattern, replacement in patterns:
            redacted = re.sub(pattern, replacement, redacted)
        return redacted

    @classmethod
    def _redact_obj(cls, value: Any) -> Any:
        if isinstance(value, str):
            return cls._redact_text(value)
        if isinstance(value, list):
            return [cls._redact_obj(item) for item in value]
        if isinstance(value, dict):
            return {key: cls._redact_obj(item) for key, item in value.items()}
        return value

    async def collect(
        self,
        runtime: SessionRuntime,
        trigger_tool: str,
        reason: str | None = None,
        diagnostics: list[dict] | None = None,
    ) -> tuple[str, list[ArtifactRef]]:
        bundle_id = datetime.now(UTC).strftime("bundle-%Y%m%dT%H%M%S%fZ")
        root = Path(runtime.model.artifact_root) / bundle_id
        screenshots = root / "screenshots"
        runtime_state = root / "runtime_state"
        diagnostics_dir = root / "diagnostics"
        console_logs = root / "console_logs"
        for directory in (root, screenshots, runtime_state, diagnostics_dir, console_logs):
            directory.mkdir(parents=True, exist_ok=True)

        artifacts: list[ArtifactRef] = []

        session_snapshot_path = runtime_state / "session_snapshot.json"
        session_snapshot_path.write_text(
            json.dumps(runtime.model.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )
        artifacts.append(ArtifactRef(type="session_snapshot_json", path=str(session_snapshot_path)))

        html_snapshot_path = runtime_state / "page_snapshot.html"
        screenshot_path = screenshots / "page.png"
        if runtime.browser.page is None:
            artifacts.append(
                ArtifactRef(
                    type="html_snapshot",
                    path=str(html_snapshot_path),
                    captured=False,
                    message="browser page unavailable",
                )
            )
            artifacts.append(
                ArtifactRef(
                    type="screenshot",
                    path=str(screenshot_path),
                    captured=False,
                    message="browser page unavailable",
                )
            )
        else:
            try:
                html = await runtime.browser.page.content()
                html_snapshot_path.write_text(self._redact_text(html), encoding="utf-8")
                artifacts.append(ArtifactRef(type="html_snapshot", path=str(html_snapshot_path)))
            except Exception as exc:
                artifacts.append(
                    ArtifactRef(
                        type="html_snapshot",
                        path=str(html_snapshot_path),
                        captured=False,
                        message=f"html capture failed: {exc}",
                    )
                )
            try:
                await runtime.browser.page.screenshot(path=str(screenshot_path), full_page=True)
                artifacts.append(ArtifactRef(type="screenshot", path=str(screenshot_path)))
            except Exception as exc:
                artifacts.append(
                    ArtifactRef(
                        type="screenshot",
                        path=str(screenshot_path),
                        captured=False,
                        message=f"screenshot capture failed: {exc}",
                    )
                )

        diagnosis_path = diagnostics_dir / "diagnosis.json"
        diagnosis_payload = self._redact_obj(diagnostics if diagnostics is not None else [])
        diagnosis_path.write_text(json.dumps(diagnosis_payload, indent=2), encoding="utf-8")
        artifacts.append(ArtifactRef(type="diagnosis_json", path=str(diagnosis_path)))

        manifest_path = root / "manifest.json"
        verdict_summary = summarize_verdict(runtime, diagnosis_payload)
        verdict_summary_path = diagnostics_dir / "verdict_summary.json"
        verdict_payload = {
            "bundle_id": bundle_id,
            "trigger_tool": trigger_tool,
            "reason": reason,
            "verdict": verdict_summary.verdict,
            "canonical_classification": verdict_summary.canonical_classification,
            "environment_vs_product": verdict_summary.environment_vs_product,
            "adapter_name": runtime.model.adapter_name,
            "adapter_id": runtime.model.adapter_id,
            "adapter_version": runtime.model.adapter_version,
            "contract_version": runtime.model.contract_version,
            "scenario_id": runtime.model.scenario_id,
        }
        verdict_summary_path.write_text(json.dumps(verdict_payload, indent=2), encoding="utf-8")
        artifacts.append(ArtifactRef(type="verdict_summary_json", path=str(verdict_summary_path)))

        runtime_metadata = {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "browser_open": runtime.browser.browser_open,
            "browser_launch_error": runtime.model.browser_launch_error,
            "browser_launch_error_classification": runtime.model.browser_launch_error_classification,
            "target_classification": classify_target(runtime),
            "media_capability_findings": await self._media_capability_findings(runtime),
            "app_metadata": await self._app_metadata(runtime),
        }
        manifest = {
            "bundle_id": bundle_id,
            "created_at": datetime.now(UTC).isoformat(),
            "trigger_tool": trigger_tool,
            "reason": reason,
            "adapter_name": runtime.model.adapter_name,
            "adapter_id": runtime.model.adapter_id,
            "adapter_version": runtime.model.adapter_version,
            "contract_version": runtime.model.contract_version,
            "scenario_id": runtime.model.scenario_id,
            "verdict_summary": verdict_payload,
            "runtime_metadata": runtime_metadata,
            "artifacts": [a.model_dump(mode="json") for a in artifacts],
        }
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        artifacts.append(ArtifactRef(type="manifest", path=str(manifest_path)))
        self._prune_old_bundles(Path(runtime.model.artifact_root))
        return str(root), artifacts

    def _prune_old_bundles(self, artifact_root: Path) -> None:
        if self._max_bundles_per_session <= 0:
            return
        bundles = sorted(
            [path for path in artifact_root.iterdir() if path.is_dir() and path.name.startswith("bundle-")]
        )
        if len(bundles) <= self._max_bundles_per_session:
            return
        for stale in bundles[: len(bundles) - self._max_bundles_per_session]:
            for child in sorted(stale.rglob("*"), reverse=True):
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            stale.rmdir()
