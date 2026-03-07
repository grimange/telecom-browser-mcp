from __future__ import annotations

from typing import Protocol

from telecom_browser_mcp.models.call import CallSnapshot
from telecom_browser_mcp.models.registration import RegistrationSnapshot
from telecom_browser_mcp.models.webrtc import WebRtcSnapshot


class TelecomAdapter(Protocol):
    name: str
    version: str

    async def open_app(self, session, url: str) -> dict: ...

    async def login_agent(
        self, session, username: str, password: str, tenant: str | None = None
    ) -> dict: ...

    async def wait_for_ready(self, session, timeout_ms: int = 30_000) -> dict: ...

    async def get_registration_snapshot(self, session) -> RegistrationSnapshot: ...

    async def wait_for_registration(
        self, session, expected: str = "registered", timeout_ms: int = 30_000
    ) -> RegistrationSnapshot: ...

    async def wait_for_incoming_call(self, session, timeout_ms: int = 30_000) -> CallSnapshot: ...

    async def answer_call(
        self, session, call_ref: str | None = None, timeout_ms: int = 15_000
    ) -> CallSnapshot: ...

    async def hangup_call(
        self, session, call_ref: str | None = None, timeout_ms: int = 15_000
    ) -> CallSnapshot: ...

    async def get_ui_call_state(self, session) -> dict: ...

    async def get_store_snapshot(self, session) -> dict: ...

    async def get_active_session_snapshot(self, session) -> CallSnapshot: ...

    async def get_peer_connection_summary(self, session) -> WebRtcSnapshot: ...
