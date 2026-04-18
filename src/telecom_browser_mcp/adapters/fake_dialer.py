from __future__ import annotations

from typing import Any

from telecom_browser_mcp.adapters.base import AdapterBase
from telecom_browser_mcp.models.session import AdapterCapabilities, TelecomStatus


class FakeDialerAdapter(AdapterBase):
    adapter_id = "fake_dialer"
    adapter_version = "0.1"
    capabilities = AdapterCapabilities(
        supports_login=True,
        supports_registration_detection=True,
        supports_incoming_call_detection=True,
        supports_answer_action=True,
        supports_hangup_action=False,
        supports_webrtc_summary=True,
    )

    async def login(
        self,
        status: TelecomStatus,
        page: Any,
        credentials: dict[str, Any],
        timeout_ms: int,
    ) -> tuple[bool, str]:
        _ = credentials
        if page is None:
            return False, "page unavailable"
        try:
            await page.wait_for_selector("#app-ready", timeout=timeout_ms)
            status.login_complete = True
            return True, "login simulated"
        except Exception:
            return False, "login UI not ready"

    async def wait_for_ready(self, status: TelecomStatus, page: Any, timeout_ms: int) -> tuple[bool, str]:
        if page is None:
            return False, "page unavailable"
        try:
            await page.wait_for_selector("#app-ready", timeout=timeout_ms)
            state = await page.locator("#app-ready").get_attribute("data-state")
            if state == "ready":
                status.ui_ready = True
                return True, "ready"
            return False, f"unexpected ready state: {state}"
        except Exception:
            return False, "ready marker not found"

    async def wait_for_registration(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> tuple[bool, str]:
        if page is None:
            return False, "page unavailable"
        try:
            await page.wait_for_function(
                "() => (document.querySelector('#registration-state')?.textContent || '').trim() === 'registered'",
                timeout=timeout_ms,
            )
            status.registration_state = "registered"
            return True, "registered"
        except Exception:
            return False, "registration never reached 'registered'"

    async def wait_for_incoming_call(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> tuple[bool, str]:
        if page is None:
            return False, "page unavailable"
        try:
            await page.wait_for_function(
                "() => (document.querySelector('#incoming-call-state')?.textContent || '').trim() === 'ringing'",
                timeout=timeout_ms,
            )
            status.incoming_call_state = "ringing"
            return True, "incoming call detected"
        except Exception:
            return False, "incoming call was not presented"

    async def answer_call(self, status: TelecomStatus, page: Any, timeout_ms: int) -> tuple[bool, str]:
        if page is None:
            return False, "page unavailable"
        button = page.locator("#answer-btn")
        count = await button.count()
        if count == 0:
            return False, "answer control not found"

        await button.click(timeout=timeout_ms)
        try:
            await page.wait_for_function(
                """
                () => {
                  const value = (document.querySelector('#active-call-state')?.textContent || '').trim();
                  return value === 'connected' || value === 'failed';
                }
                """,
                timeout=timeout_ms,
            )
        except Exception:
            return False, "answer action timed out"

        state = (await page.locator("#active-call-state").inner_text()).strip()
        status.active_call_state = state
        if state == "connected":
            return True, "call connected"
        return False, "answer clicked but call failed"

    async def peer_connection_summary(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        _ = status
        if page is None:
            return {
                "available": False,
                "reason": "page unavailable",
                "source": self.adapter_id,
            }
        payload = await page.evaluate(
            """
            () => {
              const pc = window.__fakeDialer?.peerConnection || null;
              if (!pc) {
                return { available: false, reason: 'no peer connection detected', source: 'fake_dialer' };
              }
              return {
                available: true,
                source: 'fake_dialer',
                connection_state: pc.connectionState,
                ice_connection_state: pc.iceConnectionState,
              };
            }
            """
        )
        return payload
