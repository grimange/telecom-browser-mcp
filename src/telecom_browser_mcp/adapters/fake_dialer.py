from __future__ import annotations

from typing import Any

from telecom_browser_mcp.adapters.base import AdapterBase, AdapterOperationResult
from telecom_browser_mcp.models.session import AdapterCapabilities, TelecomStatus


class FakeDialerAdapter(AdapterBase):
    adapter_id = "fake_dialer"
    adapter_name = "Fake Dialer"
    adapter_version = "0.1"
    contract_version = "fake-dialer.v1"
    scenario_id = "fake-dialer-happy-path"
    capabilities = AdapterCapabilities(
        supports_login=True,
        supports_registration_detection=True,
        supports_incoming_call_detection=True,
        supports_answer_action=True,
        supports_hangup_action=True,
        supports_webrtc_summary=True,
    )

    async def login(
        self,
        status: TelecomStatus,
        page: Any,
        credentials: dict[str, Any],
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = credentials
        if page is None:
            return self._failure(
                "page unavailable",
                error_code="runtime_probe_unavailable",
                classification="environment_limitation",
                retryable=True,
            )
        try:
            await page.wait_for_selector("#app-ready", timeout=timeout_ms)
            status.login_complete = True
            return self._success("login simulated")
        except Exception:
            return self._failure(
                "login UI not ready",
                error_code="selector_contract_missing",
                classification="ui_drift",
                retryable=True,
            )

    async def wait_for_ready(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        if page is None:
            return self._failure(
                "page unavailable",
                error_code="runtime_probe_unavailable",
                classification="environment_limitation",
                retryable=True,
            )
        try:
            await page.wait_for_selector("#app-ready", timeout=timeout_ms)
            state = await page.locator("#app-ready").get_attribute("data-state")
            if state == "ready":
                status.ui_ready = True
                return self._success("ready")
            return self._failure(
                f"unexpected ready state: {state}",
                error_code="state_divergence",
                classification="state_divergence",
                retryable=True,
            )
        except Exception:
            return self._failure(
                "ready marker not found",
                error_code="selector_contract_missing",
                classification="ui_drift",
                retryable=True,
            )

    async def wait_for_registration(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        if page is None:
            return self._failure(
                "page unavailable",
                error_code="runtime_probe_unavailable",
                classification="environment_limitation",
                retryable=True,
            )
        try:
            await page.wait_for_function(
                "() => (document.querySelector('#registration-state')?.textContent || '').trim() === 'registered'",
                timeout=timeout_ms,
            )
            status.registration_state = "registered"
            return self._success("registered")
        except Exception:
            return self._failure(
                "registration never reached 'registered'",
                error_code="registration_runtime_failure",
                classification="registration_runtime_failure",
                retryable=True,
            )

    async def wait_for_incoming_call(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        if page is None:
            return self._failure(
                "page unavailable",
                error_code="runtime_probe_unavailable",
                classification="environment_limitation",
                retryable=True,
            )
        try:
            await page.wait_for_function(
                "() => (document.querySelector('#incoming-call-state')?.textContent || '').trim() === 'ringing'",
                timeout=timeout_ms,
            )
            status.incoming_call_state = "ringing"
            return self._success("incoming call detected")
        except Exception:
            return self._failure(
                "incoming call was not presented",
                error_code="call_delivery_failure",
                classification="call_delivery_failure",
                retryable=True,
            )

    async def answer_call(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        if page is None:
            return self._failure(
                "page unavailable",
                error_code="runtime_probe_unavailable",
                classification="environment_limitation",
                retryable=True,
            )
        button = page.locator("#answer-btn")
        count = await button.count()
        if count == 0:
            return self._failure(
                "answer control not found",
                error_code="selector_contract_missing",
                classification="ui_drift",
            )

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
            return self._failure(
                "answer action timed out",
                error_code="call_delivery_failure",
                classification="call_delivery_failure",
            )

        state = (await page.locator("#active-call-state").inner_text()).strip()
        status.active_call_state = state
        if state == "connected":
            return self._success("call connected")
        return self._failure(
            "answer clicked but call failed",
            error_code="call_delivery_failure",
            classification="call_delivery_failure",
        )

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
                return {
                  available: false,
                  reason: 'no peer connection detected',
                  reason_code: 'runtime_probe_unavailable',
                  source: 'fake_dialer',
                  adapter_name: 'Fake Dialer',
                  adapter_version: '0.1',
                  contract_version: 'fake-dialer.v1',
                  scenario_id: 'fake-dialer-happy-path'
                };
              }
              return {
                available: true,
                source: 'fake_dialer',
                adapter_name: 'Fake Dialer',
                adapter_version: '0.1',
                contract_version: 'fake-dialer.v1',
                scenario_id: 'fake-dialer-happy-path',
                connection_state: pc.connectionState,
                ice_connection_state: pc.iceConnectionState,
                incoming_delivery_count: window.__fakeDialer?.incomingDeliveryCount || 0,
                media_status: window.__fakeDialer?.media || null,
                store_snapshot: window.__fakeDialer?.store || null,
              };
            }
            """
        )
        return payload

    async def hangup_call(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        if page is None:
            return self._failure(
                "page unavailable",
                error_code="runtime_probe_unavailable",
                classification="environment_limitation",
                retryable=True,
            )
        button = page.locator("#hangup-btn")
        count = await button.count()
        if count == 0:
            return self._failure(
                "hangup control not found",
                error_code="selector_contract_missing",
                classification="ui_drift",
            )
        await button.click(timeout=timeout_ms)
        try:
            await page.wait_for_function(
                "() => (document.querySelector('#active-call-state')?.textContent || '').trim() === 'disconnected'",
                timeout=timeout_ms,
            )
        except Exception:
            return self._failure(
                "hangup action timed out",
                error_code="call_delivery_failure",
                classification="call_delivery_failure",
            )
        status.active_call_state = "disconnected"
        return self._success("call disconnected")

    async def registration_snapshot(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        if page is None:
            return await super().registration_snapshot(status, page)
        return await page.evaluate(
            """
            () => ({
              available: true,
              registration_state: (document.querySelector('#registration-state')?.textContent || '').trim(),
              store_registration_state: (document.querySelector('#store-registration-state')?.textContent || '').trim(),
              source: 'fake_dialer',
              adapter_name: 'Fake Dialer',
              adapter_version: '0.1',
              contract_version: 'fake-dialer.v1',
              scenario_id: 'fake-dialer-happy-path'
            })
            """
        )

    async def store_snapshot(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        _ = status
        if page is None:
            return await super().store_snapshot(status, page)
        return await page.evaluate(
            """
            () => ({
              available: true,
              source: 'fake_dialer',
              adapter_name: 'Fake Dialer',
              adapter_version: '0.1',
              contract_version: 'fake-dialer.v1',
              scenario_id: 'fake-dialer-happy-path',
              store: window.__fakeDialer?.store || null
            })
            """
        )
