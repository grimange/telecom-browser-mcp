from __future__ import annotations

from datetime import UTC, datetime

from telecom_browser_mcp.sessions.manager import SessionRuntime


class SessionInspector:
    def snapshot(self, runtime: SessionRuntime) -> dict:
        model = runtime.model
        return {
            "session": model.model_dump(mode="json"),
            "observed_at": datetime.now(UTC).isoformat(),
            "source": "session_manager",
        }
