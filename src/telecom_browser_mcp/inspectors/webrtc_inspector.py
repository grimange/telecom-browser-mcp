from __future__ import annotations

from datetime import UTC, datetime

from telecom_browser_mcp.sessions.manager import SessionRuntime


class WebRTCInspector:
    async def summary(self, runtime: SessionRuntime) -> dict:
        adapter_summary = await runtime.adapter.peer_connection_summary(
            runtime.model.telecom,
            runtime.browser.page,
        )
        return {
            "observed_at": datetime.now(UTC).isoformat(),
            "summary": adapter_summary,
        }
