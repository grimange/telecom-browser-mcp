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
            "adapter_name": runtime.model.adapter_name,
            "adapter_version": runtime.model.adapter_version,
            "contract_version": runtime.model.contract_version,
            "scenario_id": runtime.model.scenario_id,
            "summary": adapter_summary,
        }
