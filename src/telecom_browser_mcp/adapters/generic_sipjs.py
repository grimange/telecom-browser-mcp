from __future__ import annotations

from telecom_browser_mcp.models.call import CallSnapshot
from telecom_browser_mcp.models.enums import CallState, RegistrationState, WebRtcState
from telecom_browser_mcp.models.registration import RegistrationSnapshot
from telecom_browser_mcp.models.webrtc import WebRtcSnapshot


class GenericSipJsAdapter:
    name = "generic_sipjs"
    version = "0.1.0"

    async def open_app(self, session, url: str) -> dict:
        session.base_url = url
        result = await session.ensure_driver().open(url)
        if result.get("ok"):
            session.current_page_url = str(result.get("current_page_url", url))
            session.page_title = str(result.get("page_title", ""))
            session.environment_classification = str(result.get("environment_classification", "unknown"))
        else:
            session.environment_classification = str(result.get("environment_classification", "unknown"))
        session.touch()
        return result

    async def login_agent(self, session, username: str, password: str, tenant: str | None = None) -> dict:
        _ = username, password, tenant
        session.touch()
        return {
            "ok": True,
            "message": "login scaffold executed",
            "warnings": ["adapter selector mapping is a scaffold"],
        }

    async def wait_for_ready(self, session, timeout_ms: int = 30_000) -> dict:
        _ = timeout_ms
        session.touch()
        if session.current_page_url:
            return {"ok": True, "ready": True, "message": "application appears reachable"}
        return {
            "ok": False,
            "ready": False,
            "message": "page was not opened yet",
            "reason": "open_app must run first",
        }

    async def get_registration_snapshot(self, session) -> RegistrationSnapshot:
        _ = session
        return RegistrationSnapshot(
            state=RegistrationState.UNKNOWN,
            registered=False,
            source_confidence=0.2,
            available=False,
            reason="adapter registration selectors/runtime hooks are scaffold-only",
        )

    async def wait_for_registration(
        self, session, expected: str = "registered", timeout_ms: int = 30_000
    ) -> RegistrationSnapshot:
        _ = timeout_ms
        snapshot = await self.get_registration_snapshot(session)
        if snapshot.state.value == expected:
            return snapshot
        snapshot.reason = f"expected {expected} but observed {snapshot.state.value}"
        return snapshot

    async def wait_for_incoming_call(self, session, timeout_ms: int = 30_000) -> CallSnapshot:
        _ = session, timeout_ms
        return CallSnapshot(
            state=CallState.FAILED,
            available=False,
            reason="incoming call detection selectors are not implemented in generic scaffold",
        )

    async def answer_call(
        self, session, call_ref: str | None = None, timeout_ms: int = 15_000
    ) -> CallSnapshot:
        _ = session, call_ref, timeout_ms
        return CallSnapshot(
            state=CallState.FAILED,
            available=False,
            reason="answer call action is a scaffold in generic adapter",
        )

    async def hangup_call(
        self, session, call_ref: str | None = None, timeout_ms: int = 15_000
    ) -> CallSnapshot:
        _ = session, call_ref, timeout_ms
        return CallSnapshot(state=CallState.ENDED, available=True)

    async def get_ui_call_state(self, session) -> dict:
        _ = session
        return {"available": False, "state": "unknown", "reason": "UI hook not configured"}

    async def get_store_snapshot(self, session) -> dict:
        _ = session
        return {
            "available": False,
            "source": "adapter",
            "reason": "store extraction hook not configured",
        }

    async def get_active_session_snapshot(self, session) -> CallSnapshot:
        _ = session
        return CallSnapshot(
            state=CallState.IDLE,
            available=False,
            reason="active session runtime object is not configured",
        )

    async def get_peer_connection_summary(self, session) -> WebRtcSnapshot:
        _ = session
        return WebRtcSnapshot(
            peer_connection_present=False,
            connection_state=WebRtcState.MISSING,
            available=False,
            reason="peer connection runtime hook not configured",
        )
