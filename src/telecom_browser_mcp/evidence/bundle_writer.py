from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from telecom_browser_mcp.evidence.artifact_paths import ArtifactPaths
from telecom_browser_mcp.evidence.redaction import redact_payload
from telecom_browser_mcp.models.artifact import ArtifactRef


class EvidenceBundleWriter:
    def __init__(self, redact: bool = True) -> None:
        self.redact = redact

    def _write_json(self, path: Path, payload: dict) -> None:
        content = redact_payload(payload) if self.redact else payload
        path.write_text(json.dumps(content, indent=2, default=str), encoding="utf-8")

    def collect(
        self,
        *,
        session,
        registration: dict | None = None,
        active_session: dict | None = None,
        webrtc: dict | None = None,
        environment: dict | None = None,
    ) -> list[ArtifactRef]:
        paths = ArtifactPaths(session.artifacts_dir)
        artifacts: list[ArtifactRef] = []

        runtime_payloads = {
            "registration": registration,
            "active-session": active_session,
            "webrtc-summary": webrtc,
            "environment": environment,
        }
        for name, payload in runtime_payloads.items():
            if payload is None:
                continue
            path = paths.runtime_path(name)
            self._write_json(path, payload)
            artifacts.append(
                ArtifactRef(type="runtime", label=name, path=str(path), redacted=self.redact)
            )

        summary_path = Path(session.artifacts_dir) / "summary.json"
        summary_payload = {
            "session_id": session.session_id,
            "run_id": session.run_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "artifacts": [a.model_dump(mode="json") for a in artifacts],
        }
        self._write_json(summary_path, summary_payload)
        artifacts.append(
            ArtifactRef(type="manifest", label="summary", path=str(summary_path), redacted=self.redact)
        )
        return artifacts
