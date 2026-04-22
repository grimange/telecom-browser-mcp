from __future__ import annotations

from typing import Any

from telecom_browser_mcp.adapters.apntalk_contract import (
    APNTALK_CONTRACT_VERSION,
    get_apntalk_surface_contract,
)
from telecom_browser_mcp.adapters.base import AdapterBase, AdapterOperationResult
from telecom_browser_mcp.models.session import AdapterCapabilities, TelecomStatus


class APNTalkAdapter(AdapterBase):
    adapter_id = "apntalk"
    adapter_name = "APNTalk"
    adapter_version = "0.1"
    contract_version = APNTALK_CONTRACT_VERSION
    scenario_id = "apntalk-modernization-baseline"
    support_status = "login_ui_only"
    capabilities = AdapterCapabilities(
        supports_login=True,
        supports_registration_detection=False,
        supports_incoming_call_detection=False,
        supports_answer_action=False,
        supports_hangup_action=False,
        supports_webrtc_summary=True,
    )

    _EMAIL_SELECTORS = (
        "input[type='email']",
        "input[name='email']",
        "input[autocomplete='username']",
        "input[placeholder*='Email' i]",
        "input[id*='email' i]",
    )
    _PASSWORD_SELECTORS = (
        "input[type='password']",
        "input[name='password']",
        "input[autocomplete='current-password']",
        "input[placeholder*='Password' i]",
        "input[id*='password' i]",
    )
    _SUBMIT_SELECTORS = (
        "button[type='submit']",
        "input[type='submit']",
        "button:has-text('Sign In')",
        "button:has-text('Log In')",
        "button:has-text('Login')",
    )

    @staticmethod
    async def _find_first_visible(page: Any, selectors: tuple[str, ...]) -> tuple[Any | None, str | None]:
        for selector in selectors:
            locator = page.locator(selector)
            try:
                if await locator.count() == 0:
                    continue
                if await locator.first.is_visible():
                    return locator.first, selector
            except Exception:
                continue
        return None, None

    @staticmethod
    def _credential_value(credentials: dict[str, Any], *keys: str) -> str | None:
        for key in keys:
            value = credentials.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    @staticmethod
    async def _extract_login_error(page: Any) -> str | None:
        try:
            payload = await page.evaluate(
                """
                () => {
                  const nodes = Array.from(
                    document.querySelectorAll('[role="alert"], .alert, .error, .errors, [data-testid*="error"]')
                  );
                  for (const node of nodes) {
                    const text = (node.textContent || '').trim();
                    if (text) {
                      return text;
                    }
                  }
                  return null;
                }
                """
            )
        except Exception:
            return None
        return payload if isinstance(payload, str) and payload.strip() else None

    @staticmethod
    async def _post_login_probe(page: Any) -> dict[str, Any]:
        try:
            payload = await page.evaluate(
                """
                () => {
                  const bodyText = (document.body?.innerText || '').replace(/\\s+/g, ' ').trim();
                  const title = (document.title || '').trim();
                  const path = (window.location.pathname || '').toLowerCase();
                  const href = window.location.href;
                  const hasPasswordField = !!document.querySelector("input[type='password']");
                  const hasEmailField = !!document.querySelector("input[type='email'], input[name='email'], input[autocomplete='username']");
                  const authText = /(dashboard|admin report|sign out|logout)/i.test(bodyText) || /(dashboard|admin report)/i.test(title);
                  const awayFromLogin = !/\\/login(?:\\/|$)?/.test(path) && !/login/i.test(title);
                  return {
                    success: authText || (awayFromLogin && !hasPasswordField && !hasEmailField),
                    url: href,
                    title,
                    away_from_login: awayFromLogin,
                    auth_text: authText,
                    has_password_field: hasPasswordField
                  };
                }
                """
            )
        except Exception:
            return {"success": False}
        return payload if isinstance(payload, dict) else {"success": False}

    async def wait_for_ready(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, timeout_ms)
        contract = get_apntalk_surface_contract("wait_for_ready")
        return self._failure(
            "APNTalk selector contract is not implemented; refusing scaffold ready-state success",
            error_code="selector_contract_missing",
            classification="ui_drift",
            missing_requirements=contract.missing_requirements(),
        )

    async def login(
        self,
        status: TelecomStatus,
        page: Any,
        credentials: dict[str, Any],
        timeout_ms: int,
    ) -> AdapterOperationResult:
        if page is None:
            return self._failure(
                "page unavailable",
                error_code="runtime_probe_unavailable",
                classification="environment_limitation",
                retryable=True,
            )

        username = self._credential_value(
            credentials,
            "email",
            "username",
            "user",
            "login",
            "agent_email",
        )
        password = self._credential_value(
            credentials,
            "password",
            "pass",
            "agent_password",
        )
        if not username or not password:
            return self._failure(
                "APNTalk login requires visible-UI credentials with non-empty email/username and password",
                error_code="invalid_input",
                classification="adapter_contract_failure",
            )

        email_locator, email_selector = await self._find_first_visible(page, self._EMAIL_SELECTORS)
        password_locator, password_selector = await self._find_first_visible(page, self._PASSWORD_SELECTORS)
        submit_locator, submit_selector = await self._find_first_visible(page, self._SUBMIT_SELECTORS)

        missing_selectors: list[str] = []
        if email_locator is None:
            missing_selectors.append("email_input")
        if password_locator is None:
            missing_selectors.append("password_input")
        if submit_locator is None:
            missing_selectors.append("submit_button")
        if missing_selectors:
            return self._failure(
                "APNTalk login UI controls were not found as visible elements",
                error_code="selector_contract_missing",
                classification="ui_drift",
                retryable=True,
                missing_selectors=missing_selectors,
            )

        try:
            await email_locator.fill(username, timeout=timeout_ms)
            await password_locator.fill(password, timeout=timeout_ms)
            await submit_locator.click(timeout=timeout_ms)
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            except Exception:
                pass
            await page.wait_for_function(
                """
                () => {
                  const bodyText = (document.body?.innerText || '').replace(/\\s+/g, ' ').trim();
                  const title = (document.title || '').trim();
                  const path = (window.location.pathname || '').toLowerCase();
                  const hasPasswordField = !!document.querySelector("input[type='password']");
                  const hasEmailField = !!document.querySelector("input[type='email'], input[name='email'], input[autocomplete='username']");
                  const authText = /(dashboard|admin report|sign out|logout)/i.test(bodyText) || /(dashboard|admin report)/i.test(title);
                  const awayFromLogin = !/\\/login(?:\\/|$)?/.test(path) && !/login/i.test(title);
                  return authText || (awayFromLogin && !hasPasswordField && !hasEmailField);
                }
                """,
                timeout=timeout_ms,
            )
        except Exception:
            error_text = await self._extract_login_error(page)
            if error_text:
                return self._failure(
                    f"APNTalk login form reported an error: {error_text}",
                    error_code="state_divergence",
                    classification="state_divergence",
                    retryable=True,
                )
            probe = await self._post_login_probe(page)
            return self._failure(
                "APNTalk login submit did not reach an authenticated post-login page",
                error_code="state_divergence",
                classification="state_divergence",
                retryable=True,
                post_login_probe=probe,
            )

        probe = await self._post_login_probe(page)
        if not probe.get("success"):
            return self._failure(
                "APNTalk login submit completed but authenticated UI was not confirmed",
                error_code="state_divergence",
                classification="state_divergence",
                retryable=True,
                post_login_probe=probe,
            )

        status.login_complete = True
        return self._success(
            "APNTalk login completed via visible UI",
            login_complete=True,
            landing_url=probe.get("url"),
            landing_title=probe.get("title"),
            selectors_used={
                "email": email_selector,
                "password": password_selector,
                "submit": submit_selector,
            },
        )

    async def wait_for_registration(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, timeout_ms)
        contract = get_apntalk_surface_contract("wait_for_registration")
        return self._failure(
            "APNTalk registration runtime probe is not implemented",
            error_code="runtime_probe_unavailable",
            classification="adapter_contract_failure",
            missing_requirements=contract.missing_requirements(),
        )

    async def wait_for_incoming_call(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, timeout_ms)
        contract = get_apntalk_surface_contract("wait_for_incoming_call")
        return self._failure(
            "APNTalk incoming-call runtime probe is not implemented",
            error_code="runtime_probe_unavailable",
            classification="adapter_contract_failure",
            missing_requirements=contract.missing_requirements(),
        )

    async def answer_call(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, timeout_ms)
        contract = get_apntalk_surface_contract("answer_call")
        return self._failure(
            "APNTalk answer action contract is not implemented",
            error_code="adapter_contract_unimplemented",
            classification="adapter_contract_failure",
            missing_requirements=contract.missing_requirements(),
        )

    async def hangup_call(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, timeout_ms)
        contract = get_apntalk_surface_contract("hangup_call")
        return self._failure(
            "APNTalk hangup action contract is not implemented",
            error_code="adapter_contract_unimplemented",
            classification="adapter_contract_failure",
            missing_requirements=contract.missing_requirements(),
        )

    async def registration_snapshot(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        _ = (status, page)
        contract = get_apntalk_surface_contract("get_registration_status")
        return {
            "available": False,
            "registration_state": status.registration_state,
            "reason": "APNTalk registration snapshot probe is not implemented",
            "reason_code": "runtime_probe_unavailable",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
            "missing_requirements": contract.missing_requirements(),
        }

    async def store_snapshot(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        _ = (status, page)
        contract = get_apntalk_surface_contract("get_store_snapshot")
        return {
            "available": False,
            "reason": "APNTalk store snapshot probe is not implemented",
            "reason_code": "runtime_probe_unavailable",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
            "missing_requirements": contract.missing_requirements(),
        }

    async def peer_connection_summary(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        _ = (status, page)
        contract = get_apntalk_surface_contract("get_peer_connection_summary")
        return {
            "available": False,
            "reason": "APNTalk runtime object path not configured; add verified inspector path in adapter hardening",
            "reason_code": "runtime_probe_unavailable",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
            "missing_requirements": contract.missing_requirements(),
        }
