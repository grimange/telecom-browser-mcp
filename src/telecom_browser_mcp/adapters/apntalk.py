from __future__ import annotations

from typing import Any

from telecom_browser_mcp.adapters.base import AdapterBase
from telecom_browser_mcp.models.session import AdapterCapabilities, TelecomStatus


class APNTalkAdapter(AdapterBase):
    adapter_id = "apntalk"
    adapter_version = "0.1"
    capabilities = AdapterCapabilities(
        supports_login=False,
        supports_registration_detection=False,
        supports_incoming_call_detection=False,
        supports_answer_action=False,
        supports_hangup_action=False,
        supports_webrtc_summary=True,
    )

    async def wait_for_ready(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> tuple[bool, str]:
        if page is None:
            return False, "page unavailable"
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            status.ui_ready = True
            return True, "page loaded; APNTalk selector-specific readiness pending adapter hardening"
        except Exception:
            return False, "page did not reach domcontentloaded state"

    async def peer_connection_summary(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        _ = (status, page)
        return {
            "available": False,
            "reason": "APNTalk runtime object path not configured; add verified inspector path in adapter hardening",
            "source": self.adapter_id,
        }
