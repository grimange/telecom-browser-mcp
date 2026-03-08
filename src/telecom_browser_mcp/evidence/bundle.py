from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from telecom_browser_mcp.models.common import ArtifactRef
from telecom_browser_mcp.sessions.manager import SessionRuntime


class EvidenceCollector:
    async def collect(
        self,
        runtime: SessionRuntime,
        trigger_tool: str,
        reason: str | None = None,
        diagnostics: list[dict] | None = None,
    ) -> tuple[str, list[ArtifactRef]]:
        bundle_id = datetime.now(UTC).strftime("bundle-%Y%m%dT%H%M%SZ")
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
                html_snapshot_path.write_text(html, encoding="utf-8")
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
        diagnosis_payload = diagnostics if diagnostics is not None else []
        diagnosis_path.write_text(json.dumps(diagnosis_payload, indent=2), encoding="utf-8")
        artifacts.append(ArtifactRef(type="diagnosis_json", path=str(diagnosis_path)))

        manifest_path = root / "manifest.json"
        manifest = {
            "bundle_id": bundle_id,
            "created_at": datetime.now(UTC).isoformat(),
            "trigger_tool": trigger_tool,
            "reason": reason,
            "artifacts": [a.model_dump(mode="json") for a in artifacts],
        }
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        artifacts.append(ArtifactRef(type="manifest", path=str(manifest_path)))
        return str(root), artifacts
