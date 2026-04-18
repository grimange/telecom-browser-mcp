from __future__ import annotations

from abc import ABC
from typing import Any

from telecom_browser_mcp.models.session import TelecomStatus


class AdapterBase(ABC):
    adapter_id = "base"
    adapter_version = "0.1"
    capabilities = None

    async def login(
        self,
        status: TelecomStatus,
        page: Any,
        credentials: dict[str, Any],
        timeout_ms: int,
    ) -> tuple[bool, str]:
        _ = (status, page, credentials, timeout_ms)
        return False, "login unsupported"

    async def wait_for_ready(self, status: TelecomStatus, page: Any, timeout_ms: int) -> tuple[bool, str]:
        _ = (page, timeout_ms)
        status.ui_ready = True
        return True, "ready"

    async def wait_for_registration(self, status: TelecomStatus, page: Any, timeout_ms: int) -> tuple[bool, str]:
        _ = (status, page, timeout_ms)
        return False, "registration unsupported"

    async def wait_for_incoming_call(self, status: TelecomStatus, page: Any, timeout_ms: int) -> tuple[bool, str]:
        _ = (status, page, timeout_ms)
        return False, "incoming call detection unsupported"

    async def answer_call(self, status: TelecomStatus, page: Any, timeout_ms: int) -> tuple[bool, str]:
        _ = (status, page, timeout_ms)
        return False, "answer unsupported"

    async def peer_connection_summary(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        _ = (status, page)
        return {
            "available": False,
            "reason": "adapter does not expose webrtc summary",
            "source": self.adapter_id,
        }
