from telecom_browser_mcp.models.call import CallSnapshot
from telecom_browser_mcp.models.enums import CallState, RegistrationState, WebRtcState
from telecom_browser_mcp.models.registration import RegistrationSnapshot
from telecom_browser_mcp.models.webrtc import WebRtcSnapshot


class HarnessAdapter:
    """Deterministic adapter used by integration tests and fake dialer workflows."""

    name = "harness"
    version = "0.1.0"

    def __init__(self) -> None:
        self._registered = False
        self._incoming = False
        self._connected = False
        self._registration_flapping = False
        self._registration_delayed = False
        self._duplicate_incoming = False
        self._incoming_absent = False
        self._answer_ui_mismatch = False
        self._answer_timeout = False
        self._registration_reads = 0
        self._incoming_events = 0
        self._registration_wait_attempts = 0

    async def open_app(self, session, url: str) -> dict:
        session.base_url = url
        session.current_page_url = url
        session.page_title = "Fake Dialer"
        session.environment_classification = "harness"
        return {"ok": True, "message": "harness app opened", "current_page_url": url}

    async def login_agent(self, session, username: str, password: str, tenant: str | None = None) -> dict:
        _ = session, username, password
        tenant = tenant or ""
        self._registration_flapping = "registration_flapping" in tenant
        self._registration_delayed = "registration_delayed" in tenant
        self._duplicate_incoming = "incoming_duplicate" in tenant
        self._incoming_absent = "incoming_absent" in tenant
        self._answer_ui_mismatch = "answer_ui_mismatch" in tenant
        self._answer_timeout = "answer_timeout" in tenant
        return {"ok": True, "message": "harness login ok"}

    async def wait_for_ready(self, session, timeout_ms: int = 30_000) -> dict:
        _ = session, timeout_ms
        return {"ok": True, "ready": True, "message": "harness ready"}

    async def get_registration_snapshot(self, session) -> RegistrationSnapshot:
        _ = session
        self._registration_reads += 1
        if self._registration_flapping and self._registered:
            flapping_state = (
                RegistrationState.REGISTERED
                if self._registration_reads % 2 == 0
                else RegistrationState.CONNECTING
            )
            return RegistrationSnapshot(
                state=flapping_state,
                registered=flapping_state == RegistrationState.REGISTERED,
                source_confidence=0.95,
                available=True,
                source="harness",
                reason="registration flapping scenario enabled",
            )
        return RegistrationSnapshot(
            state=RegistrationState.REGISTERED if self._registered else RegistrationState.CONNECTING,
            registered=self._registered,
            source_confidence=0.95,
            available=True,
            source="harness",
        )

    async def wait_for_registration(
        self, session, expected: str = "registered", timeout_ms: int = 30_000
    ) -> RegistrationSnapshot:
        _ = session, timeout_ms
        self._registration_wait_attempts += 1
        if (
            expected == "registered"
            and self._registration_delayed
            and self._registration_wait_attempts == 1
        ):
            return RegistrationSnapshot(
                state=RegistrationState.CONNECTING,
                registered=False,
                source_confidence=0.95,
                available=True,
                source="harness",
                reason="registration delayed scenario enabled",
            )
        if expected == "registered":
            self._registered = True
        return await self.get_registration_snapshot(session)

    async def wait_for_incoming_call(self, session, timeout_ms: int = 30_000) -> CallSnapshot:
        _ = session, timeout_ms
        if self._incoming_absent:
            return CallSnapshot(
                state=CallState.IDLE,
                available=False,
                reason="incoming absent scenario enabled",
            )
        self._incoming = True
        self._incoming_events += 1
        correlation = {"duplicate_events": "2"} if self._duplicate_incoming else {}
        return CallSnapshot(
            call_id="harness-call-001",
            direction="incoming",
            state=CallState.RINGING,
            ui_state="ringing",
            store_state="ringing",
            correlation_keys=correlation,
            reason=(
                "duplicate incoming event scenario enabled"
                if self._duplicate_incoming
                else None
            ),
            available=True,
        )

    async def answer_call(
        self, session, call_ref: str | None = None, timeout_ms: int = 15_000
    ) -> CallSnapshot:
        _ = session, call_ref, timeout_ms
        if self._answer_timeout:
            return CallSnapshot(
                call_id="harness-call-001",
                direction="incoming",
                state=CallState.FAILED,
                available=False,
                reason="answer timeout scenario enabled",
            )
        if not self._incoming:
            return CallSnapshot(state=CallState.FAILED, available=False, reason="no incoming call")
        self._connected = True
        if self._answer_ui_mismatch:
            return CallSnapshot(
                call_id="harness-call-001",
                direction="incoming",
                state=CallState.CONNECTED,
                ui_state="ringing",
                store_state="connected",
                sip_session_state="confirmed",
                available=True,
                reason="answer ui mismatch scenario enabled",
            )
        return CallSnapshot(
            call_id="harness-call-001",
            direction="incoming",
            state=CallState.CONNECTED,
            ui_state="connected",
            store_state="connected",
            available=True,
        )

    async def hangup_call(
        self, session, call_ref: str | None = None, timeout_ms: int = 15_000
    ) -> CallSnapshot:
        _ = session, call_ref, timeout_ms
        self._incoming = False
        self._connected = False
        return CallSnapshot(call_id="harness-call-001", state=CallState.ENDED, available=True)

    async def get_ui_call_state(self, session) -> dict:
        _ = session
        if self._connected:
            return {"available": True, "state": "connected"}
        if self._incoming:
            return {"available": True, "state": "ringing"}
        return {"available": True, "state": "idle"}

    async def get_store_snapshot(self, session) -> dict:
        _ = session
        return {
            "available": True,
            "source": "harness",
            "registration": "registered" if self._registered else "connecting",
            "call_state": "connected" if self._connected else ("ringing" if self._incoming else "idle"),
        }

    async def get_active_session_snapshot(self, session) -> CallSnapshot:
        _ = session
        if self._connected:
            return CallSnapshot(
                call_id="harness-call-001",
                direction="incoming",
                state=CallState.CONNECTED,
                available=True,
            )
        return CallSnapshot(state=CallState.IDLE, available=True)

    async def get_peer_connection_summary(self, session) -> WebRtcSnapshot:
        _ = session
        if self._connected:
            return WebRtcSnapshot(
                peer_connection_present=True,
                connection_state=WebRtcState.CONNECTED,
                local_audio_tracks=1,
                remote_audio_tracks=1,
                inbound_rtp_audio_packets=100,
                outbound_rtp_audio_packets=120,
                available=True,
                source="harness",
            )
        return WebRtcSnapshot(
            peer_connection_present=False,
            connection_state=WebRtcState.MISSING,
            available=True,
            source="harness",
        )
